# CLAUDE.md — STM32 BIST Agent Guidelines

Modified by Amine LTAIEF.

Behavioral guidelines for AI coding agents working on STM32 embedded firmware, specifically for BIST (Built-In Self-Test) and embedded diagnostics development. Extends the [Karpathy base guidelines](https://github.com/forrestchang/andrej-karpathy-skills).

**Tradeoff:** These guidelines bias toward safety and correctness over speed. For trivial tasks, use judgment. For anything safety-critical, apply full rigor.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

**STM32-specific:**
- If the exact STM32 family (H7, G4, U5, H5, WB, ...) is not specified, ask before writing any register-level or clock/IRQ/DMA code.
- For internal or unpublished STM32 products, locate or ask for the internal product document and product driver library before selecting ADC, DAC, timer, DMA, trigger, or analog routing details.
- If the HAL/LL/register access policy is not stated, ask before mixing layers.
- If the BIST architecture (POST, PEST, on-demand, safety level, fault reaction) is not described, ask before writing test logic.

---

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

**STM32-specific:**
- Do not add HAL error callbacks, retry loops, or fallback paths unless explicitly requested.
- Do not generate CubeMX-style boilerplate (comment blocks, USER CODE BEGIN/END sections) unless the project already uses them.
- Do not add logging, trace, or assert macros unless the project already uses a defined mechanism.

---

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

**STM32 hard boundaries — never modify without explicit request:**
- Startup files (`startup_*.s`, `system_*.c`)
- Linker scripts (`*.ld`, `*.icf`, `*.sct`)
- Clock configuration (`SystemClock_Config`, PLL/HSE/HSI setup)
- Watchdog initialization and refresh sequences (IWDG, WWDG)
- MPU / cache configuration
- Option bytes
- IRQ priority tables and `NVIC_SetPriority` calls
- Low-power entry/exit sequences
- Fault handlers (`HardFault_Handler`, `MemManage_Handler`, etc.)
- Reset cause analysis code
- BIST result tables or safety state machines

---

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add a RAM BIST" → "Implement March-C algorithm, bounded to N ms, report result to BIST_ResultTable[], verify on target with fault injection"
- "Fix clock monitor BIST" → "Write a test reproducing the failure, fix it, verify timing on oscilloscope or SWO trace"
- "Add watchdog interaction to BIST" → "Document window, refresh point, exclusion zones; verify no spurious reset under nominal load"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

**BIST-specific success criteria:**
- Test is deterministic: same input → same result every time.
- Test is bounded: maximum execution time is stated and measurable.
- Execution placement is verified: BIST code runs from RAM at base address `0x20000000`.
- Memory use is static or bounded stack-based only; dynamic allocation is forbidden.
- Fault is diagnosable: detected fault is reported (not silently ignored, not auto-cleared, not retried without specification).
- Safety assumptions are explicit: any assumption about hardware state, interrupt masking, or resource exclusivity is written in code or comments.
- Validation is on-target: if validation was done only in simulation, state that explicitly.

---

## 5. STM32 Platform Rules

**Never guess. Never invent. Reference the source of truth.**

- Never invent register names, bitfield names, reset values, peripheral instance names, trigger routes, DMA mappings, or initialization sequences.
- For published products, reference the correct Reference Manual (RM) and Datasheet (DS) for the target family. For internal or unpublished products, treat the internal product document and project driver library as the source of truth.
- Use the product driver library already present in the project. Do not bypass it with HAL, LL, or raw register access unless the project policy explicitly allows that layer for the module.
- Never mix HAL, LL, and raw register access within the same module without an explicit architectural justification.
- All BIST code must execute from RAM at base address `0x20000000`; if linker/startup/section placement support is missing, ask before modifying those files.
- Do not use dynamic memory allocation (`malloc`, `calloc`, `realloc`, `free`, `new`, `delete`) in BIST code.
- Every change to DMA, IRQ, clock, Flash, or low-power must document side effects on other subsystems.
- No blocking code, heap allocation (`malloc`/`new`), or complex logic inside ISRs.
- Always check if a peripheral clock is enabled before accessing its registers.
- If CMSIS intrinsics are used (`__disable_irq`, `__DSB`, `__ISB`, `__DMB`), explain why each one is needed.

---

## 6. BIST / Diagnostics Rules

**Test logic is safety logic. Treat it accordingly.**

- **Deterministic:** A BIST must produce the same result for the same hardware state. Non-determinism is a defect.
- **Bounded:** Every BIST must have a stated maximum execution time. Unbounded loops are not acceptable.
- **RAM-executed:** Every BIST must execute from RAM at base address `0x20000000`; Flash execution is not acceptable unless the architecture is explicitly revised.
- **No dynamic allocation:** BIST code must not use `malloc`, `calloc`, `realloc`, `free`, `new`, or `delete`; use static storage or bounded stack usage only.
- **Diagnosable:** Every detected fault must be reported through the defined reporting mechanism. Never mask, auto-clear, or silently retry a fault unless that behavior is explicitly specified.
- **Typed:** Clearly separate POST (power-on self-test), PEST (periodic self-test), and on-demand test. Do not merge their execution paths.
- **Intrusive tests:** If a test temporarily monopolizes a resource or modifies hardware state, document: resource locked, duration upper bound, system exclusions, and recovery/restore procedure.
- **Safety assumptions:** Any assumption about interrupt masking, resource exclusivity, safe system state, or external conditions must be written explicitly — never left implicit.
- **Modification impact:** Any change to RAM test, Flash CRC/ECC check, CPU register test, clock monitor, watchdog interaction, or reset cause analysis must state the safety impact and reference the relevant safety requirement.

---

**These guidelines are working if:** the agent asks before touching safety-critical code, proposes bounded and diagnosable test implementations, and every BIST change comes with explicit assumptions and verification criteria.
