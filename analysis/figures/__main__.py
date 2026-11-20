"""Scaling, absolute ratio and RQ2 figures of a campaign (DAV-141, DAV-148).

Usage: uv run --no-project --with matplotlib python -m analysis.figures
       data/raw/<campaign>... --output paper/figures [--prefix campaign]
Writes <prefix>-speedup.pdf, <prefix>-efficiency.pdf, <prefix>-absolute.pdf,
<prefix>-rq2.pdf (every k) and <prefix>-rq2-ends.pdf (k = 1 and 256, the paper's figure). Run values are per-run medians; centres are geometric
means; intervals are 95 % percentile bootstraps over runs.
"""

import argparse
import sys
from pathlib import Path

from analysis.figures.campaign import absolute_figure, efficiency_figure, rq2_figure, speedup_figure
from analysis.figures.points import absolute_ratios, rq2_ratios, scaling_curves
from analysis.runs import run_summaries
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import collect

# The paper's RQ2 figure shows the two ends of the contention sweep; the middle k are in its table.
PAPER_RQ2_KS = (1, 256)


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", default="campaign")
    parser.add_argument("--diagonal", default="ideal")
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    runs = [run for directory in args.directories for run in run_summaries(collect(directory).rows, RUN_SUMMARY)]
    args.output.mkdir(parents=True, exist_ok=True)
    curves = scaling_curves(runs)
    speedup_figure(curves, args.diagonal, args.output / f"{args.prefix}-speedup.pdf")
    efficiency_figure(curves, args.output / f"{args.prefix}-efficiency.pdf")
    absolute_figure(absolute_ratios(runs), args.output / f"{args.prefix}-absolute.pdf")
    ratios = rq2_ratios(runs)
    rq2_figure(ratios, args.output / f"{args.prefix}-rq2.pdf")
    rq2_figure(ratios, args.output / f"{args.prefix}-rq2-ends.pdf", PAPER_RQ2_KS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
