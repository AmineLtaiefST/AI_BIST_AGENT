# Using AI_BIST_AGENT with VS Code

Modified by Amine LTAIEF.

This project includes a native **GitHub Copilot instructions** file so the STM32 BIST behavioral guidelines apply automatically when you work here in VS Code.

## In this repository

1. Open the folder in VS Code with GitHub Copilot enabled.
2. The file [`.github/copilot-instructions.md`](.github/copilot-instructions.md) is committed in the repository. GitHub Copilot applies it automatically to all chat and agent requests in this workspace.
3. The custom agent [`.github/agents/stm32-bist-orchestrator.agent.md`](.github/agents/stm32-bist-orchestrator.agent.md) is committed in the repository for end-to-end BIST pipeline orchestration.
4. [`CLAUDE.md`](CLAUDE.md) is also supported by VS Code for compatibility with Claude-based tools.
5. In VS Code, inspect loaded instructions from the Chat view via **Configure Chat** → Instructions tab, or check the References section of any chat response.

## Use the BIST orchestrator agent

In VS Code Copilot Chat, select **STM32 BIST Orchestrator** from the agent picker when you want to run a complete BIST pipeline workflow.

Provide the agent with:

- pipeline name or path, for example [`Pepline_ADC_SINGLE_AC_BIST.md`](Pepline_ADC_SINGLE_AC_BIST.md)
- exact STM32 product name, family, part number or internal product identifier
- product publication status: published, internal, or unpublished
- ADC IP name, ADC instance, and ADC channel under test, when running an ADC BIST
- target firmware project path
- internal product document path, version, or excerpt
- public RM/DS reference for published products, or permission to search the web for official public documentation
- product driver library path and allowed APIs
- BIST phase: POST, PEST, or on-demand
- BIST reporting mechanism and fault reaction
- validation target: unit test, simulation, build, or hardware run

The orchestrator will collect missing context, generate code/tests/docs only when enough information is available, run available verification, and produce a result report.

## Use the same guidelines in another STM32 project

**VS Code / GitHub Copilot (recommended):**
```bash
mkdir -p .github
curl -o .github/copilot-instructions.md https://raw.githubusercontent.com/AmineLtaiefST/AI_BIST_AGENT/main/.github/copilot-instructions.md
mkdir -p .github/agents
curl -o .github/agents/stm32-bist-orchestrator.agent.md https://raw.githubusercontent.com/AmineLtaiefST/AI_BIST_AGENT/main/.github/agents/stm32-bist-orchestrator.agent.md
```

**Add project-specific context on top:**
```markdown
## Project-Specific Guidelines

- Target: STM32H743 rev Y, GCC 12.3, STM32CubeH7 v1.11
- Product status: published | internal | unpublished
- ADC under test: ADC IP/name/instance/channel, when applicable
- Product source of truth: internal product document and project driver library
- HAL only — no LL or direct register access except in startup and fault handlers
- BIST framework: BIST_Run() dispatcher, results in BIST_ResultTable[]
- BIST execution: all BIST code runs from RAM at base address 0x20000000
- Memory policy: no dynamic allocation in BIST code
- Safety level: SIL 2 (IEC 61508)
- Fault reaction: all BIST failures trigger SafeState_Enter()
```

## Claude Code vs VS Code vs Cursor

- **Claude Code:** Use [`CLAUDE.md`](CLAUDE.md) per project, or install the skill from [`skills/stm32-bist/SKILL.md`](skills/stm32-bist/SKILL.md).
- **VS Code:** Use the committed [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — this is the native Copilot format.
- **Cursor:** Use the committed [`.cursor/rules/stm32-bist-guidelines.mdc`](.cursor/rules/stm32-bist-guidelines.mdc) as described in [`CURSOR.md`](CURSOR.md).

## For contributors

When you change the rules, keep [`CLAUDE.md`](CLAUDE.md), [`.github/copilot-instructions.md`](.github/copilot-instructions.md), [`.cursor/rules/stm32-bist-guidelines.mdc`](.cursor/rules/stm32-bist-guidelines.mdc), and [`skills/stm32-bist/SKILL.md`](skills/stm32-bist/SKILL.md) in sync. When you change orchestration behavior, update [`.github/agents/stm32-bist-orchestrator.agent.md`](.github/agents/stm32-bist-orchestrator.agent.md).
