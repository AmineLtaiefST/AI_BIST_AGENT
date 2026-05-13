# ADC_SINGLE_AC_BIST Resource Map

## Confirmed From CubeMX IOC

- Project path analyzed: `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/`
- IOC: `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST.ioc`
- MCU: STM32H755ZITx
- Commercial part number: STM32H755ZIT6
- Package: LQFP144
- CubeMX version: 6.12.0
- STM32Cube firmware package: STM32Cube FW_H7 V1.11.2
- Target toolchain: STM32CubeIDE
- Project structure: dual core, CM7 and CM4 projects
- Board selector status: `board=custom` in the IOC

## PA4 Analog Mapping

CubeMX currently maps PA4 as a shared analog pin:

| Pin | CubeMX shared signal | Function |
|-----|----------------------|----------|
| PA4 | SharedAnalog_PA4.0 | DAC1_OUT1 |
| PA4 | SharedAnalog_PA4.1 | ADC1_INP18 |

This confirms the requested DAC-to-ADC PA4 path at the pin-mapping level.

## Current Firmware Generation Gap

The generated IOC does not currently enable the ADC1, DAC1, TIM, or peripheral-specific DMA configuration needed by the ADC Single AC BIST. The generated CM7 and CM4 source files already contain `Core/Src/main.c`, but they do not contain `MX_ADC*`, `MX_DAC*`, or ADC/DAC BIST timer initialization functions, and `stm32h7xx_hal_conf.h` keeps the ADC and DAC HAL modules commented out.

Do not create a new `main.c`. Use the existing owner-core `main.c` or project extension points. Because HAL ADC/DAC/TIM/DMA calls are absent, ask the focused missing-resource questions before proposing a CubeMX regeneration or manual integration route.

## Required Resource Questions Before BIST Code

- ADC: confirm ADC IP/instance, channel, and single-ended or differential mode. If differential, confirm the second channel.
- DAC: confirm DAC instance/channel and whether the DAC reaches the ADC through an internal route, external connection, shared pin, or product-specific analog routing.
- Timer: confirm the common synchronization timer. Prefer two output-compare events/channels from the same timer: one for DAC update and one phase-shifted event for ADC conversion after DAC settling.
- DMA: inspect product documentation, IOC, generated source/MSP, DMAMUX/DMA mapping, and driver APIs first. Ask only if the DAC or ADC DMA request/channel/stream remains unclear or conflicting.
- Core ownership: confirm whether CM7 or CM4 owns the BIST resources.
- Keep acquisition bounded with timeout handling in the BIST code after the resource choices are known.

## Open Decisions

- Confirm whether to keep this generated project in `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/` or move/regenerate it under the canonical `project/` folder.
- Confirm whether the project should be regenerated from the exact Nucleo Board Selector instead of the current `board=custom` IOC.
- Confirm BIST resource-owning core: CM7 or CM4.
- Confirm POST fault reaction and result reporting mechanism.
- Confirm RAM execution mechanism at base address `0x20000000` before BIST code generation.
