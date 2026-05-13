# POST Integration Plan

## Confirmed Facts

- Target product: STM32H755ZITx / STM32H755ZIT6, STM32H7, LQFP144.
- Toolchain: STM32CubeIDE.
- Firmware package: STM32Cube FW_H7 V1.11.2.
- Generated structure: dual-core CM7 and CM4 projects.
- Requested BIST phase: POST.
- Requested analog path: PA4.
- PA4 mapping from IOC: DAC1_OUT1 and ADC1_INP18.

## Current Evidence Gaps

- The generated IOC marks `board=custom`; it is not confirmed as a Nucleo Board Selector project.
- ADC1, DAC1, a trigger timer, DAC DMA, and ADC DMA are not yet generated as configured peripherals.
- The generated HAL configuration keeps ADC, DAC, and TIM modules disabled.
- The project was generated in `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/` instead of the canonical `project/` folder.
- CM7 and CM4 `Core/Src/main.c` files already exist; no new `main.c` should be created.
- POST fault reaction and result reporting mechanism are not defined yet.
- RAM execution from base address `0x20000000` is not verified yet for this BIST.

## Required Resource Discovery

Before BIST code is generated, use the existing template and ask only the missing resource questions, one at a time. For this project, PA4 already gives a candidate DAC/ADC path, but HAL ADC/DAC/TIM/DMA calls are absent, so the agent must confirm:

1. ADC instance/channel and mode: single-ended or differential; if differential, the second channel.
2. DAC instance/channel and whether the DAC-to-ADC path is internal, external, shared pin, or product-specific routing.
3. One deterministic synchronization timer. Prefer two output-compare events/channels from the same timer: one for DAC update and one phase-shifted event for ADC conversion after DAC settling.
4. DMA mapping discovered from documentation/source first, asking only if DAC or ADC DMA request/channel/stream remains unclear.
5. Generated init functions or manual integration points in the selected owner core, preferably CM7 unless the safety architecture assigns the BIST to CM4.

## Proposed BIST Architecture After Regeneration

1. Keep CubeMX-generated initialization in generated files and place BIST logic in separate BIST-specific files where possible.
2. Use static storage only: DAC LUT, ADC sample buffer, FFT input/output buffers, magnitude buffer, per-run metrics, and result table staging.
3. Run the acquisition 20 times.
4. Capture exactly 256 ADC samples per run with a bounded timeout.
5. Stop timer, ADC DMA, DAC DMA, ADC, and DAC deterministically on completion or fault.
6. Compute SNR, THD, SINAD, and ENOB with CMSIS-DSP.
7. Report pass/fail using the project-defined POST result mechanism.
8. Do not silently retry or clear faults.

## Verification Plan

- Verify peripheral integration: `MX_ADC1_Init`, `MX_DAC1_Init`, selected `MX_TIMx_Init` or approved equivalent, DMA init, and HAL module enables are present.
- Verify resource map: ADC1 channel 18, DAC1 channel 1, timer trigger, DMA requests, and owner core.
- Verify build: build CM7 and CM4 projects with STM32CubeIDE or generated build command.
- Verify RAM execution: inspect linker/map evidence before claiming BIST code executes from `0x20000000`.
- Verify acquisition: timeout path, exactly 256 samples, expected FFT fundamental bin 3.
- Verify target behavior: run on board and record SNR, THD, SINAD, ENOB across 20 runs.

## Do Not Modify Without Approval

- Startup files.
- Linker scripts.
- Clock tree and `SystemClock_Config`.
- MPU/cache setup.
- IRQ priorities.
- POST result table or safety state machine.
- Fault handlers.
