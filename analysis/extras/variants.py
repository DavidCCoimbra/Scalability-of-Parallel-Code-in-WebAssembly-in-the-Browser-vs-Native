"""Scaling of a campaign whose runs differ in a setting the configuration does not name.

Usage: python3 -m analysis.extras.variants data/raw/<campaign> --by engine-arm|grain --output TABLE.csv
The tier campaign crosses every browser cell with engine arms; the grain-by-threads campaign
crosses its cell with task sizes. Each (configuration, variant) gets the centre of its run
values, and its speedup and efficiency against the same variant at one thread, with 95 %
bootstrap intervals, plus how the first warm-up iteration compares with the run value.
"""

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from analysis.configuration import Configuration, CsvCell, configuration_of
from analysis.loading import InvalidCampaign, LoadedCampaign, add_exclusion_arguments, exclusion_rule, load_campaign
from analysis.run_context import RunContext, run_context
from analysis.runs import MEASURED
from analysis.scaling.output import CONFIGURATION_COLUMNS
from analysis.scaling.table import speedup_of
from analysis.stats.summary import CONFIGURATION_CENTER, RUN_SUMMARY

WARMUP = "warmup"
# A native run has no engine arm, and a run without a grain uses Rayon's adaptive split.
NO_ARM = "-"
ADAPTIVE = "adaptive"
VARIANTS: dict[str, Callable[[RunContext], str]] = {
    "engine-arm": lambda context: context.engine_arm or NO_ARM,
    "grain": lambda context: ADAPTIVE if context.grain is None else str(context.grain),
}
COLUMNS = (
    *CONFIGURATION_COLUMNS,
    "variant",
    "runs",
    "center_ns",
    "speedup",
    "speedup_low",
    "speedup_high",
    "efficiency",
    "efficiency_low",
    "efficiency_high",
    "first_warmup_over_value",
)
SIGNIFICANT_DIGITS = 4


@dataclass(frozen=True)
class VariantRun:
    configuration: Configuration
    variant: str
    value: float
    # The first warm-up iteration over the run value: under 1 when a run starts in faster code
    # than it settles in. None for a run without warm-up.
    first_warmup_over_value: float | None


def variant_runs(campaign: LoadedCampaign, variant_of: Callable[[RunContext], str]) -> list[VariantRun]:
    measured: dict[str, list[float]] = defaultdict(list)
    first_warmup: dict[str, float] = {}
    configurations: dict[str, Configuration] = {}
    for row in campaign.rows:
        configurations[row["run"]] = configuration_of(row)
        if row["phase"] == MEASURED:
            measured[row["run"]].append(float(row["ns"]))
        elif row["phase"] == WARMUP and row["iter"] == "0":
            first_warmup[row["run"]] = float(row["ns"])
    runs = []
    for run, times in measured.items():
        value = RUN_SUMMARY.of(times)
        first = first_warmup.get(run)
        runs.append(VariantRun(configurations[run], variant_of(run_context(campaign.directory, run)), value, None if first is None else first / value))
    return runs


def number(value: float) -> str:
    return f"{value:.{SIGNIFICANT_DIGITS}g}"


def table_rows(runs: list[VariantRun]) -> list[list[CsvCell]]:
    cells: dict[tuple[Configuration, str], list[VariantRun]] = defaultdict(list)
    for run in runs:
        cells[(run.configuration, run.variant)].append(run)
    rows: list[list[CsvCell]] = []
    for (configuration, variant), cell in sorted(cells.items()):
        values = [run.value for run in cell]
        baseline = [run.value for run in cells.get((configuration.baseline(), variant), [])]
        scaling = [""] * 6
        if baseline:
            speedup = speedup_of(baseline, values, CONFIGURATION_CENTER)
            efficiency = speedup.efficiency(configuration.threads)
            scaling = [number(value) for value in (speedup.value, *speedup.interval, efficiency.value, *efficiency.interval)]
        firsts = [run.first_warmup_over_value for run in cell if run.first_warmup_over_value is not None]
        rows.append(
            [
                *configuration.cells(),
                variant,
                len(values),
                f"{CONFIGURATION_CENTER.of(values):.0f}",
                *scaling,
                number(statistics.median(firsts)) if firsts else "",
            ]
        )
    return rows


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--by", choices=sorted(VARIANTS), required=True)
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
        writer.writerows(table_rows(variant_runs(campaign, VARIANTS[args.by])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
