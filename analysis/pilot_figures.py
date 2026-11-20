"""Figures of the pilot report: speedup of four workloads and the absolute
browser / native ratio of the filter and the atomic histogram at k = 256.

Usage: uv run --no-project --with matplotlib python -m analysis.pilot_figures
       data/raw/<campaign> --output paper/figures
Writes pilot-scaling.pdf (labels in Portuguese) and pilot-scaling-en.pdf
(English): speedup in the first two rows, absolute ratio in the last.
"""

import argparse
import sys
from pathlib import Path

from analysis.figures.pilot import ENGLISH, PORTUGUESE, pilot_figure
from analysis.figures.points import absolute_ratios, scaling_curves
from analysis.runs import run_summaries
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import collect


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    runs = run_summaries(collect(args.directory).rows, RUN_SUMMARY)
    args.output.mkdir(parents=True, exist_ok=True)
    curves, ratios = scaling_curves(runs), absolute_ratios(runs)
    for labels in (PORTUGUESE, ENGLISH):
        pilot_figure(curves, ratios, labels, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
