"""Mann-Whitney U and Cliff's delta on the 10 primary contrasts of the
analysis plan, as a robustness check of the bootstrap (lecture default for
timing data). Per run: log(T1 / TN) for RQ1, log(T atomic / T local) for
RQ2, the two cells paired by repetition index; the browser's per-run values
are compared with native's, unpaired, and the 10 p-values are Holm-adjusted.

Usage: python3 -m analysis.robustness data/raw/<campaign> --output r.csv
       --max-threads N [--strict] [--foreign-cpu-threshold SECONDS]
"""

import argparse
import sys
from pathlib import Path

from analysis.inference.exclusion import excluded_runs
from analysis.inference.family import IncompleteFamily
from analysis.inference.output import write_robustness
from analysis.inference.robustness import robustness_checks
from analysis.quality.foreign_cpu import FOREIGN_CPU_THRESHOLD
from analysis.runs import run_summaries
from analysis.stats.bootstrap import BOOTSTRAP_RESAMPLES
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import collect


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-threads", type=int, required=True)
    parser.add_argument("--foreign-cpu-threshold", type=float, default=FOREIGN_CPU_THRESHOLD)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--resamples", type=int, default=BOOTSTRAP_RESAMPLES)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    collection = collect(args.directory)
    if collection.checksum_conflicts:
        print(f"error: checksums differ, no results written: {collection.checksum_conflicts}", file=sys.stderr)
        return 1
    run_ids = {str(row["run"]) for row in collection.rows}
    dropped = excluded_runs(args.directory, run_ids, args.foreign_cpu_threshold, args.strict).dropped
    summaries = run_summaries([row for row in collection.rows if row["run"] not in dropped], RUN_SUMMARY)
    try:
        checks = robustness_checks(summaries, max_threads=args.max_threads, resamples=args.resamples)
    except IncompleteFamily as family:
        print(f"error: {family}", file=sys.stderr)
        return 1
    with args.output.open("w") as file:
        write_robustness(checks, file)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
