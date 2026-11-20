"""Runs and iterations per configuration from the pilots.

Usage: python3 -m analysis.runcount data/raw/<runs pilot>...
       [--warmup-pilot data/raw/pilot-warmup ...] [--target 0.05]
Runs: every planned primary-style contrast (RQ1 and RQ2 interactions, in
logs, geometric centre) gets the mean half-width of its Bonferroni 99.5 %
percentile bootstrap interval over random subsamples of n runs; the choice
is the smallest n, at least the plan's floor of 10, whose half-width meets
the target for every contrast; beyond the pilot's size, the runs a target
needs come from a c / sqrt(n) fit on n <= 20 (subsamples near the pilot's
size overlap with it and understate the width). Iterations: for every long run of the
warm-up pilot, the median of the first M iterations after the workload's W
is compared with the median of the iterations after those M; the choice is the
smallest M whose share of runs within each tolerance reaches the share.
"""

import argparse
import sys
from pathlib import Path

from analysis.pilot.iteration_count import (
    AGREEING_SHARE,
    ITERATION_SIZES,
    ITERATION_TOLERANCES,
    choose_iterations,
    iteration_agreement,
)
from analysis.pilot.run_count import LARGEST_FIT, RUN_FLOOR, Widths, choose_runs, contrast_widths, extrapolated_runs
from analysis.pilot.warmup import WarmupRule, campaign_warmups, load_series

# A 5 % half-width target and 20 subsamples per n (its table was made with --resamples 1000).
DEFAULT_TARGET = 0.05
DEFAULT_SUBSAMPLES = 20
DEFAULT_RESAMPLES = 2000
LABEL_WIDTH = 48


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--warmup-pilot", type=Path, nargs="*", default=[])
    parser.add_argument("--target", type=float, default=DEFAULT_TARGET)
    parser.add_argument("--subsamples", type=int, default=DEFAULT_SUBSAMPLES)
    parser.add_argument("--resamples", type=int, default=DEFAULT_RESAMPLES)
    return parser


def percent(value: float) -> str:
    return f"{100 * value:.0f} %"


def print_runs(widths: dict[str, Widths], target: float) -> None:
    for label, by_size in sorted(widths.items()):
        print(f"{label:{LABEL_WIDTH}}", "  ".join(f"n={size}: {100 * width:5.1f}%" for size, width in sorted(by_size.items())))
    print(f"runs: {choose_runs(widths, target)} (half-width <= {percent(target)} in every contrast, at least {RUN_FLOOR})")
    for label, by_size in sorted(widths.items()):
        print(
            f"{label:{LABEL_WIDTH}} runs for {percent(target)} from a c/sqrt(n) fit on n <= {LARGEST_FIT}: "
            f"{extrapolated_runs(by_size, target)}"
        )


def print_iterations(warmup_pilots: list[Path]) -> None:
    series = [run for directory in warmup_pilots for run in load_series(directory)]
    warmups = campaign_warmups(series, WarmupRule())
    for tolerance in ITERATION_TOLERANCES:
        agreement = iteration_agreement(series, warmups, list(ITERATION_SIZES), tolerance)
        shares = {size: round(share, 3) for size, share in agreement.items()}
        chosen = choose_iterations(agreement, share=AGREEING_SHARE)
        print(f"iterations within {percent(tolerance)}: {shares}, smallest with {percent(AGREEING_SHARE)} of runs: {chosen}")


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    print_runs(contrast_widths(args.directories, args.subsamples, args.resamples), args.target)
    if args.warmup_pilot:
        print_iterations(args.warmup_pilot)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
