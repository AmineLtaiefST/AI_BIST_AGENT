---
name: stm32-bist-guidelines
description: Behavioral guidelines for STM32 firmware development with a focus on BIST (Built-In Self-Test) and embedded diagnostics. Use when writing, reviewing, or refactoring STM32 C/C++ firmware involving POST, PEST, on-demand tests, clock monitors, RAM/Flash tests, or safety-critical diagnostics.
license: MIT
---

# STM32 BIST Agent Guidelines

Modified by Amine LTAIEF.

Behavioral guidelines for AI coding agents working on STM32 embedded firmware, specifically BIST and embedded diagnostics. Extends the Karpathy base guidelines.

**Tradeoff:** These guidelines bias toward safety and correctness over speed. For safety-critical code, apply full rigor.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- If the exact STM32 family is not specified, ask before writing register-level or clock/IRQ/DMA code.
- Always ask for the exact STM32 product name, family, part number or internal product identifier, and whether the product is published or internal/unpublished before choosing documentation sources or hardware details.
- For internal or unpublished STM32 products, locate or ask for the internal product document and product driver library before selecting ADC, DAC, timer, DMA, trigger, or analog routing details.
- For ADC BISTs, always ask for the ADC IP name, ADC instance, and ADC channel under test before selecting drivers, triggers, DMA, or analog routing.
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

## 6. BIST / Diagnostics Rules

- **Deterministic:** same input → same result every time. Non-determinism is a defect.
- **Bounded:** every BIST has a stated maximum execution time. Unbounded loops are not acceptable.
- **RAM-executed:** every BIST must execute from RAM at base address `0x20000000`; Flash execution is not acceptable unless the architecture is explicitly revised.
- **No dynamic allocation:** BIST code must not use `malloc`, `calloc`, `realloc`, `free`, `new`, or `delete`; use static storage or bounded stack usage only.
- **Diagnosable:** every detected fault is reported. Never mask, auto-clear, or silently retry without specification.
- **Typed:** POST, PEST, and on-demand paths are separate. Do not merge them.
- **Intrusive tests:** document resource locked, duration upper bound, system exclusions, recovery procedure.
- **Safety assumptions:** written explicitly in code or comments — never implicit.
- **Modification impact:** any change to RAM test, Flash CRC/ECC, CPU test, clock monitor, watchdog, or reset cause must state the safety impact.

---

**These guidelines are working if:** the agent asks before touching safety-critical code, proposes bounded and diagnosable BIST implementations, and every change comes with explicit assumptions and verification criteria.
