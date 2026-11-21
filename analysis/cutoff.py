"""Empirical sequential cutoff of the cutoff campaigns.

Usage: uv run --no-project --with matplotlib python -m analysis.cutoff
       data/raw/cutoff-512-v2 data/raw/cutoff-1024-v2 ... data/raw/cutoff-8192-v2
       --table data/tables/cutoff-v2/cutoff-table.csv --estimates data/tables/cutoff-v2/cutoff-estimates.csv
       --model data/tables/cutoff-v2/cutoff-model.csv [--figure paper/figures/cutoff-speedup.pdf]
Each directory is one image size, its own randomized campaign; sizes are
compared only through speedups within a size. The table has, per
environment, workload, N and size, T1 and TN (time per pass), the speedup
with its 95 % bootstrap interval and the work per region (T1 per pass).
The estimates are, per environment, workload and N, the break-even size
(speedup 1) and the worth-it size (efficiency 0.5), interpolated on log
size. The model predicts, from the fork-join cost measured at N = 8, the
work at which the fork-join is 1 % of TN (the common 100:1 rule), with 5 % as a
secondary reading.
"""

import argparse
import csv
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from analysis.quality.clock import report_clock_warnings
from analysis.runs import Row, run_summaries
from analysis.scaling.crossing import ESTIMATE_COLUMNS, estimate_rows, estimates
from analysis.scaling.cutoff import TABLE_COLUMNS, CutoffPoint, cutoff_points, table_rows
from analysis.scaling.fork_join import MODEL_COLUMNS, fork_join_costs, model_rows, predictions
from analysis.scaling.report import conflict_details
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import collect


class InvalidCutoffCampaign(ValueError):
    pass


@dataclass(frozen=True)
class SizeCampaign:
    side: int
    points: list[CutoffPoint]
    rows: list[Row]


def square_side(rows: Sequence[Row], directory: Path) -> int:
    shapes = {(int(row["width"]), int(row["height"])) for row in rows}
    if len(shapes) != 1:
        raise InvalidCutoffCampaign(f"{directory}: expected one image size, found {sorted(shapes)}")
    ((width, height),) = shapes
    if width != height:
        raise InvalidCutoffCampaign(f"{directory}: expected a square image, found {width}x{height}")
    return width


def size_campaign(directory: Path) -> SizeCampaign:
    collection = collect(directory)
    if collection.checksum_conflicts:
        raise InvalidCutoffCampaign(f"{directory}: checksums differ: {conflict_details(collection.checksum_conflicts)}")
    if not collection.rows:
        raise InvalidCutoffCampaign(f"{directory}: no completed runs")
    for environment, count in sorted(collection.failed.items()):
        print(f"{directory}: failed runs in {environment}: {count} (excluded)", file=sys.stderr)
    for run in collection.missing:
        print(f"{directory}: planned run without any file: {run}", file=sys.stderr)
    summaries = run_summaries(collection.rows, RUN_SUMMARY)
    report_clock_warnings(directory, summaries, sys.stderr)
    side = square_side(collection.rows, directory)
    return SizeCampaign(side, cutoff_points(side, summaries), collection.rows)


def size_campaigns(directories: Sequence[Path]) -> list[SizeCampaign]:
    campaigns = [size_campaign(directory) for directory in directories]
    sides = [campaign.side for campaign in campaigns]
    if len(set(sides)) != len(sides):
        raise InvalidCutoffCampaign(f"two campaigns have the same image side: {sorted(sides)}")
    return sorted(campaigns, key=lambda campaign: campaign.side)


def write_csv(rows: list[dict[str, Any]], columns: Sequence[str], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--estimates", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--figure", type=Path)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        campaigns = size_campaigns(args.directories)
    except InvalidCutoffCampaign as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    points = [point for campaign in campaigns for point in campaign.points]
    costs = fork_join_costs(row for campaign in campaigns for row in campaign.rows)
    write_csv(table_rows(points), TABLE_COLUMNS, args.table)
    write_csv(estimate_rows(estimates(points)), ESTIMATE_COLUMNS, args.estimates)
    write_csv(model_rows(predictions(points, costs)), MODEL_COLUMNS, args.model)
    if args.figure is not None:
        # Imported here so that the tables, and the tests, run without matplotlib installed.
        from analysis.figures.cutoff import plot

        plot(points, args.figure)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
