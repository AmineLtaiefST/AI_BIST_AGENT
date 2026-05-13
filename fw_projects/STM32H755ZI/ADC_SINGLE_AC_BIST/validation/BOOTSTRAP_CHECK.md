# Bootstrap Check

## Generated Project Evidence

| Evidence | Status | Notes |
|----------|--------|-------|
| `.ioc` | Present | `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST.ioc` |
| CM7 source tree | Present | `CM7/Core/Inc`, `CM7/Core/Src`, `CM7/Startup` |
| CM4 source tree | Present | `CM4/Core/Inc`, `CM4/Core/Src`, `CM4/Startup` |
| HAL drivers | Present | Root `Drivers/STM32H7xx_HAL_Driver` and per-core linked driver references |
| CMSIS | Present | Root `Drivers/CMSIS` |
| Linker files | Present | CM7 and CM4 FLASH/RAM linker files generated |
| Toolchain metadata | Present | `.project`, `.cproject`, `.mxproject` |

## Confirmed Configuration

- MCU: STM32H755ZITx
- CPN: STM32H755ZIT6
- Package: LQFP144
- Firmware package: STM32Cube FW_H7 V1.11.2
- Toolchain: STM32CubeIDE
- Cores: CM7 and CM4 generated
- PA4 shared analog mapping: DAC1_OUT1 and ADC1_INP18

## Findings

- The project was generated under `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/`, while the repository convention expects the actual firmware project under `project/`.
- The IOC reports `board=custom`; it does not record a Nucleo Board Selector identity.
- ADC1, DAC1, timer trigger, and DMA channels are not yet generated as configured peripherals.
- HAL ADC, DAC, and TIM modules are not enabled in the generated `stm32h7xx_hal_conf.h` files.
- CM7 and CM4 `Core/Src/main.c` files already exist; do not create another `main.c`.
- HAL ADC/DAC/TIM/DMA calls are absent, so the next step is focused resource discovery: ask only the missing ADC/DAC/timer/DMA questions after using the known template evidence.

## Next Verification After Regeneration

- Confirm `MX_ADC1_Init`, `MX_DAC1_Init`, selected `MX_TIMx_Init`, and DMA init functions are present in the selected core project.
- Confirm ADC1 channel 18 is configured for PA4.
- Confirm DAC1 channel 1 is configured for PA4.
- Confirm DAC DMA request and ADC DMA request are generated.
- Confirm timer trigger source and ADC trigger relationship are explicit in the IOC/source.
- Confirm no startup, linker, clock tree, or IRQ priority edits are needed without explicit approval.
