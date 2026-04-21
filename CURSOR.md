# Using AI_BIST_AGENT with Cursor

Modified by Amine LTAIEF.

This project includes a committed **Cursor project rule** so the STM32 BIST behavioral guidelines apply automatically when you work here.

## In this repository

1. Open the folder in Cursor.
2. The rule [`.cursor/rules/stm32-bist-guidelines.mdc`](.cursor/rules/stm32-bist-guidelines.mdc) is committed with `alwaysApply: true`, so no extra installation is needed.
3. In Cursor, confirm it under **Settings → Rules**, where `stm32-bist-guidelines` should appear.

## Use the same guidelines in another STM32 project

**Cursor (recommended):**
```bash
mkdir -p .cursor/rules
curl -o .cursor/rules/stm32-bist-guidelines.mdc https://raw.githubusercontent.com/AmineLtaiefST/AI_BIST_AGENT/main/.cursor/rules/stm32-bist-guidelines.mdc
```

**Other tools:** Copy [`CLAUDE.md`](CLAUDE.md) into the project root instead (or merge its contents into your existing `CLAUDE.md`).

**Add project-specific context on top:**
```markdown
## Project-Specific Guidelines

- Target: STM32G474, IAR 9.40, STM32CubeG4 v1.5
- Register access only — no HAL
- BIST results stored in BIST_Result_t gBIST_Results (section .bist_results, no init)
- Safety level: ASIL B (ISO 26262)
- Fault reaction: BIST failure sets SafeFlag and triggers software reset after 100 ms
```

## Claude Code vs Cursor vs VS Code

- **Claude Code:** Use [`CLAUDE.md`](CLAUDE.md) per project, or install the skill from [`skills/stm32-bist/SKILL.md`](skills/stm32-bist/SKILL.md).
- **Cursor:** Use the committed `.cursor/rules/stm32-bist-guidelines.mdc` as described above.
- **VS Code:** Use the committed [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for GitHub Copilot. See [`VSCODE.md`](VSCODE.md).

## For contributors

When you change the rules, keep [`CLAUDE.md`](CLAUDE.md), [`.github/copilot-instructions.md`](.github/copilot-instructions.md), [`.cursor/rules/stm32-bist-guidelines.mdc`](.cursor/rules/stm32-bist-guidelines.mdc), and [`skills/stm32-bist/SKILL.md`](skills/stm32-bist/SKILL.md) in sync.
