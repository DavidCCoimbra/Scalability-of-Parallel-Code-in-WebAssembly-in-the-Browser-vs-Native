# Extra, not part of RQ1 or RQ2: the SIMD build variants (scalar, AVX2) of the filter.

import sys
from dataclasses import dataclass, replace
from typing import Any

from analysis.configuration import ENVIRONMENTS, Configuration, Environment, Workload
from analysis.runs import RunSummary
from analysis.scaling.table import scaling_table
from analysis.stats.bootstrap import Interval
from analysis.stats.summary import CONFIGURATION_CENTER

BASELINE_BUILD = "baseline"
VARIANT_WORKLOAD = Workload.FILTER
COLUMNS = (
    "build",
    "environment",
    "threads",
    "runs",
    "center_ns",
    "efficiency",
    "efficiency_low",
    "efficiency_high",
    "excess_ns",
    "over_baseline",
    "over_native",
)

CenterKey = tuple[str, Configuration]


@dataclass(frozen=True)
class VariantPoint:
    build: str
    configuration: Configuration
    runs: int
    center_ns: float
    efficiency: float
    efficiency_interval: Interval

    @property
    def environment(self) -> str:
        return self.configuration.environment

    @property
    def threads(self) -> int:
        return self.configuration.threads

    @property
    def key(self) -> CenterKey:
        return self.build, self.configuration

    def counterpart(self, build: str, environment: str) -> CenterKey:
        return build, replace(self.configuration, environment=environment)

    def single_thread(self) -> CenterKey:
        return self.build, self.configuration.baseline()


def variant_points(build: str, runs: list[RunSummary]) -> list[VariantPoint]:
    filtered = [run for run in runs if run.configuration.workload == VARIANT_WORKLOAD]
    points = []
    for row in scaling_table(filtered, CONFIGURATION_CENTER):
        if row.efficiency is None or row.efficiency_interval is None:
            print(f"{build}: no N = 1 runs for {row.configuration}, dropped", file=sys.stderr)
            continue
        points.append(VariantPoint(build, row.configuration, row.runs, row.center_ns, row.efficiency, row.efficiency_interval))
    return points


def ratio_cell(numerator: float, denominator: float | None) -> str:
    return "" if denominator is None else f"{numerator / denominator:.3f}"


def table_order(point: VariantPoint) -> tuple[str, int, int]:
    return point.build, ENVIRONMENTS.index(point.environment), point.threads


# Efficiency alone cannot tell a shared resource from a fixed overhead (a fixed cost f
# gives faster code the lower efficiency 1 / (1 + N f / T1)), so the excess TN - T1 / N is kept too.
def table_row(point: VariantPoint, centers: dict[CenterKey, float]) -> dict[str, Any]:
    excess = point.center_ns - centers[point.single_thread()] / point.threads
    low, high = point.efficiency_interval
    return {
        "build": point.build,
        "environment": point.environment,
        "threads": point.threads,
        "runs": point.runs,
        "center_ns": round(point.center_ns),
        "efficiency": f"{point.efficiency:.3f}",
        "efficiency_low": f"{low:.3f}",
        "efficiency_high": f"{high:.3f}",
        "excess_ns": round(excess),
        "over_baseline": ratio_cell(point.center_ns, centers.get(point.counterpart(BASELINE_BUILD, point.environment))),
        "over_native": ratio_cell(point.center_ns, centers.get(point.counterpart(point.build, Environment.NATIVE))),
    }


def table_rows(points: list[VariantPoint]) -> list[dict[str, Any]]:
    centers = {point.key: point.center_ns for point in points}
    return [table_row(point, centers) for point in sorted(points, key=table_order)]
