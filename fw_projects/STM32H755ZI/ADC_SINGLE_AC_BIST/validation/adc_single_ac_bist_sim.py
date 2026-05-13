"""Simulation-only STM32 ADC single AC BIST model.

This script mirrors the repository ADC_SINGLE_AC_BIST pipeline at signal level:
it generates a coherent DAC sine record, simulates ADC capture, computes FFT-bin
power, and reports SNR, THD, SINAD, and ENOB over repeated runs.

It does not model STM32 registers, DMA, timers, analog routing, or HAL behavior.
Use product documentation and the target firmware driver library for hardware code.
"""

from __future__ import annotations

import argparse
import cmath
import math
import random
from dataclasses import dataclass
from statistics import mean, pstdev


SAMPLE_COUNT = 256
SINE_PERIODS = 3
FUNDAMENTAL_BIN = SINE_PERIODS
DEFAULT_RUNS = 20
DEFAULT_ADC_BITS = 12
DEFAULT_DAC_MIN_CODE = 100
DEFAULT_DAC_MAX_CODE = 3900
DEFAULT_DAC_OFFSET_CODE = 2000
DEFAULT_DAC_AMPLITUDE_CODE = 1900
DEFAULT_NOISE_RMS_LSB = 0.70
DEFAULT_SECOND_HARMONIC_LSB = 0.70
DEFAULT_THIRD_HARMONIC_LSB = 0.35
DEFAULT_FOURTH_HARMONIC_LSB = 0.20
DEFAULT_SEED = 20260505
DEFAULT_SNR_BAND_FRACTION = 0.25


@dataclass(frozen=True)
class SimulationConfig:
    sample_count: int = SAMPLE_COUNT
    sine_periods: int = SINE_PERIODS
    adc_bits: int = DEFAULT_ADC_BITS
    dac_min_code: int = DEFAULT_DAC_MIN_CODE
    dac_max_code: int = DEFAULT_DAC_MAX_CODE
    dac_offset_code: float = DEFAULT_DAC_OFFSET_CODE
    dac_amplitude_code: float = DEFAULT_DAC_AMPLITUDE_CODE
    noise_rms_lsb: float = DEFAULT_NOISE_RMS_LSB
    second_harmonic_lsb: float = DEFAULT_SECOND_HARMONIC_LSB
    third_harmonic_lsb: float = DEFAULT_THIRD_HARMONIC_LSB
    fourth_harmonic_lsb: float = DEFAULT_FOURTH_HARMONIC_LSB
    snr_band_fraction: float = DEFAULT_SNR_BAND_FRACTION
    runs: int = DEFAULT_RUNS
    seed: int = DEFAULT_SEED

    @property
    def adc_max_code(self) -> int:
        return (1 << self.adc_bits) - 1

    @property
    def fundamental_bin(self) -> int:
        return self.sine_periods

    @property
    def nyquist_bin(self) -> int:
        return self.sample_count // 2

    @property
    def snr_band_last_bin(self) -> int:
        return max(1, round(self.nyquist_bin * self.snr_band_fraction))


@dataclass(frozen=True)
class DynamicMetrics:
    snr_db: float
    thd_db: float
    sinad_db: float
    enob_bits: float
    fundamental_bin: int


def clip(value: float, lower: float, upper: float) -> float:
    return min(max(value, lower), upper)


def build_dac_lut(config: SimulationConfig) -> list[int]:
    lut: list[int] = []

    for sample_index in range(config.sample_count):
        phase = 2.0 * math.pi * config.sine_periods * sample_index / config.sample_count
        dac_code = round(config.dac_offset_code + config.dac_amplitude_code * math.sin(phase))
        lut.append(int(clip(dac_code, config.dac_min_code, config.dac_max_code)))

    return lut


def simulate_adc_capture(config: SimulationConfig, rng: random.Random) -> list[int]:
    adc_codes: list[int] = []
    adc_mid_code = config.adc_max_code / 2.0

    for sample_index in range(config.sample_count):
        phase = 2.0 * math.pi * config.sine_periods * sample_index / config.sample_count
        ideal_code = config.dac_offset_code + config.dac_amplitude_code * math.sin(phase)
        distortion = (
            config.second_harmonic_lsb * math.sin(2.0 * phase + 0.20)
            + config.third_harmonic_lsb * math.sin(3.0 * phase - 0.35)
            + config.fourth_harmonic_lsb * math.sin(4.0 * phase + 0.55)
        )
        noise = rng.gauss(0.0, config.noise_rms_lsb)
        captured_code = adc_mid_code + (ideal_code - config.dac_offset_code) + distortion + noise
        adc_codes.append(int(round(clip(captured_code, 0, config.adc_max_code))))

    return adc_codes


