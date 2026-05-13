# ADC Dynamic SoftBIST Pattern

Modified by Amine LTAIEF.

This file preserves the useful information extracted from the former `Exemple de Bist/` firmware reference. It is intentionally lightweight: it captures the BIST architecture, resource pattern, result interface, and generation rules without keeping a full Cube/IAR firmware project in this agent repository.

Use this document together with `Pepline_ADC_SINGLE_AC_BIST.md` and `.github/agents/stm32-bist-orchestrator.agent.md` when generating a concrete ADC dynamic BIST inside `fw_projects/<PRODUCT_ID>/<TEST_ID>/project/`.

## Reference Facts Extracted

- Reference target: STM32G474VETx, STM32G4 family, LQFP100.
- Reference project name: `474_ADC_SB_AC`.
- Toolchain/configuration observed: IAR EWARM V8.32, STM32CubeMX 5.3.0, STM32Cube FW_G4 V1.1.0.
- BIST style: standalone ADC dynamic SoftBIST intended for ATE/debug observation.
- Execution model: RAM-oriented build with code and vector table placed in RAM at base `0x20000000`.
- Result interface: fixed SRAM result table at `0x20009000` plus GPIO status pins.
- DSP library: Arm CMSIS-DSP floating-point FFT functions.

These facts describe only the reference project. For any new product, reconfirm the exact product, publication status, ADC IP, ADC instance, ADC channel, routing, timer triggers, DMA mapping, GPIO pins, toolchain, and allowed driver layer.

## Reference BIST Flow

1. Initialize HAL and system clock.
2. Reset or initialize the result table and progress counter.
3. Start execution timing measurement using DWT cycle counter on Cortex-M4.
4. Initialize GPIO status pins for ATE/debug signaling.
5. Initialize DAC, DAC DMA, and DAC trigger timer.
6. Initialize ADC, ADC calibration, ADC interrupt capture, and ADC trigger timer.
7. Start timer-triggered DAC waveform generation and ADC sampling.
8. Collect exactly 256 ADC samples corresponding to a coherent 3-period sine record.
9. Stop ADC acquisition and owned resources.
10. Convert ADC samples to DSP buffers.
11. Run CMSIS-DSP FFT and magnitude computation.
12. Extract the fundamental bin and harmonics.
13. Compute THD, SNR, SINAD, and ENOB.
14. Deinitialize or restore ADC, DAC, timer, DMA, GPIO, and IRQ resources as required by the project.
15. Stop timing measurement.
16. Write the result table and final marker.
17. Update GPIO pass/fail/error status only after the result table is complete.

## Reference Resources

The reference used the following concrete STM32G474 resources:

| Resource | Reference value |
|----------|-----------------|
| ADC under test | ADC2 |
| ADC channel | ADC channel 17 |
| ADC pin/path | PA4 / ADC2_IN17 |
| ADC capture | EOC interrupt capture variant |
| DAC stimulus | DAC1 channel 1 |
| DAC waveform transfer | DMA1 Channel 1, memory-to-DAC |
| DAC LUT | 256 samples, 3 sine periods |
| ADC trigger timer | TIM1 update/TRGO path in source |
| DAC trigger timer | TIM2 update/TRGO path in source |
| DSP size | 256-point FFT |
| Result SRAM base | `0x20009000` |
| Timing source | DWT CYCCNT on Cortex-M4 |
| Status GPIOs | PA0, PA1, PA2 used for status; PA3 intended for error in handler |

Do not copy these resources to another product without checking the product document, public RM/DS for published products, and the firmware project driver/library configuration.

## Stimulus And Capture Pattern

- DAC stimulus is a coherent sine lookup table.
- Reference length is 256 samples.
- Reference coherence is 3 complete sine periods in 256 samples, so the expected fundamental FFT bin is bin 3.
- Pipeline target range is 100 to 3900 LSB, offset 2000 LSB, amplitude 1900 LSB unless the product document overrides it.
- The observed source LUT must always be checked against the pipeline values; if source and pipeline differ, surface the discrepancy and ask which one is authoritative.
- The ADC capture mechanism may be either:
  - pipeline-preferred ADC DMA capture, or
  - reference-style ADC EOC interrupt capture with bounded downsampling.
- The selected variant must be stated before implementation. Do not silently mix DMA and ISR capture logic.

## DSP And Metrics

Use the project-approved CMSIS-DSP library. The reference pipeline is:

