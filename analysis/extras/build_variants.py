"""Filter scaling of the SIMD build variants against the baseline.

Usage: uv run --no-project --with matplotlib python -m analysis.extras.build_variants
       baseline=data/raw/campaign-v2 scalar=data/raw/simd-scalar-v2 avx2=data/raw/simd-avx2-v2
       --table data/tables/simd-v2/simd-v2-variants.csv --figure paper/figures/simd-efficiency.pdf
Per build, environment and N: the geometric mean of the run medians, the
efficiency with its 95 % bootstrap interval, the excess time TN - T1 / N,
the time over the same environment's baseline time and the time over the
same build's native time.
"""

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from analysis.runs import run_summaries
from analysis.scaling.build_variants import COLUMNS, VariantPoint, table_rows, variant_points
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import collect


@dataclass(frozen=True)
class Series:
    build: str
    directory: Path


def parse_series(text: str) -> Series:
    build, separator, directory = text.partition("=")
    if not separator or not build or not directory:
        raise argparse.ArgumentTypeError(f"expected build=directory, got {text!r}")
    return Series(build, Path(directory))


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("series", type=parse_series, nargs="+")
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--figure", type=Path)
    return parser


def write_table(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def series_points(series: Series) -> list[VariantPoint]:
    return variant_points(series.build, run_summaries(collect(series.directory).rows, RUN_SUMMARY))


def main(argv: list[str]) -> int:
    arguments = parser()
    args = arguments.parse_args(argv)
    builds = [series.build for series in args.series]
    if len(set(builds)) != len(builds):
        arguments.error(f"duplicate build names: {builds}")
    points = [point for series in args.series for point in series_points(series)]
    write_table(table_rows(points), args.table)
    if args.figure is not None:
        # Imported here so that the table, and the tests, run without matplotlib installed.
        from analysis.figures.build_variants import plot

        plot(points, args.figure)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
