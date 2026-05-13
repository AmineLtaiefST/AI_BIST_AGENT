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

When information is missing, ask one question at a time by default. Summarize only the facts already proven by workspace evidence, then ask the single next highest-priority question and wait for the user's answer before asking the next one. Do not present a full open-question checklist unless the user explicitly asks for all open questions or batch mode. Do not re-ask facts already confirmed by README/resource maps, `.ioc`, generated metadata, validation notes, or prior user answers unless they conflict.

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- If the exact STM32 family is not specified, ask before writing register-level or clock/IRQ/DMA code.
- Always ask for the exact STM32 product name, family, part number or internal product identifier, and whether the product is published or internal/unpublished before choosing documentation sources or hardware details.
- For internal or unpublished STM32 products, locate or ask for the internal product document and product driver library before selecting ADC, DAC, timer, DMA, trigger, or analog routing details.
- For ADC BISTs, first inspect the existing product template/project, `.ioc`, product document, and driver library; then ask only for ADC/DAC/timer/DMA facts that are still missing or ambiguous.
- If the BIST architecture (POST/PEST/on-demand, safety level, fault reaction) is not described, ask before writing test logic.

### Existing Product Template Workflow

When a functional product template or generated firmware project already exists, use it as the starting point. Do not ask the user to create a new CubeMX project unless the template is missing, incomplete, inconsistent, or the user explicitly chooses regeneration.

If the template already contains `main.c`, do not ask to create another `main.c`. Locate the owner core's existing `Core/Src/main.c` and use the project's established integration points. If ADC/DAC/timer/DMA initialization is missing, treat it as missing resource knowledge first: extract what is known from the template, then ask the focused ADC/DAC/timer/DMA questions below. Do not describe this as a missing `main.c` problem and do not jump directly to CubeMX project creation.

For ADC BIST work on an existing template, the focused question order is:

1. ADC: ask or confirm ADC IP/name, ADC instance, channel, and mode: single-ended or differential. For differential mode, ask or confirm the second channel.
2. DAC: ask or confirm DAC instance/channel and how it is connected to the ADC path: internal route, external connection, shared pin, or product-specific analog routing.
3. Timer synchronization: prefer one common timer time base. Use two deterministic timer output-compare events/channels when supported: one for DAC update and one phase-shifted event for ADC conversion after DAC settling. If the timer or trigger route is unclear, ask.
4. DMA: inspect the product document, `.ioc`, generated source, DMAMUX/DMA mapping, and driver library before asking. Ask only when the DMA request/channel/stream choice is unclear or conflicting.
5. CubeMX: if a selected product template is functional, do not request CubeMX project creation. Only discuss CubeMX regeneration after the missing ADC/DAC/timer/DMA facts are identified and the existing template cannot be completed safely from its current evidence.

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
