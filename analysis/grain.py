"""U-curves of the grain sweep campaigns.

Usage: uv run --no-project --with matplotlib python -m analysis.grain
       data/raw/grain-1024-v2 data/raw/grain-8192-v2
       --points data/tables/grain-v2/grain-points.csv
       --best data/tables/grain-v2/grain-best.csv
       [--figure paper/figures/grain-ucurve.pdf] [--paper-figure paper/figures/grain-ucurve-8192.pdf]
Each directory is one image size, its own randomized campaign. A run's grain
(rows per task for the filter, KB for the histograms, none for Rayon's
adaptive split) is read from its context JSON. The points are, per
environment, workload, size and grain, the geometric mean of the run medians
of the time per pass with a 95 % bootstrap interval. The best table gives the
fastest fixed grain, the flat region around it, the adaptive split against
it, and the grain the common 100:1 rule asks for given the fork-join cost
measured by the runs' calibration.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from analysis.campaign import campaign_metadata
from analysis.cutoff import InvalidCutoffCampaign, load_runs, square_side, write_csv
from analysis.loading import ExclusionRule, InvalidCampaign, add_exclusion_arguments, exclusion_rule
from analysis.quality.clock import report_clock_warnings
from analysis.run_context import run_context
from analysis.scaling.fork_join import fork_join_costs
from analysis.scaling.grain import BEST_COLUMNS, POINT_COLUMNS, GrainPoint, best_grains, best_rows, grain_points, point_rows
from harness.collect import Row

# The paper's U-curve figure shows the main campaign's image size only.
PAPER_SIDES = (8192,)


# The sweep's campaigns are never pooled with campaigns of another build, the main campaign's
# included.
def same_build(directories: Sequence[Path]) -> None:
    recorded = [(campaign_metadata(directory) or {}).get("build") for directory in directories]
    unknown = [str(directory) for directory, build in zip(directories, recorded) if build is None]
    if unknown:
        raise InvalidCutoffCampaign(f"no build recorded for: {', '.join(unknown)}")
    builds = {str(build) for build in recorded}
    if len(builds) != 1:
        raise InvalidCutoffCampaign(f"the grain campaigns come from different builds: {sorted(builds)}")


def grain_campaign(directory: Path, rule: ExclusionRule = ExclusionRule()) -> tuple[list[GrainPoint], list[Row]]:
    # Checksums are compared per configuration across grains too: every grain computes the same output.
    campaign = load_runs(directory, rule)
    summaries = campaign.summaries()
    report_clock_warnings(directory, summaries, sys.stderr)
    grains = {run.run: run_context(directory, run.run).grain for run in summaries}
    return grain_points(summaries, square_side(campaign.rows, directory), grains), campaign.rows


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--points", type=Path, required=True)
    parser.add_argument("--best", type=Path, required=True)
    parser.add_argument("--figure", type=Path)
    parser.add_argument("--paper-figure", type=Path, help="the U-curve at the main campaign's size alone")
    add_exclusion_arguments(parser)
    return parser


def main(argv: Sequence[str]) -> int:
    args = parser().parse_args(argv)
    points: list[GrainPoint] = []
    rows: list[Row] = []
    try:
        same_build(args.directories)
        for directory in args.directories:
            campaign_points, campaign_rows = grain_campaign(directory, exclusion_rule(args))
            points += campaign_points
            rows += campaign_rows
    except InvalidCampaign as error:
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
