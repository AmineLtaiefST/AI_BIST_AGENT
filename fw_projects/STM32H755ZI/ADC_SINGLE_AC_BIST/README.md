# STM32H755ZI - ADC_SINGLE_AC_BIST

## Target

- Product: STM32H755ZI
- Product status: published
- STM32 family/part: STM32H7 / STM32H755ZITx, CPN STM32H755ZIT6, LQFP144
- Board: Nucleo board requested by user, but generated IOC currently records `board=custom`
- Firmware project: ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/ generated in place; canonical `project/` folder remains empty
- Existing entry points: CM7 `Core/Src/main.c` and CM4 `Core/Src/main.c` are present and referenced by `.mxproject`
- CubeMX creation source: MCU/Product Selector or custom IOC, not confirmed as Board Selector by generated IOC
- CubeMX toolchain: STM32CubeIDE
- CubeMX firmware package: STM32Cube FW_H7 V1.11.2
- Driver library: generated STM32H7xx HAL driver under `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/Drivers/`
- Product document: public STM32H755 reference manual and datasheet

## BIST

- Pipeline: ../../../Pepline_ADC_SINGLE_AC_BIST.md
- Reference pattern: ../../../ADC_DYNAMIC_SOFTBIST_PATTERN.md
- BIST phase: POST, pending project safety architecture confirmation
- ADC under test: PA4 shared analog path, CubeMX signal `ADC1_INP18`
- DAC stimulus: PA4 shared analog path, CubeMX signal `DAC1_OUT1`

## Bootstrap Status

- Canonical folder created: yes
- CubeMX project generated: yes, but not under canonical `project/`
- Generated project evidence: `.ioc`, CM7/CM4 `Core/`, `Drivers/`, startup/linker files, `.project`, `.cproject`, and `.mxproject` are present
- BIST code generation status: do not create a new `main.c`; use the existing owner-core entry point. HAL ADC/DAC/TIM/DMA calls are not present, so the next agent action is to ask focused ADC/DAC/timer/DMA resource questions after using the known PA4 mapping, not to request CubeMX project creation.

## Open Items

- Use the existing generated project in `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/` unless the user explicitly chooses to move or regenerate it.
- Ask the focused missing-resource questions: ADC instance/channel/mode, DAC instance/channel/connection, common timer/two-OC trigger strategy, and unclear DMA mapping after inspection.
- Only discuss CubeMX regeneration if the answered resource choices require changing generated configuration and the user chooses that route.
- Confirm BIST resource-owning core: CM7 or CM4.
- Confirm POST execution policy, fault reaction, and result reporting mechanism.
- Confirm RAM execution and result-memory reservation mechanism before BIST code generation.

## Generated Notes

- Resource map: bist/RESOURCE_MAP.md
- Bootstrap check: validation/BOOTSTRAP_CHECK.md
