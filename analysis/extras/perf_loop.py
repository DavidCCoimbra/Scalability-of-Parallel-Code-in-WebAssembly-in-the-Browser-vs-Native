"""Counters per pixel of the loop alone, from two counter campaigns that differ only in passes.

Usage: python3 -m analysis.extras.perf_loop data/raw/perf-loop1-<build> data/raw/perf-loop8-<build>
       --output data/tables/perf-loop-<build>/perf-loop-<build>-counters.csv [--rises RISES.csv]
A run of the second campaign does more passes of every timed sample and nothing else, so the
difference of the mean counts, over the difference of the pixels, leaves out the start of the
process or browser, the input and the checksums. The interval is a 95 % percentile bootstrap
over the runs of both campaigns. --rises also writes each counter at N threads over the same
counter at one thread.
"""

import argparse
import sys
from pathlib import Path

from analysis.extras.perf.intervals import counters_in, read_intervals
from analysis.extras.perf.loop import loop_counters, write_loop_counters, write_rises
from analysis.extras.perf.run_counters import RunCounters, counters_of, runs_of
from analysis.extras.perf_counters import COUNTERS_DIRECTORY
from analysis.loading import InvalidCampaign, add_exclusion_arguments, exclusion_rule, load_campaign


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("few", type=Path)
    parser.add_argument("many", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rises", type=Path)
    add_exclusion_arguments(parser)
    return parser


def run_counters(raw: Path, args: argparse.Namespace) -> list[RunCounters]:
    campaign = load_campaign(raw, exclusion_rule(args))
    campaign.report_gaps()
    intervals = read_intervals(raw / COUNTERS_DIRECTORY)
    names = counters_in(intervals)
    rows = [counters_of(run, intervals, names) for run in runs_of(campaign)]
    empty = [row.run.run_id for row in rows if row.intervals == 0]
    if empty:
        raise InvalidCampaign(f"{raw}: runs with no counter interval: {empty}")
    return rows


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        few, many = run_counters(args.few, args), run_counters(args.many, args)
        table = loop_counters(few, many)
    except (InvalidCampaign, ValueError) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_loop_counters(table, args.output)
    if args.rises is not None:
        write_rises(few, many, args.rises)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
