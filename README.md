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

---

## The Four Layers

| Layer | File | Scope |
|-------|------|-------|
| Agent behavior | `CLAUDE.md` | All tools (Claude, Cursor, VS Code) |
| VS Code / GitHub Copilot | `.github/copilot-instructions.md` | VS Code Copilot Chat + Agents |
| Cursor | `.cursor/rules/stm32-bist-guidelines.mdc` | Cursor editor |
| Reusable skill | `skills/stm32-bist/SKILL.md` | Claude Code plugin / skill |

---

## Rules Overview

### Agent Behavior (Karpathy base)

1. **Think Before Coding** — Surface assumptions. Ask before guessing.
2. **Simplicity First** — Minimum code. No speculative features.
3. **Surgical Changes** — Touch only what the request requires.
4. **Goal-Driven Execution** — Define verifiable success criteria upfront.

### STM32 Platform Hard Rules

- Never modify startup, linker, clock tree, watchdog, MPU/cache, option bytes, IRQ priorities, or low-power sequences without an explicit request and justification.
- Never invent register names, bitfield values, reset states, or initialization sequences. Always reference the correct RM/DS for the target family.
- Never mix HAL, LL, and raw register access within the same module without explicit architectural justification.
- No blocking code, heap allocation, or heavy logic inside ISRs.
- Every change to DMA, IRQ, clock, or Flash must document side effects.
- If the exact STM32 family (e.g., H7, G4, U5, H5) is not specified, ask before writing any register-level code.

### BIST / Diagnostics Rules

- Every BIST must be **deterministic**, **bounded in execution time**, and **diagnosable** (fault must be observable and reported, never silently ignored or retried).
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
- HAL only, no LL or direct register access except in startup and fault handlers
- BIST framework: custom BIST_Run() dispatcher, results in BIST_ResultTable[]
- Safety level: SIL 2 (IEC 61508)
- Fault reaction: all BIST failures trigger system safe state via SafeState_Enter()
```

---

## Tradeoff

These guidelines bias toward **safety and correctness over speed**. For trivial tasks (renaming a variable, fixing a comment), use judgment. For anything touching clocks, IRQ, startup, BIST logic, or safety paths — apply full rigor.

---

## License

MIT
