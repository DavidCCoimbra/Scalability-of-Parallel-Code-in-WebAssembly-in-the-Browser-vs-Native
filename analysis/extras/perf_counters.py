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
       [--foreign-cpu-threshold SECONDS | --no-foreign-cpu-threshold] [--strict]
The campaign is read like any other (analysis.loading): a checksum conflict stops it and the
plan's exclusions apply. The summary has the arithmetic mean per configuration with a 95 %
percentile bootstrap interval over runs. The retries table has, per environment and k, the
locked loads per operation at the largest N minus those at N = 1.
"""

import argparse
import sys
from pathlib import Path

from analysis.campaign import campaign_spec
from analysis.configuration import Configuration, configuration_of
from analysis.extras.perf.intervals import read_intervals
from analysis.extras.perf.run_counters import counters_of, runs_of
from analysis.extras.perf.tables import short_cells, write_retries, write_runs, write_summary
from analysis.loading import InvalidCampaign, LoadedCampaign, add_exclusion_arguments, exclusion_rule, load_campaign

COUNTERS_DIRECTORY = "counters"


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--retries", type=Path)
    add_exclusion_arguments(parser)
    return parser


def completed_configurations(campaign: LoadedCampaign) -> list[Configuration]:
    return list({row["run"]: configuration_of(row) for row in campaign.collection.rows}.values())


def problem(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        campaign = load_campaign(args.raw, exclusion_rule(args))
        runs = runs_of(campaign)
    except InvalidCampaign as invalid:
        return problem(str(invalid))
    campaign.report_gaps()
    intervals = read_intervals(args.raw / COUNTERS_DIRECTORY)
    rows = [counters_of(run, intervals) for run in runs]
    empty = [row.run.run_id for row in rows if row.intervals == 0]
    if empty:
        return problem(f"runs with no counter interval: {empty}")
    repetitions = campaign_spec(args.raw).get("repetitions")
    short = short_cells(completed_configurations(campaign), repetitions) if isinstance(repetitions, int) else []
    if short:
        return problem(f"configurations with fewer than {repetitions} runs: {short}")
    args.runs.parent.mkdir(parents=True, exist_ok=True)
    write_runs(rows, args.runs)
    write_summary(rows, args.summary)
    if args.retries is not None:
        write_retries(rows, args.retries)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
