"""The two factors of the RQ2 ratio, and the absolute cost of synchronization.

Usage: python3 -m analysis.rq2_decomposition data/raw/<campaign> --max-threads N
       --output decomposition.csv [--strict] [--foreign-cpu-threshold SECONDS]
The RQ2 effect is a ratio of ratios: (A_b / A_n) / (L_b / L_n), with A the
time of the atomic histogram, L of the local one, b a browser and n native.
Per browser and k at N threads, the table has both factors and the ratio of
the excesses, (A_b - L_b) / (A_n - L_n): the time the shared counters add in
the browser over the time they add natively. Post hoc: not in the analysis
plan, so every interval is an uncorrected 95 % percentile bootstrap interval.
"""

import argparse
import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from analysis.configuration import BROWSERS, Configuration, Environment, Workload
from analysis.loading import InvalidCampaign, add_exclusion_arguments, exclusion_rule, load_campaign
from analysis.runs import values_by_configuration
from analysis.stats.bootstrap import Interval, bootstrap_interval
from analysis.stats.summary import CONFIGURATION_CENTER

COLUMNS = ("environment", "k", "threads", "quantity", "ratio", "low", "high")
Groups = list[list[float]]


def center(values: list[float]) -> float:
    return CONFIGURATION_CENTER.of(values)


# Each takes the four groups in the order of Cells.groups: A_b, L_b, A_n, L_n.
def atomic_ratio(groups: Groups) -> float:
    return center(groups[0]) / center(groups[2])


def local_ratio(groups: Groups) -> float:
    return center(groups[1]) / center(groups[3])


def rq2_ratio(groups: Groups) -> float:
    return atomic_ratio(groups) / local_ratio(groups)


# Undefined (nan) when the atomic histogram is not slower than the local one natively: there is
# then no native excess to compare with.
def excess_ratio(groups: Groups) -> float:
    native_excess = center(groups[2]) - center(groups[3])
    return (center(groups[0]) - center(groups[1])) / native_excess if native_excess > 0 else math.nan


# rq2 = atomic / local; excess is the ratio of (A - L) between the browser and native.
QUANTITIES = (
    ("rq2", rq2_ratio),
    ("atomic", atomic_ratio),
    ("local", local_ratio),
    ("excess", excess_ratio),
)


@dataclass(frozen=True)
class Cells:
    browser_atomic: Configuration
    groups: Groups


def cells(values: dict[Configuration, list[float]], threads: int) -> list[Cells]:
    found = []
    for atomic in sorted(values):
        if atomic.environment not in BROWSERS or atomic.workload != Workload.HIST_ATOMIC or atomic.threads != threads:
            continue
        local = atomic.as_workload(Workload.HIST_LOCAL)
        wanted = [atomic, local, atomic.in_environment(Environment.NATIVE), local.in_environment(Environment.NATIVE)]
        if all(configuration in values for configuration in wanted):
            found.append(Cells(atomic, [values[configuration] for configuration in wanted]))
    return found


def number(value: float) -> str:
    return f"{value:.4g}"


def decomposition_rows(values: dict[Configuration, list[float]], threads: int) -> list[list[str]]:
    rows = []
    for cell in cells(values, threads):
        for name, statistic in QUANTITIES:
            interval: Interval = bootstrap_interval(cell.groups, statistic)
            atomic = cell.browser_atomic
            rows.append(
                [atomic.environment, str(atomic.k), str(threads), name, number(statistic(cell.groups)), number(interval.low), number(interval.high)]
            )
    return rows


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--max-threads", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    add_exclusion_arguments(parser)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        summaries = load_campaign(args.directory, exclusion_rule(args)).summaries()
    except InvalidCampaign as invalid:
        print(f"error: {invalid}", file=sys.stderr)
        return 1
    with args.output.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(decomposition_rows(values_by_configuration(summaries), args.max_threads))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
