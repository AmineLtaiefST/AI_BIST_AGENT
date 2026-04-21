# Examples — STM32 BIST Agent Guidelines

Modified by Amine LTAIEF.

Real-world firmware examples demonstrating the six rules. Each example shows what AI agents commonly do wrong on STM32/BIST code and how to fix it.

---

## 1. Think Before Coding

### Example: Ambiguous BIST request

**User Request:** "Add a RAM BIST"

**❌ What agents do (wrong assumptions)**

```c
/* RAM BIST — agent picks March-C, runs at startup, no timing bound, no fault report */
void RAM_BIST(void) {
    uint32_t *p = (uint32_t *)0x20000000;
    for (int i = 0; i < 0x20000; i++) {
        p[i] = 0xAAAAAAAA;
        if (p[i] != 0xAAAAAAAA) { while(1); }  // silent hang
        p[i] = 0x55555555;
        if (p[i] != 0x55555555) { while(1); }
    }
}
```

**Problems:**
- Assumed test algorithm (March-C) without asking
- Assumed memory range and size without checking linker
- Unbounded execution time — no maximum stated
- Fault reaction is a silent hang, not a diagnosable report
- Overwrites live data — no save/restore, no exclusion zone defined

**✅ What should happen (surface assumptions)**

```
Before implementing, I need to clarify:

1. Algorithm: March-C, March-X, Checkerboard, or other? (coverage vs time tradeoff)
2. Scope: full SRAM or only a dedicated test section? (linker symbol or address range?)
3. Phase: POST (before .data/.bss init) or PEST (periodic, with exclusions)?
4. Timing constraint: maximum allowed execution time?
5. Fault reaction: which reporting mechanism? (BIST_ResultTable[], SafeState_Enter(), reset?)
6. Intrusive: is it acceptable to temporarily corrupt SRAM during the test?

Simplest safe starting point: a bounded checkerboard test on a dedicated .bist_ram section,
reporting to BIST_ResultTable[BIST_ID_RAM].
```

---

## 2. Simplicity First

### Example: Over-engineered clock monitor BIST

**User Request:** "Add a clock frequency check in the BIST"

**❌ What agents do (overengineered)**

```c
typedef struct {
    uint32_t expectedFreq;
    uint32_t tolerancePpm;
    uint32_t measurementWindowMs;
    bool     autoCorrect;
    bool     logEnabled;
    void (*onFaultCallback)(uint32_t measured, uint32_t expected);
} ClockBIST_Config_t;

ClockBIST_Result_t ClockBIST_Run(const ClockBIST_Config_t *cfg) {
    // 80 lines of generic framework nobody asked for
}
```

**✅ What should happen (just what was asked)**

```c
/* Clock monitor BIST — check HSE against LSI using TIM14 input capture.
   Max execution: 2 ms. Reports to BIST_ResultTable[BIST_ID_CLK]. */
BIST_Status_t ClockBIST_Run(void) {
    uint32_t count = TIM14_MeasureHSECycles(LSI_WINDOW_MS);
    if ((count < CLK_COUNT_MIN) || (count > CLK_COUNT_MAX)) {
        BIST_ResultTable[BIST_ID_CLK] = BIST_FAIL;
        return BIST_FAIL;
    }
    BIST_ResultTable[BIST_ID_CLK] = BIST_PASS;
    return BIST_PASS;
}
```

Add callbacks and configurability only when a second use case actually requires it.

---

## 3. Surgical Changes

### Example: Drive-by startup modification

**User Request:** "Fix the Flash wait states in the clock init"

**❌ What agents do (too much)**

```diff
  void SystemClock_Config(void) {
-     /* USER CODE BEGIN SystemClock_Config 0 */
-     /* USER CODE END SystemClock_Config 0 */
+     /* Configure flash latency */
      RCC_OscInitTypeDef RCC_OscInitStruct = {0};
      RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

-     __HAL_RCC_PWR_CLK_ENABLE();
-     __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
+     /* Set voltage scale before PLL */
+     __HAL_RCC_PWR_CLK_ENABLE();
+     __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
+     while (!__HAL_PWR_GET_FLAG(PWR_FLAG_VOSRDY)) {}  // added: wait for VOS ready

      RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
-     RCC_OscInitStruct.HSEState = RCC_HSE_ON;
+     RCC_OscInitStruct.HSEState       = RCC_HSE_BYPASS;  // changed silently
```

