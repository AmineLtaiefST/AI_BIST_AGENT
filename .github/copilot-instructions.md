# STM32 BIST Agent — GitHub Copilot Instructions

Modified by Amine LTAIEF.

Behavioral guidelines for GitHub Copilot when working on STM32 embedded firmware, specifically for BIST (Built-In Self-Test) and embedded diagnostics. Extends the Karpathy base guidelines.

**Tradeoff:** These guidelines bias toward safety and correctness over speed. For safety-critical code, apply full rigor.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- If the exact STM32 family is not specified, ask before writing register-level or clock/IRQ/DMA code.
- For internal or unpublished STM32 products, locate or ask for the internal product document and product driver library before selecting ADC, DAC, timer, DMA, trigger, or analog routing details.
- If the BIST architecture (POST/PEST/on-demand, safety level, fault reaction) is not described, ask before writing test logic.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- Do not add HAL error callbacks, retry loops, or fallback paths unless explicitly requested.
- Do not generate CubeMX-style boilerplate unless the project already uses it.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

Never modify without explicit request:
- Startup files, linker scripts, clock configuration, watchdog sequences
- MPU/cache setup, option bytes, IRQ priority tables
- Low-power entry/exit sequences, fault handlers
- Reset cause analysis, BIST result tables, safety state machines

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

For BIST tasks, success criteria must include:
- Test is deterministic and bounded in execution time.
- BIST execution placement is verified: code runs from RAM at base address `0x20000000`.
- No dynamic memory allocation is used; memory is static or stack-based with bounded usage.
- Detected fault is reported — never silently ignored, auto-cleared, or retried without specification.
- Safety assumptions are written explicitly in code or comments.
- If validation was done only in simulation, state that explicitly.

For multi-step tasks, state a brief plan:
```
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

## 5. STM32 Platform Rules

- Never invent register names, bitfield values, reset states, peripheral instance names, trigger routes, DMA mappings, or init sequences.
- For published products, reference the correct RM/DS for the target family. For internal or unpublished products, treat the internal product document and project driver library as the source of truth.
- Use the product driver library already present in the project. Do not bypass it with HAL, LL, or raw register access unless the project policy explicitly allows that layer for the module.
- Never mix HAL, LL, and raw register access within the same module without explicit justification.
- All BIST code must execute from RAM at base address `0x20000000`; if linker/startup/section placement support is missing, ask before modifying those files.
- Do not use dynamic memory allocation (`malloc`, `calloc`, `realloc`, `free`, `new`, `delete`) in BIST code.
- No blocking code, heap allocation, or complex logic inside ISRs.
- Every change to DMA, IRQ, clock, or Flash must document side effects.
- Always check peripheral clock enable before accessing registers.
- Explain every CMSIS intrinsic used (`__disable_irq`, `__DSB`, `__ISB`, `__DMB`).

## 6. BIST / Diagnostics Rules

- Every BIST must be deterministic, bounded in time, and diagnosable.
- Every BIST must execute from RAM at base address `0x20000000`; never assume Flash execution is acceptable.
- BIST code must not use dynamic memory allocation; use static storage or bounded stack usage only.
- Separate POST, PEST, and on-demand test execution paths. Do not merge them.
- Intrusive tests must document: resource locked, duration upper bound, system exclusions, recovery procedure.
- Never mask, auto-clear, or silently retry a detected fault unless that behavior is explicitly specified.
- Any change to RAM test, Flash CRC/ECC, CPU test, clock monitor, watchdog interaction, or reset cause analysis must state the safety impact.
- Safety assumptions must be written explicitly — never left implicit.

---

**These guidelines are working if:** the agent asks before touching safety-critical code, implements bounded and diagnosable BIST logic, and every change comes with explicit assumptions and verification criteria.
