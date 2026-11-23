"""The one-thread run values of a campaign, split by the core that did the work.

Usage: python3 -m analysis.extras.core_split data/raw/<campaign> --output TABLE.csv
A campaign leaves the placement of a run to the kernel. Each run records how long every measured
CPU was busy, so a one-thread run can be put on the core it ran on. Per configuration and core:
how many runs, their values against the median of the configuration, and the share of the busy
time that the busiest core has. A low share says other cores worked too (a browser's helper
threads), and the core of such a run is the busiest one, not the only one.
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

COLUMNS = (*CONFIGURATION_COLUMNS, "cpu", "runs", "median_over_configuration", "max_over_configuration", "median_busy_share")
ONE_THREAD = 1


def table_rows(campaign: LoadedCampaign) -> list[list[CsvCell]]:
    by_core: dict[Configuration, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    shares: dict[tuple[Configuration, int], list[float]] = defaultdict(list)
    summaries = [*campaign.summaries(), *campaign.sequential_summaries()]
    for run in summaries:
        context = run_context(campaign.directory, run.run)
        cpu, share = context.busiest_cpu, context.busiest_share
        if run.configuration.threads == ONE_THREAD and cpu is not None and share is not None:
            by_core[run.configuration][cpu].append(run.value)
            shares[(run.configuration, cpu)].append(share)
    rows: list[list[CsvCell]] = []
    for configuration, cores in sorted(by_core.items()):
        centre = statistics.median(value for values in cores.values() for value in values)
        for cpu, values in sorted(cores.items()):
            share = statistics.median(shares[(configuration, cpu)])
            rows.append([*configuration.cells(), cpu, len(values), f"{statistics.median(values) / centre:.4f}", f"{max(values) / centre:.4f}", f"{share:.3f}"])
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
