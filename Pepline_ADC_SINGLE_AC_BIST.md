# ADC Single AC BIST Pipeline

Modified by Amine LTAIEF.

This document captures the first STM32 BIST pipeline for evaluating ADC dynamic parameters using a DAC-generated sine wave and synchronous ADC acquisition.

## Purpose

Evaluate the dynamic behavior of one ADC channel by generating a coherent AC stimulus with the DAC, capturing it with the ADC, and computing:

- SNR
- THD
- SINAD
- ENOB

This BIST is intended to detect ADC dynamic performance degradation, synchronization defects, excessive noise, or distortion in the ADC/DAC acquisition path.

## Global BIST Constraints

- All BIST code must execute from RAM at base address `0x20000000`.
- No dynamic memory allocation is allowed in BIST code: no `malloc`, `calloc`, `realloc`, `free`, `new`, or `delete`.
- LUTs, DMA buffers, FFT buffers, and per-run result buffers must be fixed-size static storage or bounded stack storage.
- Any linker/startup/section placement needed to run this BIST from RAM must be defined by the project architecture before implementation.
- The BIST must be deterministic, bounded in time, and diagnosable.

## Source Of Truth For Internal Products

Many target products may be internal or not yet publicly released. For those products, the agent must not infer ADC, DAC, timer, DMA, trigger, or analog routing details from a similar public STM32 family.

Authoritative sources are:

- The internal product document for the target device.
- The product driver library already used by the firmware project.
- Existing project configuration and integration code.

The agent must use the product driver APIs and names from the project unless the architecture explicitly permits HAL, LL, or raw register access for this BIST. If the internal document or driver library is missing, the agent must ask for it before implementation.

## BIST Type

Recommended classification: intrusive on-demand BIST or controlled periodic BIST.

This test temporarily owns these resources:

- DAC output channel
- ADC input channel
- Timer trigger source, for example TIM2
- DMA channel or stream for DAC sample output
- DMA channel or stream for ADC sample capture
- Internal DAC-to-ADC analog route, or shared PA4 path if internal routing is not available

The pipeline must not be merged silently into POST, PEST, or on-demand flows. The final placement depends on the product safety architecture.

## Signal Definition

The DAC stimulus is a coherent sine lookup table:

- LUT length: 256 samples
- Sine periods inside the LUT: 3 complete periods
- DAC code minimum: 100 LSB
- DAC code maximum: 3900 LSB
- DAC code offset: 2000 LSB
- DAC code amplitude: 1900 LSB

Reference formula:

```text
lut[n] = round(2000 + 1900 * sin(2 * pi * 3 * n / 256))
for n = 0..255
```

The value must be clipped to the configured DAC range if rounding produces an out-of-range value.

Because 3 periods are captured over 256 samples, the ADC record is coherent and the fundamental FFT bin is bin 3 when the ADC captures exactly 256 synchronized samples.

## Synchronization Model

The DAC and ADC must be synchronized from the same timer time base.

Expected model:

1. Configure a timer, for example TIM2, as the common trigger source.
2. Use separate timer trigger events or channels for DAC update and ADC conversion.
3. Start DAC DMA so each timer event outputs one LUT sample.
4. Trigger ADC conversion after a delay from the DAC update so the DAC output has time to settle.
5. Capture exactly 256 ADC samples by DMA.
6. Stop the timer, DAC DMA, and ADC DMA deterministically when the acquisition is complete.

Current working assumption: the ADC conversion trigger is delayed by 3/4 of the DAC sample period after the DAC update. This must be confirmed against the selected STM32 timer trigger capabilities and DAC settling time.

The implementation must verify that the ADC sample index corresponds to the DAC LUT index with the configured delay. If this relationship is not deterministic, the BIST result is not valid.

## Acquisition Pipeline

1. Save or check ownership of ADC, DAC, timer, DMA, and optional PA4 routing resources.
2. Load the static 256-sample DAC LUT.
3. Prepare a static 256-sample ADC capture buffer.
4. Start DAC DMA from the LUT.
5. Start ADC DMA into the capture buffer.
6. Start the common timer.
7. Wait for a bounded acquisition-complete event.
8. Stop timer, ADC DMA, and DAC DMA.
9. Restore or release resources according to the product architecture.
10. Report any timeout, DMA error, trigger error, or resource conflict through the BIST reporting mechanism.

No detected fault may be silently ignored, auto-cleared, or retried unless the safety architecture explicitly permits it.

## DSP Processing Pipeline

Processing uses the Arm CMSIS-DSP library.

Expected fixed-size buffers:

- ADC raw buffer: 256 samples
- DSP input buffer: 256 real samples or CMSIS-DSP compatible complex/interleaved format
- FFT output buffer: CMSIS-DSP compatible fixed-size output
- Magnitude buffer: FFT magnitude per bin
- Per-run metric storage for 20 runs, or fixed-size aggregate statistics

Recommended processing sequence:

