"""Distribution of the run values of a campaign: one violin per environment
for the filter at N = 1 and N = 8 and the atomic histogram at k = 1 and
k = 256, N = 8, with the median and the interquartile range of the 30
per-run medians and every run as a dot.

Usage: uv run --no-project --with matplotlib python -m analysis.distributions
       data/raw/<campaign> --figure paper/figures/<campaign>-distributions.pdf
       [--table data/tables/<campaign>/<campaign>-distributions.csv]
       [--foreign-cpu-threshold SECONDS | --no-foreign-cpu-threshold] [--strict]
The table gives, per panel and environment, the quartiles, extremes and
the spread relative to the median that the figure shows.
"""

import argparse
import sys
from pathlib import Path

from analysis.figures.spread import CAMPAIGN_PANELS, panel_spreads, write_spreads
from analysis.loading import InvalidCampaign, add_exclusion_arguments, exclusion_rule, load_campaign


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--figure", type=Path, required=True)
    parser.add_argument("--table", type=Path)
    add_exclusion_arguments(parser)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        runs = load_campaign(args.directory, exclusion_rule(args)).summaries()
    except InvalidCampaign as invalid:
        print(f"error: {invalid}", file=sys.stderr)
        return 1
    panels = [(panel, panel_spreads(panel, runs)) for panel in CAMPAIGN_PANELS]
    if args.table is not None:
        with args.table.open("w") as file:
            write_spreads(panels, file)
    # Imported here so that the table, and the tests, run without matplotlib installed.
    from analysis.figures.distributions import distributions_figure

    distributions_figure(panels, args.figure)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
