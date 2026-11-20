from collections import defaultdict
from dataclasses import dataclass

from analysis.configuration import Configuration, Environment, Workload
from analysis.runs import RunSummary, values_by_configuration
from analysis.scaling.table import scaling_table
from analysis.stats.ratio import ratio_of_geometric_means
from analysis.stats.summary import CONFIGURATION_CENTER

WorkloadKey = tuple[str, int | None]


@dataclass(frozen=True)
class ScalingPoint:
    threads: int
    speedup: float
    low: float
    high: float
    efficiency: float


@dataclass(frozen=True)
class RatioPoint:
    threads: int
    value: float
    low: float
    high: float


ScalingCurves = dict[WorkloadKey, dict[str, list[ScalingPoint]]]
RatioCurves = dict[WorkloadKey, dict[str, list[RatioPoint]]]
Rq2Curves = dict[int | None, dict[str, list[RatioPoint]]]


def scaling_curves(runs: list[RunSummary]) -> ScalingCurves:
    curves: ScalingCurves = defaultdict(lambda: defaultdict(list))
    for row in scaling_table(runs, CONFIGURATION_CENTER):
        if row.speedup is None or row.speedup_interval is None or row.efficiency is None:
            continue
        c = row.configuration
        low, high = row.speedup_interval
        curves[(c.workload, c.k)][c.environment].append(ScalingPoint(c.threads, row.speedup, low, high, row.efficiency))
    return curves


def ratio_point(baseline: list[float], treatment: list[float], threads: int) -> RatioPoint:
    ratio = ratio_of_geometric_means(baseline, treatment)
    return RatioPoint(threads, ratio.value, ratio.interval.low, ratio.interval.high)


# T(browser, N) / T(native, N), so a slow browser baseline cannot pass for good scaling.
def absolute_ratios(runs: list[RunSummary]) -> RatioCurves:
    groups = values_by_configuration(runs)
    ratios: RatioCurves = defaultdict(lambda: defaultdict(list))
    for configuration in sorted(groups):
        native = configuration.in_environment(Environment.NATIVE)
        if configuration.environment == Environment.NATIVE or native not in groups:
            continue
        point = ratio_point(groups[native], groups[configuration], configuration.threads)
        ratios[(configuration.workload, configuration.k)][configuration.environment].append(point)
    return ratios


# T(atomic) / T(local) in each environment, the r of RQ2 before taking logs.
def rq2_ratios(runs: list[RunSummary]) -> Rq2Curves:
    groups = values_by_configuration(runs)
    ratios: Rq2Curves = defaultdict(lambda: defaultdict(list))
    for configuration in sorted(groups):
        local = configuration.as_workload(Workload.HIST_LOCAL)
        if configuration.workload != Workload.HIST_ATOMIC or local not in groups:
            continue
        point = ratio_point(groups[local], groups[configuration], configuration.threads)
        ratios[configuration.k][configuration.environment].append(point)
    return ratios
