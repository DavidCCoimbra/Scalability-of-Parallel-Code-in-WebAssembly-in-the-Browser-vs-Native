"""Mann-Whitney U and Cliff's delta on the 10 primary contrasts of the
analysis plan, as a robustness check of the bootstrap (the rank test commonly
used for timing data). Per run: log(T1 / TN) for RQ1, log(T atomic / T local) for
RQ2, the two cells paired by repetition index; the browser's per-run values
are compared with native's, unpaired, and the 10 p-values are Holm-adjusted.

Usage: python3 -m analysis.robustness data/raw/<campaign> --output r.csv
       --max-threads N [--strict] [--foreign-cpu-threshold SECONDS]
"""

import argparse
import sys
from pathlib import Path

from analysis.inference.family import IncompleteFamily
from analysis.inference.output import write_robustness
from analysis.inference.robustness import robustness_checks
from analysis.loading import InvalidCampaign, add_exclusion_arguments, exclusion_rule, load_campaign
from analysis.stats.bootstrap import BOOTSTRAP_RESAMPLES


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-threads", type=int, required=True)
    add_exclusion_arguments(parser)
    parser.add_argument("--resamples", type=int, default=BOOTSTRAP_RESAMPLES)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        summaries = load_campaign(args.directory, exclusion_rule(args)).summaries()
        checks = robustness_checks(summaries, max_threads=args.max_threads, resamples=args.resamples)
    except (InvalidCampaign, IncompleteFamily) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    with args.output.open("w") as file:
        write_robustness(checks, file)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
