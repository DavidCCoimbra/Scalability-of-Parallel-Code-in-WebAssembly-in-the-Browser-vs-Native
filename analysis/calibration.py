"""Fork-join cost of a campaign from the calibration samples of its runs.

Usage: python3 -m analysis.calibration data/raw/<campaign> --output fork-join.csv
       [--strict] [--foreign-cpu-threshold SECONDS]
The runs are those of the primary analysis: the same exclusions apply.
Per environment, thread count, probe (empty broadcast or empty par_iter) and
phase (warm: calls back to back; cold: one call after a pause), over the runs
of every workload ("all") and of each workload: the number of runs, the median
over runs of each run's median sample, and the mean over runs of each run's
mean sample, in microseconds. The cold cost depends on the workload of the
run, so both views are written.
"""

import argparse
import csv
import statistics
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from analysis.configuration import ENVIRONMENTS
from analysis.loading import InvalidCampaign, add_exclusion_arguments, exclusion_rule, load_campaign
from analysis.runs import Row

NS_PER_US = 1_000
PHASES = {"calibration-warm": "warm", "calibration-cold": "cold"}
ALL_WORKLOADS = "all"
ENVIRONMENT_ORDER = {environment.value: position for position, environment in enumerate(ENVIRONMENTS)}
COLUMNS = ("environment", "workload", "threads", "probe", "phase", "runs", "median_of_run_medians_us", "mean_of_run_means_us")


@dataclass(frozen=True, order=True)
class Cell:
    environment: str
    workload: str
    threads: int
    probe: str
    phase: str


def run_samples(rows: Iterable[Row]) -> dict[tuple[str, Cell], list[float]]:
    samples: dict[tuple[str, Cell], list[float]] = {}
    for row in rows:
        phase = PHASES.get(row["phase"])
        if phase is None:
            continue
        for workload in (ALL_WORKLOADS, row["workload"]):
            cell = Cell(row["env"], workload, int(row["threads"]), row["probe"], phase)
            samples.setdefault((row["run"], cell), []).append(float(row["ns"]))
    return samples


def microseconds(ns: float) -> str:
    return f"{ns / NS_PER_US:.1f}"


def calibration_rows(rows: Iterable[Row]) -> list[list[str]]:
    medians: dict[Cell, list[float]] = {}
    means: dict[Cell, list[float]] = {}
    for (_, cell), values in run_samples(rows).items():
        medians.setdefault(cell, []).append(statistics.median(values))
        means.setdefault(cell, []).append(statistics.fmean(values))

    def order(cell: Cell) -> tuple[int, bool, Cell]:
        return (ENVIRONMENT_ORDER[cell.environment], cell.workload != ALL_WORKLOADS, cell)

    return [
        [
            cell.environment,
            cell.workload,
            str(cell.threads),
            cell.probe,
            cell.phase,
            str(len(medians[cell])),
            microseconds(statistics.median(medians[cell])),
            microseconds(statistics.fmean(means[cell])),
        ]
        for cell in sorted(medians, key=order)
    ]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    add_exclusion_arguments(parser)
    args = parser.parse_args(argv)
    try:
        campaign = load_campaign(args.directory, exclusion_rule(args))
    except InvalidCampaign as invalid:
        print(f"error: {invalid}", file=sys.stderr)
        return 1
    with args.output.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(calibration_rows(campaign.rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
