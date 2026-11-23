import csv
import statistics
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

from analysis.configuration import Configuration
from analysis.extras.perf.run_counters import RunCounters
from analysis.stats.bootstrap import bootstrap_interval

RETRIES_COUNTER = "lock_loads"


def cell_columns(configuration: Configuration) -> list[str | int]:
    return [configuration.environment, configuration.workload, "" if configuration.k is None else configuration.k, configuration.threads]


# Counted over the completed runs, the excluded ones included: an exclusion is not a gap in the
# campaign, and the summary's runs column gives the n each mean is over.
def short_cells(completed: Iterable[Configuration], repetitions: int) -> list[str]:
    runs = Counter(completed)
    return [f"{cell.label}: {count} runs" for cell, count in sorted(runs.items()) if count < repetitions]


# Every row of one campaign has the same counters, in table order.
def counter_names(rows: list[RunCounters]) -> tuple[str, ...]:
    return tuple(rows[0].per_operation) if rows else ()


def write_runs(rows: list[RunCounters], path: Path) -> None:
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        names = counter_names(rows)
        writer.writerow(["run_id", "environment", "workload", "k", "threads", "operations", "intervals", *names])
        for row in rows:
            run = row.run
            writer.writerow(
                [run.run_id, *cell_columns(run.configuration), run.operations, row.intervals]
                + [f"{row.per_operation[name]:.4f}" for name in names]
            )


def mean_of(groups: list[list[float]]) -> float:
    return statistics.fmean(groups[0])


# The arithmetic mean: a rate can be 0, so the geometric mean of the timing analysis does not apply.
def write_summary(rows: list[RunCounters], path: Path) -> None:
    cells: dict[Configuration, list[RunCounters]] = defaultdict(list)
    for row in rows:
        cells[row.run.configuration].append(row)
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["environment", "workload", "k", "threads", "runs", "counter", "mean", "low", "high"])
        for configuration, cell in sorted(cells.items()):
            for name in counter_names(rows):
                values = [row.per_operation[name] for row in cell]
                interval = bootstrap_interval([values], mean_of)
                writer.writerow(
                    [*cell_columns(configuration), len(values), name]
                    + [f"{value:.4f}" for value in (mean_of([values]), interval.low, interval.high)]
                )


def mean_difference(groups: list[list[float]]) -> float:
    return statistics.fmean(groups[1]) - statistics.fmean(groups[0])


# Every compare-and-swap attempt is one locked load, so the locked loads per operation at the
# largest N above those at N = 1 count the retries; the N = 1 count already holds the run's own
# locked operations outside the loop.
def write_retries(rows: list[RunCounters], path: Path) -> None:
    lock_loads: dict[Configuration, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        configuration = row.run.configuration
        lock_loads[configuration.baseline()][configuration.threads].append(row.per_operation[RETRIES_COUNTER])
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["environment", "workload", "k", "threads", "excess_lock_loads", "low", "high"])
        for baseline, by_threads in sorted(lock_loads.items()):
            threads = max(by_threads)
            if threads == 1 or 1 not in by_threads:
                continue
            groups = [by_threads[1], by_threads[threads]]
            interval = bootstrap_interval(groups, mean_difference)
            writer.writerow(
                cell_columns(baseline.at_threads(threads))
                + [f"{value:.4f}" for value in (mean_difference(groups), interval.low, interval.high)]
            )
