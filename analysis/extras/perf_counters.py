"""Hardware counters per atomic operation, per run, from the perf-v2 campaign.

scripts/perf-counters-v2.sh counts the eight P-cores system-wide in 100 ms intervals while an
ordinary campaign runs. Runs are sequential, so the intervals that end inside one run's
startedAt..finishedAt window belong to that run. Each run's counts are divided by its atomic
operations: one per pixel per warm-up or measured iteration (8192^2 x 15 per run). The window
also holds the browser's start-up and the calibration, which add few locked operations next to
the 1.0e9 of the timed loop.

Usage: python3 -m analysis.extras.perf_counters data/raw/perf-v2
       --runs data/tables/perf-v2/perf-v2-runs.csv --summary data/tables/perf-v2/perf-v2-counters.csv
       --retries data/tables/perf-v2/perf-v2-retries.csv
The summary has the arithmetic mean per configuration with a 95 % percentile bootstrap interval
over runs: a rate can be 0, so the geometric mean of the timing analysis does not apply.
The retries table has, per environment and k, the locked loads per operation at the largest N
minus those at N = 1. Every compare-and-swap attempt is one locked load, so the excess counts
V8's retries; the N = 1 count already holds the run's own locked operations outside the loop.
"""

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from analysis.stats.bootstrap import bootstrap_interval

# The perf events of scripts/perf-counters-v2.sh, by the name used in the tables.
EVENTS = {
    "cpu_core/cycles/": "cycles",
    "cpu_core/instructions/": "instructions",
    "cpu_core/mem_inst_retired.lock_loads/": "lock_loads",
    "cpu_core/ocr.demand_rfo.l3_hit.snoop_hitm/": "rfo_hitm",
    "cpu_core/ocr.demand_data_rd.l3_hit.snoop_hitm/": "read_hitm",
}
COUNTERS = tuple(EVENTS.values())
# perf stat -x, prints the share of the interval the event was counted; below 100 it multiplexed.
FULLY_COUNTED = "100.00"
TIMED_PHASES = ("warmup", "measured")
RUN_NAME = re.compile(r"-(?P<environment>native|chrome|firefox)-(?P<workload>[a-z-]+)-k(?P<k>\d+)-n(?P<threads>\d+)-r(?P<repetition>\d+)$")


@dataclass(frozen=True)
class Interval:
    end: float
    counts: dict[str, float]


@dataclass(frozen=True)
class Run:
    run_id: str
    environment: str
    workload: str
    k: int
    threads: int
    start: float
    end: float
    operations: int


@dataclass(frozen=True)
class RunCounters:
    run: Run
    intervals: int
    per_operation: dict[str, float]


def timestamp(text: str) -> float:
    return datetime.fromisoformat(text).timestamp()


# One perf stat -I segment: "<seconds since start>,<count>,,<event>,<run time>,<percent>,..." rows
# after comment lines. A row not counted, unsupported or multiplexed would read as a false rate, so
# it stops the analysis instead of becoming 0.
def read_segment(csv_path: Path, start: float) -> list[Interval]:
    by_time: dict[float, dict[str, float]] = defaultdict(dict)
    for line in csv_path.read_text().splitlines():
        fields = line.split(",")
        if line.startswith("#") or len(fields) < 6 or fields[3] not in EVENTS:
            continue
        if fields[5] != FULLY_COUNTED:
            raise ValueError(f"{csv_path}: {fields[3]} not fully counted at {fields[0]} s: {line}")
        by_time[float(fields[0])][EVENTS[fields[3]]] = float(fields[1])
    return [Interval(start + seconds, counts) for seconds, counts in sorted(by_time.items())]


def read_intervals(counters_dir: Path) -> list[Interval]:
    intervals: list[Interval] = []
    for csv_path in sorted(counters_dir.glob("*.csv")):
        start = float(csv_path.with_suffix(".start").read_text())
        intervals.extend(read_segment(csv_path, start))
    return sorted(intervals, key=lambda interval: interval.end)


def operations(csv_path: Path) -> int:
    with csv_path.open(newline="") as file:
        rows = [row for row in csv.DictReader(file) if row["phase"] in TIMED_PHASES]
    return sum(int(row["width"]) * int(row["height"]) * int(row["passes"] or 1) for row in rows)


