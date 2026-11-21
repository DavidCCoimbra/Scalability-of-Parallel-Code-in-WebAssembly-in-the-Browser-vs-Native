"""Analysis v0: one value per run, then speedup T1/TN and efficiency per
environment with bootstrap intervals over runs.

Usage: python3 -m analysis.v0 data/raw/<campaign> [--summary median|mean]
       [--center geometric|median|mean] [--weak] [--output scaling.csv]
       [--foreign-cpu-threshold SECONDS | --no-foreign-cpu-threshold] [--strict]
With --weak, T1/TN is written as the weak-scaling efficiency and the
speedup / N columns, meaningless for weak scaling, are left out.
A checksum conflict stops it without a table. The plan's exclusions are
applied as in analysis.results; excluded, failed and missing runs are
reported and, with --output, recorded in scaling.json with the options
and commit.
"""

import argparse
import json
import sys
from pathlib import Path

from analysis.loading import InvalidCampaign, add_exclusion_arguments, exclusion_rule
from analysis.scaling.output import Scaling, write_scaling
from analysis.scaling.report import ScalingOptions, ScalingReport, analyse, scaling_sidecar
from analysis.stats.summary import CONFIGURATION_CENTER, RUN_SUMMARY, Summary


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--summary", choices=[Summary.MEDIAN.value, Summary.MEAN.value], default=RUN_SUMMARY.value)
    parser.add_argument("--center", choices=[item.value for item in Summary], default=CONFIGURATION_CENTER.value)
    parser.add_argument("--weak", action="store_true")
    parser.add_argument("--output", type=Path)
    add_exclusion_arguments(parser)
    return parser


def write_outputs(report: ScalingReport, options: ScalingOptions, output: Path | None) -> None:
    if output is None:
        write_scaling(report.rows, sys.stdout, options.scaling)
        return
    with output.open("w") as file:
        write_scaling(report.rows, file, options.scaling)
    output.with_suffix(".json").write_text(json.dumps(scaling_sidecar(options, report), indent=2) + "\n")


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    scaling = Scaling.WEAK if args.weak else Scaling.STRONG
    options = ScalingOptions(args.directory, args.summary, args.center, scaling, exclusion_rule(args))
    try:
        report = analyse(options.directory, Summary(options.summary), Summary(options.center), options.rule)
    except InvalidCampaign as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    write_outputs(report, options, args.output)
    report.campaign.report_gaps()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
