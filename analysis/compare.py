"""Compare two pilots configuration by configuration.

Usage: python3 -m analysis.compare <baseline dir>... --against <treatment dir>...
For every configuration present in both, the ratio treatment / baseline of
the geometric means of the per-run medians, its 95 % percentile bootstrap
interval (runs resampled within each side) and Cliff's delta over runs
(positive: treatment slower).
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from statistics import geometric_mean

from analysis.configuration import Configuration
from analysis.runs import run_summaries
from analysis.stats.cliff import cliffs_delta
from analysis.stats.ratio import ratio_of_geometric_means
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import collect

NS_PER_MS = 1e6
HEADER = "configuration | runs | baseline ms | treatment ms | ratio [95 % CI] | Cliff's delta"


def pooled_values(directories: list[Path]) -> dict[Configuration, list[float]]:
    found: defaultdict[Configuration, list[float]] = defaultdict(list)
    for directory in directories:
        for run in run_summaries(collect(directory).rows, RUN_SUMMARY):
            found[run.configuration].append(run.value)
    return found


def comparison_line(configuration: Configuration, before: list[float], after: list[float]) -> str:
    ratio = ratio_of_geometric_means(before, after)
    low, high = ratio.interval
    return (
        f"{configuration.label} | {len(before)}/{len(after)} | {geometric_mean(before) / NS_PER_MS:.2f} | "
        f"{geometric_mean(after) / NS_PER_MS:.2f} | {ratio.value:.3f} [{low:.3f}, {high:.3f}] | {cliffs_delta(before, after):+.2f}"
    )


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path, nargs="+")
    parser.add_argument("--against", type=Path, nargs="+", required=True)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    baseline, treatment = pooled_values(args.baseline), pooled_values(args.against)
    print(HEADER)
    for configuration in sorted(set(baseline) & set(treatment)):
        print(comparison_line(configuration, baseline[configuration], treatment[configuration]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