1. Convert ADC codes to a numeric DSP format.
2. Remove DC offset before dynamic metric computation.
3. Run the FFT using CMSIS-DSP.
4. Compute magnitude or power per FFT bin.
5. Identify the fundamental at bin 3.
6. Compute harmonics using the first 3 harmonics after the fundamental.
7. Compute SNR over the configured 25% noise bandwidth.
8. Compute THD, SINAD, and ENOB.

Because the acquisition is coherent, no window is expected by default. If a window is introduced later, amplitude and power normalization must be documented explicitly.

## Metric Definitions

Let:

- `Pfund` be the power at the fundamental bin.
- `P2`, `P3`, and `P4` be the power at harmonics 2, 3, and 4 of the fundamental.
- `Pnoise` be the integrated noise power over the configured SNR band, excluding DC, fundamental, and harmonic bins used for distortion.
- `Pdist` be `P2 + P3 + P4`.

THD:

```text
THD_dB = 10 * log10(Pdist / Pfund)
```

SINAD:

```text
SINAD_dB = 10 * log10(Pfund / (Pnoise + Pdist))
```

ENOB:

```text
ENOB_bits = (SINAD_dB - 1.76) / 6.02
```

SNR:

```text
SNR_dB = 10 * log10(Pfund / Pnoise)
```

SNR bandwidth rule from the pipeline: compute SNR on 25% of the band. The exact bin range must be defined by the product architecture, for example 25% of the usable Nyquist FFT bins.

## Stability Loop

The BIST must run the full generate-acquire-process sequence multiple times to evaluate result stability.

Required repeat count:

- 20 runs

For each run, store or update fixed-size statistics for:

- SNR
- THD
- SINAD
- ENOB

At minimum, the final report should expose:

- min
- max
- mean
- run-to-run spread or standard deviation
- pass/fail status

The exact allowed run-to-run variation is not specified yet. Until it is defined, the agent must not invent a stability threshold; it must report the variation and fail only on specified product thresholds.

## Acceptance Criteria

The BIST passes only if all specified thresholds are met across the required repeated runs.

Current thresholds:

- ENOB > 9 bits
- SNR > 50 dB
- THD < -50 dB

SINAD is computed and reported. A dedicated SINAD threshold is not specified yet.

If ENOB, SNR, THD, or stability is not acceptable, the first investigation path is synchronization quality:

- timer trigger alignment
- ADC trigger delay after DAC update
- DAC settling time
- DMA start order
- ADC/DAC sample index alignment
- exact coherent capture of 256 samples over 3 periods
- analog routing, internal connection, or PA4 path integrity
- CPU or bus activity during acquisition

## Implementation Inputs Required Before Coding

Before implementing this BIST for a concrete STM32 project, the agent must ask for or verify:

- Exact STM32 product name, family, part number or internal product identifier.
- Product publication status: published, internal, or unpublished.
- Internal product document path, version, or relevant excerpt for unpublished products.
- Public RM/DS reference for published products, or permission to search the web for official public documentation.
- Product driver library path, version, and allowed ADC/DAC/timer/DMA APIs.
- HAL, LL, or register access policy.
- ADC IP name, ADC instance, and ADC channel to test.
- DAC instance and channel.
- Whether DAC and ADC are internally connected in this product.
- Whether PA4 is used as the fallback shared analog path.
- Timer instance and available trigger outputs or compare channels.
- DMA channels or streams reserved for DAC and ADC.
- ADC sampling time and target sampling frequency.
- DAC settling time requirement.
- BIST phase: POST, PEST, or on-demand.
- BIST result reporting mechanism.
- Fault reaction on threshold failure.
- Linker or section mechanism that places BIST code in RAM at `0x20000000`.
- Static memory budget for LUT, ADC buffer, FFT buffers, and 20-run statistics.
- Exact definition of the 25% SNR bandwidth.
- Stability threshold, if pass/fail must include repeatability and not only metric limits.

## Agent Rules For This Pipeline

When asked to implement or modify this pipeline, the agent must not:

- Guess STM32 register names, timer routing, trigger sources, DMA mapping, or reset values.
- Infer internal product details from a similar public STM32 product when an internal product document or driver library is required.
- Bypass the project driver library unless the project policy explicitly allows it.
- Modify startup files, linker scripts, clock tree, IRQ priorities, watchdog setup, or safety state machines unless explicitly requested.
- Allocate memory dynamically.
- Run the BIST from Flash.
- Hide acquisition, DMA, DSP, or threshold failures.
- Retry a failed run silently.
- Merge this BIST into another BIST flow without an explicit architecture decision.

The agent must:

- Keep the test deterministic and bounded.
- Use DMA for DAC generation and ADC capture to reduce CPU load and noise.
- Use CMSIS-DSP for FFT and magnitude computation.
- Report SNR, THD, SINAD, and ENOB.
- Run 20 repetitions for stability observation.
- Preserve resource ownership and document side effects.