1. Convert ADC raw codes to floating-point DSP input.
2. Build a CMSIS-DSP-compatible complex/interleaved FFT buffer.
3. Run 256-point FFT.
4. Compute magnitude or power per bin.
5. Clear or exclude the DC bin.
6. Detect the fundamental and verify the expected bin, normally bin 3.
7. Extract the first required harmonics.
8. Compute THD, SNR, SINAD, and ENOB.

Metric formulas must be documented in the generated project. Do not add empirical ENOB offsets, metric corrections, or hidden scale factors unless they come from a requirement, product document, or validated reference.

## Result Table Pattern

The reference wrote 4-byte fields to a fixed SRAM table. A generated BIST must define named offsets and keep comments, documentation, and write order consistent.

Recommended fields:

| Offset | Field |
|--------|-------|
| `0x00` | Start marker, for example `0x5555AAAA` |
| `0x04` | Progress/status/pass counter |
| `0x08` | Fault code or THD field, depending on product result map |
| `0x0C` | SNR |
| `0x10` | SINAD |
| `0x14` | ENOB, with explicit scaling if integer-stored |
| `0x18` | Fundamental FFT bin |
| `0x1C` | Reserved or product-specific diagnostic field |
| `0x20` | SoftBIST revision |
| `0x24` | Execution time in microseconds or cycles with documented unit |
| `0x28` | Stop marker, for example `0xAAAA5555` |

Before using a fixed SRAM address, verify from the linker/map that it does not overlap code, constants, data, BSS, stack, heap, DMA buffers, retained state, or another BIST/result table.

## Mandatory Guardrails For Generation

- Acquisition must be bounded. Never generate an unbounded wait for `sample_count == 256`.
- On timeout or acquisition failure, stop owned resources, write a diagnosable fault code, and skip DSP on partial data.
- ISR code must remain minimal: initialize gate flags, read/store one sample, bounds-check the write index, update done/fault flags, and avoid heavy logic.
- Static buffer sizes must be cross-checked: LUT, ADC raw buffer, real buffer, complex FFT buffer, magnitude buffer, harmonic buffer, metric array, and result table.
- Harmonic buffer length must match the maximum harmonic index written by the DSP helper.
- Float-to-integer metric storage must define units, scaling, clipping/saturation, and handling of negative, NaN, infinite, or out-of-range values.
- GPIO ATE pins must be explicitly initialized before use; final pass/fail/error GPIO state must be updated only after the result table stop marker is written.
- Direct register writes require explicit access-policy approval and named masks/macros. Prefer the project driver layer already used by the firmware.
- CubeMX-generated files, MSP, IRQ, startup, linker, clock tree, and IRQ priorities must not be modified without explicit user approval.
- Generated documentation must state whether validation is static-only, build-only, simulation-only, or verified on target hardware.

## Integration Checklist For A New Project

Before letting the agent implement this BIST in a target firmware project, provide or confirm only what cannot be discovered from the approved product template/project, `.ioc`, product document, generated source, and driver library. If a functional product template already exists, the agent must inspect it first and must not ask for CubeMX project creation. If HAL ADC/DAC/TIM/DMA calls are absent, the agent must ask the focused resource questions below before discussing CubeMX regeneration or manual integration.

Provide or confirm:

- Product name/family/part number or internal product identifier.
- Product status: published, internal, or unpublished.
- Public RM/DS for published products, or internal product document for internal/unpublished products.
- Firmware project path under `fw_projects/<PRODUCT_ID>/<TEST_ID>/project/`.
- Driver library path/version and allowed API layer: product driver, HAL, LL, raw register access, or defined combination.
- ADC IP/name, ADC instance, ADC channel, ADC pin or internal route, and ADC mode: single-ended or differential.
- Second ADC channel if differential mode is selected.
- DAC instance/channel and analog connection to the ADC input: internal route, external connection, shared pin, or product-specific analog routing.
- Timer trigger resources, trigger delay, and expected ADC:DAC timing relationship. Prefer one common timer with two deterministic output-compare events/channels: one for DAC update and one phase-shifted event for ADC conversion after DAC settling.
- DMA resources for DAC and, if used, ADC capture. The agent must inspect product documentation, `.ioc`, generated source/MSP, DMAMUX/DMA mapping, and driver APIs before asking about DMA request/channel/stream choices.
- ADC sampling time, target sample frequency, DAC settling requirement, and expected FFT fundamental bin.
- BIST phase: POST, PEST, or on-demand.
- Fault reaction and result reporting mechanism.
- RAM execution and result-memory reservation mechanism.
- Static memory budget for all LUT, capture, FFT, metric, and result buffers.
- Validation method: build, simulation, target run, GPIO timing, SWO, ATE, or manual measurement.
