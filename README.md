# BIST_AGENT

Modified by Amine LTAIEF.

AI agent behavioral guidelines and coding rules for STM32 firmware development, focused on Built-In Self-Test (BIST) and embedded diagnostics.

Derived from [Karpathy-inspired agent guidelines](https://github.com/forrestchang/andrej-karpathy-skills) and extended with STM32 platform rules and BIST-specific constraints.

---

## Purpose

This repository provides instruction files for GitHub Copilot (VS Code), Cursor, and Claude Code so that AI coding agents behave correctly when working on STM32 firmware projects involving:

- Power-On Self-Test (POST)
- Periodic Self-Test (PEST)
- On-Demand Self-Test
- Safety-critical diagnostics (IEC 61508, ISO 26262 context)
- Embedded hardware diagnostics (RAM, Flash, CPU, Clock, Watchdog, Peripherals)
- BIST execution from RAM at base address `0x20000000`
- Internal or unpublished STM32 products where the product document and driver library are the source of truth

---

## The Five Layers

| Layer | File | Scope |
|-------|------|-------|
| Agent behavior | `CLAUDE.md` | All tools (Claude, Cursor, VS Code) |
| VS Code / GitHub Copilot | `.github/copilot-instructions.md` | VS Code Copilot Chat + Agents |
| VS Code custom agent | `.github/agents/stm32-bist-orchestrator.agent.md` | End-to-end BIST pipeline orchestration |
| Cursor | `.cursor/rules/stm32-bist-guidelines.mdc` | Cursor editor |
| Reusable skill | `skills/stm32-bist/SKILL.md` | Claude Code plugin / skill |

---

## BIST Pipelines

| Pipeline | Purpose |
|----------|---------|
| [`Pepline_ADC_SINGLE_AC_BIST.md`](Pepline_ADC_SINGLE_AC_BIST.md) | ADC dynamic performance BIST using DAC sine generation, synchronized ADC capture, DMA, CMSIS-DSP FFT, SNR, THD, SINAD, and ENOB. |

## Reference Patterns

| Pattern | Purpose |
|---------|---------|
| [`ADC_DYNAMIC_SOFTBIST_PATTERN.md`](ADC_DYNAMIC_SOFTBIST_PATTERN.md) | Lightweight extraction of the former ADC SoftBIST reference project: BIST flow, resources, SRAM/ATE result interface, DSP metrics, and generation guardrails. |

---

## Firmware Project Architecture

Concrete firmware BIST projects should be organized by product and by test under:

```text
fw_projects/<PRODUCT_ID>/<TEST_ID>/
```

See [`FW_PROJECT_ARCHITECTURE.md`](FW_PROJECT_ARCHITECTURE.md) for the canonical layout, naming rules, metadata template, and handling of project-specific firmware folders.

---

## BIST Orchestrator Agent

Use the workspace custom agent [`STM32 BIST Orchestrator`](.github/agents/stm32-bist-orchestrator.agent.md) when you want Copilot to drive a complete BIST workflow:

- select a pipeline document
- collect internal product documentation and product driver library context
- generate or modify firmware code
- add focused tests or validation assets
- update implementation documentation
- produce a BIST result report

The orchestrator must not implement hardware details until the selected pipeline, internal product document, driver APIs, BIST phase, reporting mechanism, fault reaction, and RAM execution mechanism are known.

At the start of a workflow, the orchestrator must always ask for the exact STM32 product name/family/part number or internal product identifier, plus whether the product is published or internal/unpublished. For ADC BIST workflows, it must also ask which ADC IP/name/instance/channel must be tested.

---

## Rules Overview

### Agent Behavior (Karpathy base)

1. **Think Before Coding** — Surface assumptions. Ask before guessing.
2. **Simplicity First** — Minimum code. No speculative features.
3. **Surgical Changes** — Touch only what the request requires.
4. **Goal-Driven Execution** — Define verifiable success criteria upfront.

### STM32 Platform Hard Rules

- Never modify startup, linker, clock tree, watchdog, MPU/cache, option bytes, IRQ priorities, or low-power sequences without an explicit request and justification.
- Never invent register names, bitfield values, reset states, peripheral instance names, trigger routes, DMA mappings, or initialization sequences.
- Always ask for the exact STM32 product name, family, part number or internal product identifier, and whether the product is published or internal/unpublished before choosing documentation sources or hardware details.
- For ADC BISTs, always ask for the ADC IP name, ADC instance, and ADC channel under test.
- For published products, reference the correct RM/DS for the target family. For internal or unpublished products, treat the internal product document and project driver library as the source of truth.
- Use the product driver library already present in the project. Do not bypass it with HAL, LL, or raw register access unless the project policy explicitly allows that layer for the module.
- Never mix HAL, LL, and raw register access within the same module without explicit architectural justification.
- All BIST code must execute from RAM at base address `0x20000000`; if linker/startup/section placement support is missing, ask before modifying those files.
- Do not use dynamic memory allocation (`malloc`, `calloc`, `realloc`, `free`, `new`, `delete`) in BIST code.
- No blocking code, heap allocation, or heavy logic inside ISRs.
- Every change to DMA, IRQ, clock, or Flash must document side effects.
- If the exact STM32 family (e.g., H7, G4, U5, H5) is not specified, ask before writing any register-level code.

### BIST / Diagnostics Rules

- Every BIST must be **deterministic**, **bounded in execution time**, and **diagnosable** (fault must be observable and reported, never silently ignored or retried).
- Every BIST must execute from RAM at base address `0x20000000`; Flash execution is not acceptable unless the architecture is explicitly revised.
- BIST code must not use dynamic memory allocation; use static storage or bounded stack usage only.
- Clearly separate POST, PEST, and on-demand test logic. Do not merge their execution paths.
- Intrusive tests (those that temporarily monopolize a resource or affect system state) must document: resource locked, duration upper bound, system exclusions, and recovery strategy.
- Never mask, auto-clear, or silently retry a detected fault unless that behavior is explicitly specified in the architecture.
- Any modification to RAM test, Flash CRC/ECC, CPU test, clock monitor, watchdog interaction, or reset cause analysis must state the safety impact.
- Safety assumptions must be written explicitly in code or comments — never left implicit.

---

## Install

### VS Code / GitHub Copilot

```bash
mkdir -p .github
curl -o .github/copilot-instructions.md https://raw.githubusercontent.com/AmineLtaiefST/BIST_AGENT/main/.github/copilot-instructions.md
mkdir -p .github/agents
curl -o .github/agents/stm32-bist-orchestrator.agent.md https://raw.githubusercontent.com/AmineLtaiefST/BIST_AGENT/main/.github/agents/stm32-bist-orchestrator.agent.md
```

### Cursor

```bash
mkdir -p .cursor/rules
curl -o .cursor/rules/stm32-bist-guidelines.mdc https://raw.githubusercontent.com/AmineLtaiefST/BIST_AGENT/main/.cursor/rules/stm32-bist-guidelines.mdc
```

### Claude Code / CLAUDE.md

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/AmineLtaiefST/BIST_AGENT/main/CLAUDE.md
```

---

## Customization

These rules are designed to be merged with project-specific instructions. Add project-level sections such as:

```markdown
## Project-Specific Guidelines

- Target: STM32H743 rev Y, GCC 12.3, STM32CubeH7 v1.11
- Product status: published | internal | unpublished
- ADC under test: ADC IP/name/instance/channel, when applicable
- Product source of truth: internal product document and project driver library
- HAL only, no LL or direct register access except in startup and fault handlers
- BIST framework: custom BIST_Run() dispatcher, results in BIST_ResultTable[]
- BIST execution: all BIST code runs from RAM at base address 0x20000000
- Memory policy: no dynamic allocation in BIST code
- Safety level: SIL 2 (IEC 61508)
- Fault reaction: all BIST failures trigger system safe state via SafeState_Enter()
```

---

## Tradeoff

These guidelines bias toward **safety and correctness over speed**. For trivial tasks (renaming a variable, fixing a comment), use judgment. For anything touching clocks, IRQ, startup, BIST logic, or safety paths — apply full rigor.

---

## License

MIT
