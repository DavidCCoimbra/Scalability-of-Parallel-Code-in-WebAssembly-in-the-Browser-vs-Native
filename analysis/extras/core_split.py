"""The one-thread run values of a campaign, split by the core that did the work.

Usage: python3 -m analysis.extras.core_split data/raw/<campaign> --output TABLE.csv
A campaign leaves the placement of a run to the kernel. Each run records how long every measured
CPU was busy, so a one-thread run can be put on the core it ran on. Per configuration and core:
how many runs, and their values against the median of the configuration.
"""

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from analysis.configuration import Configuration, CsvCell
from analysis.loading import InvalidCampaign, LoadedCampaign, add_exclusion_arguments, exclusion_rule, load_campaign
from analysis.run_context import run_context
from analysis.scaling.output import CONFIGURATION_COLUMNS

COLUMNS = (*CONFIGURATION_COLUMNS, "cpu", "runs", "median_over_configuration", "max_over_configuration")
ONE_THREAD = 1


def table_rows(campaign: LoadedCampaign) -> list[list[CsvCell]]:
    by_core: dict[Configuration, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    summaries = [*campaign.summaries(), *campaign.sequential_summaries()]
    for run in summaries:
        cpu = run_context(campaign.directory, run.run).busiest_cpu
        if run.configuration.threads == ONE_THREAD and cpu is not None:
            by_core[run.configuration][cpu].append(run.value)
    rows: list[list[CsvCell]] = []
    for configuration, cores in sorted(by_core.items()):
        centre = statistics.median(value for values in cores.values() for value in values)
        for cpu, values in sorted(cores.items()):
            rows.append([*configuration.cells(), cpu, len(values), f"{statistics.median(values) / centre:.4f}", f"{max(values) / centre:.4f}"])
    return rows


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
