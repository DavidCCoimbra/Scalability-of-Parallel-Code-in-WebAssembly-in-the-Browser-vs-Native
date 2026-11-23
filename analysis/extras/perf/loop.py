"""Counters of the loop alone: two campaigns that differ only in passes per timed sample."""

import csv
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from analysis.configuration import Configuration
from analysis.extras.perf.run_counters import RunCounters
from analysis.extras.perf.tables import cell_columns, counter_names
from analysis.stats.bootstrap import Interval, bootstrap_interval

COLUMNS = ("environment", "workload", "k", "threads", "runs_few", "runs_many", "counter", "per_pixel", "low", "high")
SIGNIFICANT_DIGITS = 4


@dataclass(frozen=True)
class LoopCounter:
    configuration: Configuration
    runs_few: int
    runs_many: int
    counter: str
    per_pixel: float
    interval: Interval


# A run's count over its whole window: the per-operation value times its operations, which are
# the pixels of every timed sample, warm-up included, times the passes.
def totals(rows: list[RunCounters], counter: str) -> list[float]:
    return [row.per_operation[counter] * row.run.operations for row in rows]


def mean_operations(rows: list[RunCounters]) -> float:
    return statistics.fmean(row.run.operations for row in rows)


# The campaign with more passes does that many more pixels of the same loop and nothing else, so
# the difference of the mean counts over the difference of the pixels is the loop's count per
# pixel: the start of the process, the input and the checksums are in both and cancel.
def loop_counters(few: list[RunCounters], many: list[RunCounters]) -> list[LoopCounter]:
    cells: dict[Configuration, tuple[list[RunCounters], list[RunCounters]]] = defaultdict(lambda: ([], []))
    for row in few:
        cells[row.run.configuration][0].append(row)
    for row in many:
        cells[row.run.configuration][1].append(row)
    table = []
    for configuration, (low_passes, high_passes) in sorted(cells.items()):
        if not low_passes or not high_passes:
            continue
        pixels = mean_operations(high_passes) - mean_operations(low_passes)
        if pixels <= 0:
            raise ValueError(f"{configuration.label}: the second campaign does not do more pixels than the first")

        def per_pixel(groups: list[list[float]], pixels: float = pixels) -> float:
            return (statistics.fmean(groups[1]) - statistics.fmean(groups[0])) / pixels

        for counter in counter_names(low_passes):
            groups = [totals(low_passes, counter), totals(high_passes, counter)]
            table.append(LoopCounter(configuration, len(low_passes), len(high_passes), counter, per_pixel(groups), bootstrap_interval(groups, per_pixel)))
    return table


def write_loop_counters(table: list[LoopCounter], path: Path) -> None:
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in table:
            values = (row.per_pixel, row.interval.low, row.interval.high)
            writer.writerow([*cell_columns(row.configuration), row.runs_few, row.runs_many, row.counter, *(f"{value:.{SIGNIFICANT_DIGITS}g}" for value in values)])


RISE_COLUMNS = ("environment", "workload", "k", "threads", "counter", "over_one_thread", "low", "high")
ONE_THREAD = 1


# How a counter of the loop changes with the thread count: its count per pixel at N threads over
# that at one thread, for the same workload and environment. The four groups of runs (few and
# many passes, at one and at N threads) are resampled together.
def write_rises(few: list[RunCounters], many: list[RunCounters], path: Path) -> None:
    cells: dict[Configuration, tuple[list[RunCounters], list[RunCounters]]] = defaultdict(lambda: ([], []))
    for row in few:
        cells[row.run.configuration][0].append(row)
    for row in many:
        cells[row.run.configuration][1].append(row)
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(RISE_COLUMNS)
        for configuration, (low_passes, high_passes) in sorted(cells.items()):
            base_low, base_high = cells.get(configuration.baseline(), ([], []))
            if configuration.threads == ONE_THREAD or not (low_passes and high_passes and base_low and base_high):
                continue
            pixels = mean_operations(high_passes) - mean_operations(low_passes)
            base_pixels = mean_operations(base_high) - mean_operations(base_low)

            def rise(groups: list[list[float]], pixels: float = pixels, base_pixels: float = base_pixels) -> float:
                loop = (statistics.fmean(groups[1]) - statistics.fmean(groups[0])) / pixels
                base = (statistics.fmean(groups[3]) - statistics.fmean(groups[2])) / base_pixels
                return loop / base

            for counter in counter_names(low_passes):
                groups = [totals(low_passes, counter), totals(high_passes, counter), totals(base_low, counter), totals(base_high, counter)]
                interval = bootstrap_interval(groups, rise)
                values = (rise(groups), interval.low, interval.high)
                writer.writerow([*cell_columns(configuration), counter, *(f"{value:.{SIGNIFICANT_DIGITS}g}" for value in values)])