def dft_power_by_bin(samples: list[int]) -> list[float]:
    sample_count = len(samples)
    average_code = mean(samples)
    centered_samples = [sample - average_code for sample in samples]
    powers: list[float] = []

    for bin_index in range((sample_count // 2) + 1):
        coefficient = 0j
        for sample_index, sample in enumerate(centered_samples):
            angle = -2.0 * math.pi * bin_index * sample_index / sample_count
            coefficient += sample * cmath.exp(1j * angle)
        powers.append(float(abs(coefficient) ** 2))

    powers[0] = 0.0
    return powers


def safe_log10_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0:
        return float("-inf")
    if denominator <= 0.0:
        return float("inf")
    return 10.0 * math.log10(numerator / denominator)


def compute_dynamic_metrics(config: SimulationConfig, adc_codes: list[int]) -> DynamicMetrics:
    powers = dft_power_by_bin(adc_codes)
    fundamental_bin = config.fundamental_bin
    harmonic_bins = [
        harmonic_index * fundamental_bin
        for harmonic_index in range(2, 5)
        if harmonic_index * fundamental_bin <= config.nyquist_bin
    ]
    excluded_bins = {0, fundamental_bin, *harmonic_bins}

    fundamental_power = powers[fundamental_bin]
    distortion_power = sum(powers[bin_index] for bin_index in harmonic_bins)
    noise_power = sum(
        powers[bin_index]
        for bin_index in range(1, config.snr_band_last_bin + 1)
        if bin_index not in excluded_bins
    )

    snr_db = safe_log10_ratio(fundamental_power, noise_power)
    thd_db = safe_log10_ratio(distortion_power, fundamental_power)
    sinad_db = safe_log10_ratio(fundamental_power, noise_power + distortion_power)
    enob_bits = (sinad_db - 1.76) / 6.02

    return DynamicMetrics(
        snr_db=snr_db,
        thd_db=thd_db,
        sinad_db=sinad_db,
        enob_bits=enob_bits,
        fundamental_bin=fundamental_bin,
    )


def summarize(values: list[float]) -> str:
    return (
        f"min={min(values):8.3f}  max={max(values):8.3f}  "
        f"mean={mean(values):8.3f}  std={pstdev(values):8.3f}"
    )


def run_simulation(config: SimulationConfig) -> list[DynamicMetrics]:
    rng = random.Random(config.seed)
    return [compute_dynamic_metrics(config, simulate_adc_capture(config, rng)) for _ in range(config.runs)]


def print_report(config: SimulationConfig, metrics_by_run: list[DynamicMetrics]) -> None:
    print("STM32 ADC_SINGLE_AC_BIST signal-level simulation")
    print("Assumptions: simulation-only, coherent capture, no STM32 register/timer/DMA model")
    print(f"samples={config.sample_count}, sine_periods={config.sine_periods}, fundamental_bin={config.fundamental_bin}")
    print(f"adc_bits={config.adc_bits}, runs={config.runs}, seed={config.seed}")
    print(f"snr_band_bins=1..{config.snr_band_last_bin} excluding DC/fundamental/harmonics")
    print()

    for run_index, metrics in enumerate(metrics_by_run, start=1):
        print(
            f"run={run_index:02d}  "
            f"SNR={metrics.snr_db:7.2f} dB  "
            f"THD={metrics.thd_db:7.2f} dB  "
            f"SINAD={metrics.sinad_db:7.2f} dB  "
            f"ENOB={metrics.enob_bits:5.2f} bits"
        )

    print()
    print("Summary")
    print(f"SNR   dB   {summarize([metrics.snr_db for metrics in metrics_by_run])}")
    print(f"THD   dB   {summarize([metrics.thd_db for metrics in metrics_by_run])}")
    print(f"SINAD dB   {summarize([metrics.sinad_db for metrics in metrics_by_run])}")
    print(f"ENOB bits {summarize([metrics.enob_bits for metrics in metrics_by_run])}")

    passes = all(
        metrics.enob_bits > 9.0 and metrics.snr_db > 50.0 and metrics.thd_db < -50.0
        for metrics in metrics_by_run
    )
    print()
    print(f"Pipeline thresholds: ENOB > 9 bits, SNR > 50 dB, THD < -50 dB -> {'PASS' if passes else 'FAIL'}")


def parse_args() -> SimulationConfig:
    parser = argparse.ArgumentParser(description="STM32 ADC_SINGLE_AC_BIST signal-level simulation")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--adc-bits", type=int, default=DEFAULT_ADC_BITS)
    parser.add_argument("--noise-rms-lsb", type=float, default=DEFAULT_NOISE_RMS_LSB)
    parser.add_argument("--h2-lsb", type=float, default=DEFAULT_SECOND_HARMONIC_LSB)
    parser.add_argument("--h3-lsb", type=float, default=DEFAULT_THIRD_HARMONIC_LSB)
    parser.add_argument("--h4-lsb", type=float, default=DEFAULT_FOURTH_HARMONIC_LSB)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    if args.runs <= 0:
        parser.error("--runs must be greater than zero")
    if args.adc_bits <= 0:
        parser.error("--adc-bits must be greater than zero")
    if args.noise_rms_lsb < 0.0:
        parser.error("--noise-rms-lsb must be non-negative")

    return SimulationConfig(
        runs=args.runs,
        adc_bits=args.adc_bits,
        noise_rms_lsb=args.noise_rms_lsb,
        second_harmonic_lsb=args.h2_lsb,
        third_harmonic_lsb=args.h3_lsb,
        fourth_harmonic_lsb=args.h4_lsb,
        seed=args.seed,
    )


def main() -> None:
    config = parse_args()
    dac_lut = build_dac_lut(config)
    if len(dac_lut) != config.sample_count:
        raise RuntimeError("DAC LUT length does not match sample count")
    print_report(config, run_simulation(config))


if __name__ == "__main__":
    main()