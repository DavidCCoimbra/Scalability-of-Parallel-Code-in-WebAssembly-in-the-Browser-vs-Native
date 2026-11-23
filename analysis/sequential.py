"""The speedup against sequential code, from the sequential references of a campaign.

Usage: python3 -m analysis.sequential data/raw/<campaign> --output TABLE.csv
The relative speedup of the scaling table divides by the same code on a pool of one thread. This
table divides the time of a sequential reference (the same kernel in one plain loop, no Rayon) by
the time of the parallel workload at every N: at N = 1 that is what the pool of one thread costs,
and at larger N it is the speedup over code that was never parallel. 95 % bootstrap intervals.
"""

import argparse
import csv
import sys
from pathlib import Path

from analysis.configuration import Configuration, CsvCell, Workload
from analysis.loading import InvalidCampaign, LoadedCampaign, add_exclusion_arguments, exclusion_rule, load_campaign
from analysis.runs import values_by_configuration
from analysis.scaling.output import CONFIGURATION_COLUMNS
from analysis.scaling.table import speedup_of
from analysis.stats.summary import CONFIGURATION_CENTER

# The sequential reference of each parallel workload: the same kernel and the same output.
REFERENCE = {
    Workload.FILTER: Workload.FILTER_SEQ,
    Workload.HIST_LOCAL: Workload.HIST_SEQ,
    Workload.HIST_ATOMIC: Workload.HIST_SEQ,
}
COLUMNS = (*CONFIGURATION_COLUMNS, "runs", "sequential_runs", "sequential_ns", "center_ns", "speedup_vs_sequential", "low", "high")
SIGNIFICANT_DIGITS = 4
SEQUENTIAL_THREADS = 1


def number(value: float) -> str:
    return f"{value:.{SIGNIFICANT_DIGITS}g}"


def table_rows(campaign: LoadedCampaign) -> list[list[CsvCell]]:
    parallel = values_by_configuration(campaign.summaries())
    sequential = values_by_configuration(campaign.sequential_summaries())
    rows: list[list[CsvCell]] = []
    for configuration, values in sorted(parallel.items()):
        reference = REFERENCE.get(Workload(configuration.workload)) if configuration.workload in set(Workload) else None
        baseline = sequential.get(reference_of(configuration, reference)) if reference is not None else None
        if not baseline:
            continue
        speedup = speedup_of(baseline, values, CONFIGURATION_CENTER)
        rows.append(
            [
                *configuration.cells(),
                len(values),
                len(baseline),
                f"{CONFIGURATION_CENTER.of(baseline):.0f}",
                f"{CONFIGURATION_CENTER.of(values):.0f}",
                *(number(value) for value in (speedup.value, *speedup.interval)),
            ]
        )
    return rows


def reference_of(configuration: Configuration, reference: Workload) -> Configuration:
    return configuration.as_workload(reference).at_threads(SEQUENTIAL_THREADS)


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    add_exclusion_arguments(parser)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        campaign = load_campaign(args.directory, exclusion_rule(args))
    except InvalidCampaign as invalid:
        print(f"error: {invalid}", file=sys.stderr)
        return 1
    campaign.report_gaps()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(table_rows(campaign))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