**Problems:**
- Changed `HSE_ON` to `HSE_BYPASS` silently — completely wrong on a crystal board
- Added VOS ready wait (unrequested improvement)
- Reformatted adjacent code

**✅ What should happen (only the fix)**

```diff
  /* Configure the main internal regulator output voltage */
- if (HAL_FLASH_SetLatency(FLASH_LATENCY_2) != HAL_OK) { Error_Handler(); }
+ if (HAL_FLASH_SetLatency(FLASH_LATENCY_4) != HAL_OK) { Error_Handler(); }
```

One line changed. Nothing else touched.

---

## 4. Goal-Driven Execution

### Example: Watchdog interaction in BIST

**User Request:** "Make sure the BIST doesn't trigger the watchdog"

**❌ What agents do (weak criteria)**

```c
// Refresh watchdog during BIST
HAL_IWDG_Refresh(&hiwdg);
```

**Problems:**
- No plan stated
- No timing analysis — is the BIST actually within the IWDG window?
- No consideration of WWDG window if used alongside IWDG
- No documentation of where refresh is placed and why

**✅ What should happen (goal-driven plan)**

```
Plan:
1. Measure BIST worst-case execution time → verify: timing on SWO trace or GPIO toggle
2. Compare against IWDG reload value (RLR) and prescaler → verify: BIST_max < IWDG_window
3. If BIST_max > IWDG_window: define a single explicit refresh point mid-BIST
   → verify: no spurious reset under nominal load + fault injection
4. If WWDG also active: verify refresh falls within WWDG window too
   → verify: no spurious reset, no missed window reset

Assumption: IWDG reload = 4095, prescaler = 32 → window = 4.096 s.
RAM BIST worst-case = 800 µs → no refresh needed.
Clock BIST worst-case = 2 ms → no refresh needed.
Flash CRC worst-case = 120 ms → one refresh at midpoint, documented in BIST_FlashCRC_Run().
```

---

## 5. STM32 Platform Rules

### Example: Invented register access

**User Request:** "Enable the CRC peripheral clock on STM32G474"

**❌ What agents do (invent bitfields)**

```c
RCC->AHB1ENR |= RCC_AHB1ENR_CRCEN;   // wrong family, this is STM32F4 layout
```

**✅ What should happen (reference correct RM)**

```c
/* STM32G474 RM0440 Rev 5 §7.4.17: RCC_AHB1ENR bit 12 = CRCEN */
RCC->AHB1ENR |= RCC_AHB1ENR_CRCEN;   // correct — same bit, verified in CMSIS header
```

Or, using HAL:
```c
__HAL_RCC_CRC_CLK_ENABLE();   // preferred — family-portable, verified by HAL
```

If unsure which family: **ask before writing any register access.**

---

## 6. BIST / Diagnostics Rules

### Example: Silent fault masking

**User Request:** "Handle the case where the Flash CRC BIST fails but the system should continue"

**❌ What agents do (silent mask)**

```c
if (FlashCRC_BIST() != BIST_PASS) {
    flash_bist_retry_count++;
    if (flash_bist_retry_count < 3) return;  // silently swallow the fault
}
```

**Problems:**
- Fault is retried and swallowed without specification
- `flash_bist_retry_count` is never reset — state machine is broken
- No diagnostic report — fault is invisible to any supervisor
- "Continue" and "retry silently" are not the same thing

**✅ What should happen (explicit, diagnosable)**

```
This requires architectural clarification before coding:

1. "Continue" — does it mean degrade gracefully (restricted mode) or full operation?
2. Is retry permitted by the safety architecture? If yes: how many times, with what delay,
   and what happens after N failures?
3. Who is the fault consumer? (BIST_ResultTable, fault log, safe state machine, supervisor task)

Proposed implementation after clarification:

BIST_Status_t FlashCRC_BIST_WithPolicy(void) {
    BIST_Status_t result = FlashCRC_BIST_Run();
    BIST_ResultTable[BIST_ID_FLASH_CRC] = result;   // always report, never hide

    if (result != BIST_PASS) {
        FaultLog_Record(FAULT_ID_FLASH_CRC, result);
        /* Degraded mode entry — defined by architecture, not invented here */
        System_EnterDegradedMode(DEGRADED_REASON_FLASH_CRC);
    }
    return result;
}
```

Safety assumption (explicit): Flash CRC failure does not corrupt RAM or execution flow;
degraded mode is safe to enter from any BIST phase.