def read_runs(raw: Path) -> Iterator[Run]:
    for json_path in sorted(raw.glob("*.json")):
        match = RUN_NAME.search(json_path.stem)
        if match is None:
            continue
        record = json.loads(json_path.read_text())
        yield Run(
            run_id=json_path.stem,
            environment=match["environment"],
            workload=match["workload"],
            k=int(match["k"]),
            threads=int(match["threads"]),
            start=timestamp(record["startedAt"]),
            end=timestamp(record["finishedAt"]),
            operations=operations(json_path.with_suffix(".csv")),
        )


def counters_of(run: Run, intervals: Iterable[Interval]) -> RunCounters:
    inside = [interval for interval in intervals if run.start < interval.end <= run.end]
    totals = {name: sum(interval.counts.get(name, 0.0) for interval in inside) for name in COUNTERS}
    return RunCounters(run, len(inside), {name: totals[name] / run.operations for name in COUNTERS})


def planned_repetitions(raw: Path) -> int | None:
    campaign = raw / "campaign.json"
    if not campaign.exists():
        return None
    repetitions: int = json.loads(campaign.read_text())["spec"]["repetitions"]
    return repetitions


def short_cells(rows: list[RunCounters], repetitions: int) -> list[str]:
    runs: dict[tuple[str, str, int, int], int] = defaultdict(int)
    for row in rows:
        runs[(row.run.environment, row.run.workload, row.run.k, row.run.threads)] += 1
    return [f"{cell}: {count} runs" for cell, count in sorted(runs.items()) if count < repetitions]


def write_runs(rows: list[RunCounters], path: Path) -> None:
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["run_id", "environment", "workload", "k", "threads", "operations", "intervals", *COUNTERS])
        for row in rows:
            run = row.run
            writer.writerow(
                [run.run_id, run.environment, run.workload, run.k, run.threads, run.operations, row.intervals]
                + [f"{row.per_operation[name]:.4f}" for name in COUNTERS]
            )


def mean_of(groups: list[list[float]]) -> float:
    return statistics.fmean(groups[0])


def write_summary(rows: list[RunCounters], path: Path) -> None:
    cells: dict[tuple[str, str, int, int], list[RunCounters]] = defaultdict(list)
    for row in rows:
        cells[(row.run.environment, row.run.workload, row.run.k, row.run.threads)].append(row)
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["environment", "workload", "k", "threads", "runs", "counter", "mean", "low", "high"])
        for (environment, workload, k, threads), cell in sorted(cells.items()):
            for name in COUNTERS:
                values = [row.per_operation[name] for row in cell]
                interval = bootstrap_interval([values], mean_of)
                writer.writerow(
                    [environment, workload, k, threads, len(values), name]
                    + [f"{value:.4f}" for value in (mean_of([values]), interval.low, interval.high)]
                )


def mean_difference(groups: list[list[float]]) -> float:
    return statistics.fmean(groups[1]) - statistics.fmean(groups[0])


def write_retries(rows: list[RunCounters], path: Path) -> None:
    lock_loads: dict[tuple[str, str, int], dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        lock_loads[(row.run.environment, row.run.workload, row.run.k)][row.run.threads].append(row.per_operation["lock_loads"])
    with path.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["environment", "workload", "k", "threads", "excess_lock_loads", "low", "high"])
        for (environment, workload, k), by_threads in sorted(lock_loads.items()):
            threads = max(by_threads)
            if threads == 1 or 1 not in by_threads:
                continue
            groups = [by_threads[1], by_threads[threads]]
            interval = bootstrap_interval(groups, mean_difference)
            writer.writerow(
                [environment, workload, k, threads]
                + [f"{value:.4f}" for value in (mean_difference(groups), interval.low, interval.high)]
            )


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--retries", type=Path)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    intervals = read_intervals(args.raw / "counters")
    rows = [counters_of(run, intervals) for run in read_runs(args.raw)]
    empty = [row.run.run_id for row in rows if row.intervals == 0]
    if empty:
        print(f"runs with no counter interval: {empty}", file=sys.stderr)
        return 1
    repetitions = planned_repetitions(args.raw)
    short = short_cells(rows, repetitions) if repetitions is not None else []
    if short:
        print(f"configurations with fewer than {repetitions} runs: {short}", file=sys.stderr)
        return 1
    args.runs.parent.mkdir(parents=True, exist_ok=True)
    write_runs(rows, args.runs)
    write_summary(rows, args.summary)
    if args.retries is not None:
        write_retries(rows, args.retries)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
