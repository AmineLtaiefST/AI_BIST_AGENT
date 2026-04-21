# Using AI_BIST_AGENT with VS Code

Modified by Amine LTAIEF.

This project includes a native **GitHub Copilot instructions** file so the STM32 BIST behavioral guidelines apply automatically when you work here in VS Code.

## In this repository

1. Open the folder in VS Code with GitHub Copilot enabled.
2. The file [`.github/copilot-instructions.md`](.github/copilot-instructions.md) is committed in the repository. GitHub Copilot applies it automatically to all chat and agent requests in this workspace.
3. [`CLAUDE.md`](CLAUDE.md) is also supported by VS Code for compatibility with Claude-based tools.
4. In VS Code, inspect loaded instructions from the Chat view via **Configure Chat** → Instructions tab, or check the References section of any chat response.

## Use the same guidelines in another STM32 project

**VS Code / GitHub Copilot (recommended):**
```bash
mkdir -p .github
curl -o .github/copilot-instructions.md https://raw.githubusercontent.com/AmineLtaiefST/AI_BIST_AGENT/main/.github/copilot-instructions.md
```

**Add project-specific context on top:**
```markdown
## Project-Specific Guidelines

- Target: STM32H743 rev Y, GCC 12.3, STM32CubeH7 v1.11
- HAL only — no LL or direct register access except in startup and fault handlers
- BIST framework: BIST_Run() dispatcher, results in BIST_ResultTable[]
- Safety level: SIL 2 (IEC 61508)
- Fault reaction: all BIST failures trigger SafeState_Enter()
```

## Claude Code vs VS Code vs Cursor

- **Claude Code:** Use [`CLAUDE.md`](CLAUDE.md) per project, or install the skill from [`skills/stm32-bist/SKILL.md`](skills/stm32-bist/SKILL.md).
- **VS Code:** Use the committed [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — this is the native Copilot format.
- **Cursor:** Use the committed [`.cursor/rules/stm32-bist-guidelines.mdc`](.cursor/rules/stm32-bist-guidelines.mdc) as described in [`CURSOR.md`](CURSOR.md).

## For contributors

When you change the rules, keep [`CLAUDE.md`](CLAUDE.md), [`.github/copilot-instructions.md`](.github/copilot-instructions.md), [`.cursor/rules/stm32-bist-guidelines.mdc`](.cursor/rules/stm32-bist-guidelines.mdc), and [`skills/stm32-bist/SKILL.md`](skills/stm32-bist/SKILL.md) in sync.
