"""U-curves of the grain sweep campaigns.

Usage: uv run --no-project --with matplotlib python -m analysis.grain
       data/raw/grain-1024-v2 data/raw/grain-8192-v2
       --points data/tables/grain-v2/grain-points.csv
       --best data/tables/grain-v2/grain-best.csv
       [--figure paper/figures/grain-ucurve.pdf] [--paper-figure paper/figures/grain-ucurve-8192.pdf]
Each directory is one image size, its own randomized campaign. A run's grain
(rows per task for the filter, KB for the local histogram, none for Rayon's
adaptive split) is read from its context JSON. The points are, per
environment, workload, size and grain, the geometric mean of the run medians
of the time per pass with a 95 % bootstrap interval. The best table gives the
fastest fixed grain, the flat region around it, the adaptive split against
it, and the grain the lecture's 100:1 rule asks for given the fork-join cost
measured by the runs' calibration.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from analysis.campaign import campaign_metadata, run_context
from analysis.cutoff import InvalidCutoffCampaign, square_side, write_csv
from analysis.quality.clock import report_clock_warnings
from analysis.runs import Row, run_summaries
from analysis.scaling.fork_join import fork_join_costs
from analysis.scaling.grain import BEST_COLUMNS, POINT_COLUMNS, GrainPoint, best_grains, best_rows, grain_points, point_rows
from analysis.scaling.report import conflict_details
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import collect

GRAIN_KEY = "grain"


# The sweep's campaigns are never pooled with campaigns of another build, the main campaign's
# included.
# The paper's U-curve figure shows the main campaign's image size only.
PAPER_SIDES = (8192,)


def same_build(directories: Sequence[Path]) -> None:
    builds = {str((campaign_metadata(directory) or {}).get("build")) for directory in directories}
    if len(builds) != 1:
        raise InvalidCutoffCampaign(f"the grain campaigns come from different builds: {sorted(builds)}")


def run_grain(directory: Path, run_id: str) -> int | None:
    grain = run_context(directory, run_id).get(GRAIN_KEY)
    return grain if isinstance(grain, int) and not isinstance(grain, bool) else None


def grain_campaign(directory: Path) -> tuple[list[GrainPoint], list[Row]]:
    collection = collect(directory)
    # Checksums are compared per configuration across grains too: every grain computes the same output.
    if collection.checksum_conflicts:
        raise InvalidCutoffCampaign(f"{directory}: checksums differ: {conflict_details(collection.checksum_conflicts)}")
    if not collection.rows:
        raise InvalidCutoffCampaign(f"{directory}: no completed runs")
    for environment, count in sorted(collection.failed.items()):
        print(f"{directory}: failed runs in {environment}: {count} (excluded)", file=sys.stderr)
    summaries = run_summaries(collection.rows, RUN_SUMMARY)
    report_clock_warnings(directory, summaries, sys.stderr)
    grains = {run.run: run_grain(directory, run.run) for run in summaries}
    return grain_points(summaries, square_side(collection.rows, directory), grains), collection.rows


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--points", type=Path, required=True)
    parser.add_argument("--best", type=Path, required=True)
    parser.add_argument("--figure", type=Path)
    parser.add_argument("--paper-figure", type=Path, help="the U-curve at the main campaign's size alone")
    return parser


def main(argv: Sequence[str]) -> int:
    args = parser().parse_args(argv)
    points: list[GrainPoint] = []
    rows: list[Row] = []
    try:
        same_build(args.directories)
        for directory in args.directories:
            campaign_points, campaign_rows = grain_campaign(directory)
            points += campaign_points
            rows += campaign_rows
    except InvalidCutoffCampaign as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    write_csv(point_rows(points), POINT_COLUMNS, args.points)
    write_csv(best_rows(best_grains(points, fork_join_costs(rows))), BEST_COLUMNS, args.best)
    if args.figure is not None:
        # Imported here so that the tables, and the tests, run without matplotlib installed.
        from analysis.figures.grain import plot

        plot(points, args.figure)
    if args.paper_figure is not None:
        from analysis.figures.grain import plot

        plot(points, args.paper_figure, PAPER_SIDES)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
