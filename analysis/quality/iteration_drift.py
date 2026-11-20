import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import TextIO

from analysis.configuration import Configuration, CsvCell, configuration_of
from analysis.runs import MEASURED, Row
from harness.collect import collect

# The first three measured iterations against the last three.
DEFAULT_WINDOW = 3
COLUMNS = ("environment", "workload", "input", "k", "threads", "runs", "first_median_ns", "last_median_ns", "first_over_last")

RunTimes = dict[str, list[int]]


@dataclass(frozen=True)
class IterationDrift:
    configuration: Configuration
    runs: int
    first_median_ns: float
    last_median_ns: float

    @property
    def first_over_last(self) -> float:
        return self.first_median_ns / self.last_median_ns

    def cells(self) -> list[CsvCell]:
        return self.configuration.cells() + [
            self.runs,
            f"{self.first_median_ns:.0f}",
            f"{self.last_median_ns:.0f}",
            f"{self.first_over_last:.3f}",
        ]


def measured_series(rows: list[Row]) -> dict[Configuration, RunTimes]:
    series: defaultdict[Configuration, defaultdict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["phase"] == MEASURED:
            series[configuration_of(row)][row["run"]].append(int(row["ns"]))
    return dict(series)


# Pitfall: a ratio near 1 says the measured iterations do not trend, but it
# cannot see a slower level that lasts through every measured iteration.
def drift_of(configuration: Configuration, runs: RunTimes, window: int) -> IterationDrift:
    first = [ns for times in runs.values() for ns in times[:window]]
    last = [ns for times in runs.values() for ns in times[-window:]]
    return IterationDrift(configuration, len(runs), median(first), median(last))


def drifts(directory: Path, window: int) -> list[IterationDrift]:
    series = measured_series(collect(directory).rows)
    return [drift_of(configuration, series[configuration], window) for configuration in sorted(series)]


def write_drifts(rows: list[IterationDrift], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(COLUMNS)
    for drift in rows:
        writer.writerow(drift.cells())
