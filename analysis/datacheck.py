"""Data quality report of a campaign before any analysis.

Usage: python3 -m analysis.datacheck data/raw/<campaign> [--output report.md]
Counts planned, done, missing and failed runs, checksum conflicts, runs
that fail strict validation (by reason), runs above the foreign CPU
threshold, clock warnings, and the configurations whose run
values trend with the execution order (Spearman's rho, |rho| above the
limit with at least the minimum runs). Nothing is removed here: the
exclusions are the analysis plan's (D7).
"""

import argparse
import sys
from pathlib import Path

from analysis.quality.report import quality_report


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    report = quality_report(args.directory)
    text = report.text()
    print(text)
    if args.output:
        args.output.write_text(text)
    return 1 if report.blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
