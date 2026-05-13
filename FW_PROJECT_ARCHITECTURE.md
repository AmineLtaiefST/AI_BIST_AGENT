# Firmware Project Architecture

Modified by Amine LTAIEF.

This document defines the folder convention for concrete STM32 BIST firmware projects handled by the agent. The goal is to keep each firmware project easy to identify by product and by BIST test, without mixing project files, product documentation, validation artifacts, and result reports at repository root.

## Canonical Path

Use this path for every concrete firmware BIST project:

```text
fw_projects/<PRODUCT_ID>/<TEST_ID>/
```

`<PRODUCT_ID>` is the exact STM32 product, part number, or internal product identifier normalized for a folder name. `<TEST_ID>` is the BIST pipeline or test name normalized for a folder name.

Use uppercase letters, digits, and underscores. Avoid spaces and accents in folder names because STM32 toolchains, scripts, and build systems are easier to keep portable with simple paths.

Examples:

```text
fw_projects/STM32G474VETX/ADC_SINGLE_AC_BIST/
fw_projects/<INTERNAL_PRODUCT_ID>/ADC_SINGLE_AC_BIST/
fw_projects/<INTERNAL_PRODUCT_ID>/RAM_BIST/
```

## Folder Layout

Each `<TEST_ID>` folder should use this structure:

```text
fw_projects/<PRODUCT_ID>/<TEST_ID>/
  README.md
  project/
  product/
  bist/
  validation/
  reports/
```

Use `project/` for the real STM32 firmware project: `.ioc`, `.project`, `.cproject`, `Inc/`, `Src/`, `Drivers/`, `Startup/`, linker scripts, EWARM files, Makefiles, and generated toolchain files.

For a new firmware project, `project/` should be created from STM32CubeMX or STM32CubeIDE before BIST code generation starts. The user must choose the CubeMX creation source first: MCU/Product Selector, Board Selector, or an approved existing `.ioc`/template. The generated project should then be placed under `fw_projects/<PRODUCT_ID>/<TEST_ID>/project/`.

If a functional product template or generated firmware project already exists, the agent must inspect and use it first instead of asking the user to create a new CubeMX project. The agent should verify the template evidence: `.ioc`, source folders, include folders, drivers, startup/linker/toolchain metadata, selected core ownership, and existing peripheral initialization. CubeMX creation or regeneration should be requested only when the template is absent, incomplete, contradictory, or explicitly selected by the user.

If the template already contains `Core/Src/main.c`, the agent must not ask to create a new `main.c`. It should choose the owner core, use the existing file or project extension points, and treat missing ADC/DAC/timer/DMA setup as missing resource knowledge first. The agent must ask the focused ADC/DAC/timer/DMA questions after inspecting the template before it discusses CubeMX regeneration or manual integration.

For ADC dynamic BISTs on an existing template, the agent should ask only focused missing questions after inspection: ADC instance/channel/mode, differential second channel when applicable, DAC instance/channel and connection path, synchronization timer/OC trigger strategy when unclear, and DMA mapping only when product documentation, `.ioc`, generated source, DMAMUX/DMA tables, and driver APIs do not provide a safe answer.

The agent may help automate CubeMX/CubeIDE project creation only when a supported command or CLI is available and the user approves using it. Otherwise, the agent should provide the exact target folder and wait until the user has generated or imported the CubeMX project.

On Windows, when `STM32CubeMX.exe` is installed in `PATH`, the agent may run `STM32CubeMX.exe -i` after user approval to open STM32CubeMX interactively. Opening CubeMX is not enough to continue: the agent must still verify the generated `.ioc`, source folders, driver folders, startup/linker files, and toolchain metadata under `project/`.

Use `product/` for product facts needed by the BIST workflow. For internal or unpublished products, store only approved references, paths, document versions, or sanitized excerpts. The internal product document and the project driver library remain the source of truth.

Use `bist/` for BIST-specific design notes, integration notes, generated LUTs, static memory maps, resource ownership notes, and RAM execution assumptions.

Use `validation/` for build commands, simulation logs, target measurement notes, GPIO/SWO timing captures, and fault-injection observations.

Use `reports/` for BIST result reports produced from the pipeline report template.

## Project README Template

Create `fw_projects/<PRODUCT_ID>/<TEST_ID>/README.md` with this minimum content:

```markdown
# <PRODUCT_ID> - <TEST_ID>

## Target
- Product: <exact product, part number, or internal id>
- Product status: published | internal | unpublished
- STM32 family/part: <family and exact part/internal id>
- Firmware project: project/
- CubeMX creation source: MCU/Product Selector | Board Selector | Existing `.ioc`/template
- CubeMX toolchain: <STM32CubeIDE | EWARM | MDK | Makefile/CMake | other>
- CubeMX firmware package: <name/version>
- Driver library: <name/version/path>
- Product document: <name/version/path or public RM/DS>

## BIST
- Pipeline: <pipeline document path>
- Phase: POST | PEST | on-demand
- Fault reaction: <reporting and system reaction>
- RAM execution mechanism: <section/linker/startup mechanism>
- Static memory budget: <buffers and sizes>

## ADC Scope
- ADC IP/name: <value or N/A>
- ADC instance: <value or N/A>
- ADC channel: <value or N/A>
- DAC/timer/DMA resources: <values or TBD>

## Verification
- Build command: <command or TBD>
- Target validation: done | not done
- Timing validation: done | not done
- Last report: reports/<report file or TBD>
```

## Handling Reference Examples

Do not keep bulky ad hoc firmware examples at the repository root once their useful behavior has been extracted. First capture the reusable behavior in a lightweight pattern or report document, then archive or delete the original reference project only with explicit user approval.

For ADC dynamic SoftBIST generation, the extracted reusable reference is:

```text
ADC_DYNAMIC_SOFTBIST_PATTERN.md
```

Concrete firmware projects should still be created under `fw_projects/<PRODUCT_ID>/<TEST_ID>/project/` with product-specific source code, drivers, toolchain files, validation logs, and reports.
