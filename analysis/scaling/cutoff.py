import sys
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from analysis.configuration import ENVIRONMENTS, Configuration, Workload, workload_order
from analysis.runs import RunSummary
from analysis.scaling.table import scaling_table
from analysis.stats.bootstrap import Interval
from analysis.stats.summary import CONFIGURATION_CENTER

# The filter, and the local histogram at k = 256; not k = 1, whose single-counter chain is
# a microarchitecture artefact.
CUTOFF_WORKLOADS: tuple[tuple[str, int | None], ...] = ((Workload.FILTER, None), (Workload.HIST_LOCAL, 256))
NS_PER_US = 1_000
TABLE_COLUMNS = (
    "environment",
    "workload",
    "input",
    "k",
    "threads",
    "side",
    "runs",
    "t1_ns",
    "tn_ns",
    "speedup",
    "speedup_low",
    "speedup_high",
    "efficiency",
    "work_us",
)

CurveKey = tuple[str, str, str, int | None, int]


@dataclass(frozen=True)
class CutoffPoint:
    side: int
    configuration: Configuration
    runs: int
    t1_ns: float
    tn_ns: float
    speedup: float
    speedup_interval: Interval

    @property
    def threads(self) -> int:
        return self.configuration.threads

    @property
    def efficiency(self) -> float:
        return self.speedup / self.threads

    # A run value is the time per pass, and one pass is one parallel region, so T1 per
    # pass is the work of one region.
    @property
    def work_us(self) -> float:
        return self.t1_ns / NS_PER_US

    @property
    def curve(self) -> CurveKey:
        c = self.configuration
        return c.environment, c.workload, c.input, c.k, c.threads


def is_cutoff_workload(configuration: Configuration) -> bool:
    return (configuration.workload, configuration.k) in CUTOFF_WORKLOADS


def cutoff_points(side: int, runs: Iterable[RunSummary]) -> list[CutoffPoint]:
    kept = [run for run in runs if is_cutoff_workload(run.configuration)]
    rows = scaling_table(kept, CONFIGURATION_CENTER)
    centers = {row.configuration: row.center_ns for row in rows}
    points = []
    for row in rows:
        if row.speedup is None or row.speedup_interval is None:
            print(f"cutoff-{side}: no N = 1 runs for {row.configuration.label}, dropped", file=sys.stderr)
            continue
        t1 = centers[row.configuration.baseline()]
        points.append(CutoffPoint(side, row.configuration, row.runs, t1, row.center_ns, row.speedup, row.speedup_interval))
    return points


def point_order(point: CutoffPoint) -> tuple[int, tuple[str, int], int, int]:
    c = point.configuration
    return ENVIRONMENTS.index(c.environment), workload_order((c.workload, c.k)), c.threads, point.side


def table_row(point: CutoffPoint) -> dict[str, Any]:
    low, high = point.speedup_interval
    return {
        **dict(zip(("environment", "workload", "input", "k", "threads"), point.configuration.cells())),
        "side": point.side,
        "runs": point.runs,
        "t1_ns": round(point.t1_ns),
        "tn_ns": round(point.tn_ns),
        "speedup": f"{point.speedup:.3f}",
        "speedup_low": f"{low:.3f}",
        "speedup_high": f"{high:.3f}",
        "efficiency": f"{point.efficiency:.3f}",
        "work_us": f"{point.work_us:.1f}",
    }


def table_rows(points: Iterable[CutoffPoint]) -> list[dict[str, Any]]:
    return [table_row(point) for point in sorted(points, key=point_order)]


def curves(points: Iterable[CutoffPoint]) -> dict[CurveKey, list[CutoffPoint]]:
    grouped: dict[CurveKey, list[CutoffPoint]] = {}
    for point in points:
        grouped.setdefault(point.curve, []).append(point)
    return {key: sorted(series, key=lambda point: point.side) for key, series in sorted(grouped.items(), key=lambda item: point_order(item[1][0]))}
