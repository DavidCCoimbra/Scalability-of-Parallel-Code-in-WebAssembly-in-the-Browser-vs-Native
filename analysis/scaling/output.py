import csv
from enum import Enum
from typing import TextIO

from analysis.configuration import CsvCell
from analysis.scaling.table import ScalingRow
from analysis.stats.bootstrap import Interval

CONFIGURATION_COLUMNS = ("environment", "workload", "input", "k", "threads")
COUNT_COLUMNS = ("runs", "baseline_runs", "center_ns")
STRONG_COLUMNS = (
    *CONFIGURATION_COLUMNS,
    *COUNT_COLUMNS,
    "speedup",
    "speedup_low",
    "speedup_high",
    "efficiency",
    "efficiency_low",
    "efficiency_high",
)
WEAK_COLUMNS = (*CONFIGURATION_COLUMNS, *COUNT_COLUMNS, "weak_efficiency", "weak_efficiency_low", "weak_efficiency_high")
NO_INTERVAL = (None, None)


# Under weak scaling the work grows with N, so T1 / TN is already the weak-scaling efficiency and
# dividing it by N would mean nothing.
class Scaling(Enum):
    STRONG = "strong"
    WEAK = "weak"

    @property
    def columns(self) -> tuple[str, ...]:
        return WEAK_COLUMNS if self is Scaling.WEAK else STRONG_COLUMNS


def number(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def ratio_cells(value: float | None, interval: Interval | None) -> list[CsvCell]:
    low, high = interval or NO_INTERVAL
    return [number(value), number(low), number(high)]


def scaling_cells(row: ScalingRow, scaling: Scaling) -> list[CsvCell]:
    cells = row.configuration.cells() + [row.runs, row.baseline_runs, f"{row.center_ns:.0f}"]
    cells += ratio_cells(row.speedup, row.speedup_interval)
    if scaling is Scaling.STRONG:
        cells += ratio_cells(row.efficiency, row.efficiency_interval)
    return cells


def write_scaling(rows: list[ScalingRow], output: TextIO, scaling: Scaling = Scaling.STRONG) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(scaling.columns)
    for row in rows:
        writer.writerow(scaling_cells(row, scaling))
