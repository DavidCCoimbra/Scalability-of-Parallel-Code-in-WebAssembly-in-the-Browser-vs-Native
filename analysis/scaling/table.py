from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from analysis.configuration import Configuration
from analysis.runs import RunSummary, values_by_configuration
from analysis.stats.bootstrap import Interval, bootstrap_interval
from analysis.stats.summary import CONFIGURATION_CENTER, Summary

SINGLE_THREAD_INTERVAL = Interval(1.0, 1.0)


@dataclass(frozen=True)
class Speedup:
    value: float
    interval: Interval

    def efficiency(self, threads: int) -> "Speedup":
        return Speedup(self.value / threads, self.interval.divided_by(threads))


@dataclass(frozen=True)
class ScalingRow:
    configuration: Configuration
    runs: int
    baseline_runs: int
    center_ns: float
    speedup: float | None
    speedup_interval: Interval | None
    efficiency: float | None
    efficiency_interval: Interval | None


def speedup_of(baseline: Sequence[float], values: Sequence[float], center: Summary) -> Speedup:
    def ratio(groups: list[list[float]]) -> float:
        return center.of(groups[0]) / center.of(groups[1])

    return Speedup(center.of(baseline) / center.of(values), bootstrap_interval([baseline, values], ratio))


def row_without_baseline(configuration: Configuration, values: Sequence[float], center: Summary) -> ScalingRow:
    return ScalingRow(configuration, len(values), 0, center.of(values), None, None, None, None)


def row_with_speedup(
    configuration: Configuration, values: Sequence[float], baseline: Sequence[float], center: Summary, speedup: Speedup
) -> ScalingRow:
    efficiency = speedup.efficiency(configuration.threads)
    return ScalingRow(
        configuration,
        len(values),
        len(baseline),
        center.of(values),
        speedup.value,
        speedup.interval,
        efficiency.value,
        efficiency.interval,
    )


# Strong scaling within one environment: speedup = T1 / TN with T1 from the same
# environment, workload, input and k; N = 1 is 1 by definition and is not resampled.
def scaling_row(
    configuration: Configuration, values: Sequence[float], baseline: Sequence[float] | None, center: Summary
) -> ScalingRow:
    if baseline is None:
        return row_without_baseline(configuration, values, center)
    if configuration.threads == 1:
        return row_with_speedup(configuration, values, baseline, center, Speedup(1.0, SINGLE_THREAD_INTERVAL))
    return row_with_speedup(configuration, values, baseline, center, speedup_of(baseline, values, center))


def scaling_table(runs: Iterable[RunSummary], center: Summary = CONFIGURATION_CENTER) -> list[ScalingRow]:
    groups = values_by_configuration(runs)
    return [
        scaling_row(configuration, values, groups.get(configuration.baseline()), center)
        for configuration, values in sorted(groups.items())
    ]
