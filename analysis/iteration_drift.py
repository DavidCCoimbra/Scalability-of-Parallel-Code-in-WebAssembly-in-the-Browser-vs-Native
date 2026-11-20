"""Drift inside runs: the median of the first measured iterations over the
median of the last ones, pooled over the runs of each configuration.

Usage: python3 -m analysis.iteration_drift data/raw/<campaign> [--window 3]
       [--output drift.csv]
A ratio near 1 means the measured iterations do not trend, so the warm-up
was long enough; it cannot see a level shift that lasts every iteration.
"""

import argparse
import sys
from pathlib import Path

from analysis.quality.iteration_drift import DEFAULT_WINDOW, drifts, write_drifts


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    rows = drifts(args.directory, args.window)
    if args.output is None:
        write_drifts(rows, sys.stdout)
        return 0
    with args.output.open("w") as file:
        write_drifts(rows, file)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
