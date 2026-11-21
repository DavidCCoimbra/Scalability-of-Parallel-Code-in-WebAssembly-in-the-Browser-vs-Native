"""Throughput and absolute speedup per configuration (post hoc, descriptive).

Usage: python3 -m analysis.throughput data/raw/<campaign> --output throughput.csv
       [--foreign-cpu-threshold SECONDS | --no-foreign-cpu-threshold] [--strict]
Per configuration: the geometric centre of the per-run medians as nanoseconds per pixel
and megapixels per second, and the absolute speedup T(native, 1) / T(environment, N)
with its 95 % bootstrap interval. A configuration measured on images of more than one
size stops it.
"""

import argparse
import sys
from pathlib import Path

from analysis.configuration import Configuration, configuration_of
from analysis.loading import InvalidCampaign, LoadedCampaign, add_exclusion_arguments, exclusion_rule, load_campaign
from analysis.scaling.throughput import throughput_table, write_throughput


def pixels_by_configuration(campaign: LoadedCampaign) -> dict[Configuration, int]:
    sizes: dict[Configuration, set[int]] = {}
    for row in campaign.rows:
        sizes.setdefault(configuration_of(row), set()).add(int(row["width"]) * int(row["height"]))
    mixed = sorted(configuration.label for configuration, pixels in sizes.items() if len(pixels) > 1)
    if mixed:
        raise InvalidCampaign(f"{campaign.directory}: more than one image size in {', '.join(mixed)}")
    return {configuration: next(iter(pixels)) for configuration, pixels in sizes.items()}


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    add_exclusion_arguments(parser)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        campaign = load_campaign(args.directory, exclusion_rule(args))
        rows = throughput_table(campaign.summaries(), pixels_by_configuration(campaign))
    except InvalidCampaign as invalid:
        print(f"error: {invalid}", file=sys.stderr)
        return 1
    with args.output.open("w") as file:
        write_throughput(rows, file)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
