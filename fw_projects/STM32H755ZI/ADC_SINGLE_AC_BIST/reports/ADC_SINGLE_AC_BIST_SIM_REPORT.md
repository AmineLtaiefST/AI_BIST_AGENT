# BIST Result Report: ADC Single AC BIST Simulation

## Target

- Product: STM32H755ZI
- Product status: published
- STM32 family/part: STM32H7 / STM32H755ZITx, CPN STM32H755ZIT6, LQFP144
- ADC under test: planned ADC1_INP18 on PA4; not yet generated as an ADC peripheral in CubeMX
- Firmware project: `fw_projects/STM32H755ZI/ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/`
- Driver library: generated STM32Cube FW_H7 V1.11.2 HAL drivers
- Internal product document: N/A, published product
- BIST phase: POST requested, pending project safety architecture confirmation

## Pipeline

- Pipeline document: `Pepline_ADC_SINGLE_AC_BIST.md`
- Reference pattern: `ADC_DYNAMIC_SOFTBIST_PATTERN.md`
- Resources used: simulation-only DAC/ADC signal model; no target ADC/DAC/TIM/DMA resources executed
- RAM execution mechanism: not verified; no firmware BIST code generated yet
- Static memory used: simulation host memory only; firmware LUT, DMA, FFT, and result storage not allocated yet

## Acceptance Criteria

- ENOB > 9 bits across all 20 runs
- SNR > 50 dB across all 20 runs
- THD < -50 dB across all 20 runs
- SINAD reported; no dedicated SINAD threshold is currently specified

## Results

| Metric | Min | Max | Mean | Spread/StdDev | Threshold | Status |
|--------|-----|-----|------|---------------|-----------|--------|
| SNR | 70.210 dB | 72.200 dB | 71.384 dB | 0.551 dB | > 50 dB | PASS |
| THD | -68.932 dB | -65.866 dB | -67.356 dB | 0.786 dB | < -50 dB | PASS |
| SINAD | 64.905 dB | 67.120 dB | 65.884 dB | 0.564 dB | TBD | REPORTED |
| ENOB | 10.489 bits | 10.857 bits | 10.652 bits | 0.094 bits | > 9 bits | PASS |

## Verification

- Build/test command: `python fw_projects/STM32H755ZI/ADC_SINGLE_AC_BIST/validation/adc_single_ac_bist_sim.py`
- Target validation: not done
- Timing validation: not done
- Simulation assumptions: coherent 256-sample capture, 3 sine periods, fundamental FFT bin 3, 25% SNR band, no STM32 register/timer/DMA/analog routing model

## Findings

- The signal-level simulation passes the current dynamic metric thresholds for 20 repeated runs.
- The generated IOC confirms PA4 shared analog mapping for DAC1_OUT1 and ADC1_INP18.
- Firmware BIST implementation has not started. Because HAL ADC/DAC/TIM/DMA calls are absent in the current template, the next step is focused resource discovery: confirm ADC, DAC, synchronization timer, and unclear DMA facts before selecting CubeMX regeneration or manual integration.
- Both CM7 and CM4 generated HAL configuration files currently leave ADC, DAC, and TIM HAL modules disabled.
- RAM execution from base address `0x20000000` and fixed result-memory reservation are not verified for this BIST.

## Open Items

- Ask the focused ADC/DAC/timer/DMA resource questions using the known PA4 mapping as evidence.
- Confirm BIST resource-owning core: CM7 or CM4.
- Confirm POST result reporting mechanism and fault reaction policy.
- Confirm whether the generated project should stay under `ADC_SINGLE_AC_BIST/ADC_SINGLE_AC_BIST/` or be regenerated/moved under the canonical `project/` folder.
- Verify RAM execution and result-memory placement from linker/map evidence before firmware BIST code generation.