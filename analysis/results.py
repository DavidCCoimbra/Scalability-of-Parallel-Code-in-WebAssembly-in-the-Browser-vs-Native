"""Inference from the analysis plan: RQ1 and RQ2
contrasts with bootstrap intervals, bootstrap p-values and Holm over the
primary family, plus the shape of the run distributions.

Usage: python3 -m analysis.results data/raw/<campaign> --contrasts c.csv
       --max-threads N [--partial] [--shape shape.csv]
       [--foreign-cpu-threshold SECONDS] [--strict]
       [--summary median|mean] [--center geometric|median]
"""

import argparse
import json
import sys
from pathlib import Path

from analysis.inference.estimation import contrasts
from analysis.inference.exclusion import excluded_runs
from analysis.inference.family import IncompleteFamily
from analysis.inference.cells import missing_absolute
from analysis.inference.output import write_contrasts, write_shape
from analysis.inference.shape import shape_table
from analysis.inference.sidecar import ResultsOptions, ResultsOutcome, results_sidecar
from analysis.quality.clock import report_clock_warnings
from analysis.quality.foreign_cpu import FOREIGN_CPU_THRESHOLD
from analysis.runs import run_summaries
from analysis.stats.bootstrap import BOOTSTRAP_RESAMPLES
from analysis.stats.summary import CONFIGURATION_CENTER, RUN_SUMMARY, Summary
from harness.collect import collect


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--contrasts", type=Path, required=True)
    parser.add_argument("--shape", type=Path)
    parser.add_argument("--foreign-cpu-threshold", type=float, default=FOREIGN_CPU_THRESHOLD)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--summary", choices=[Summary.MEDIAN.value, Summary.MEAN.value], default=RUN_SUMMARY.value)
    parser.add_argument("--center", choices=[Summary.GEOMETRIC.value, Summary.MEDIAN.value], default=CONFIGURATION_CENTER.value)
    parser.add_argument("--resamples", type=int, default=BOOTSTRAP_RESAMPLES)
    parser.add_argument("--max-threads", type=int, required=True)
    parser.add_argument("--partial", action="store_true")
    return parser


def parse_options(argv: list[str]) -> ResultsOptions:
    args = parser().parse_args(argv)
    return ResultsOptions(
        directory=args.directory,
        contrasts=args.contrasts,
        shape=args.shape,
        foreign_cpu_threshold=args.foreign_cpu_threshold,
        strict=args.strict,
        summary=args.summary,
        center=args.center,
        resamples=args.resamples,
        max_threads=args.max_threads,
        partial=args.partial,
    )


def error(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    options = parse_options(argv)
    collection = collect(options.directory)
    if collection.checksum_conflicts:
        return error(f"checksums differ, no results written: {collection.checksum_conflicts}")
    run_ids = {str(row["run"]) for row in collection.rows}
    exclusions = excluded_runs(options.directory, run_ids, options.foreign_cpu_threshold, options.strict)
    dropped = exclusions.dropped
    summaries = run_summaries([row for row in collection.rows if row["run"] not in dropped], Summary(options.summary))
    try:
        results = contrasts(
            summaries, Summary(options.center), max_threads=options.max_threads, partial=options.partial, resamples=options.resamples
        )
    except IncompleteFamily as family:
        return error(str(family))

    with options.contrasts.open("w") as file:
        write_contrasts(results, file)
    if options.shape:
        with options.shape.open("w") as file:
            write_shape(shape_table(summaries), file)
    clock = report_clock_warnings(options.directory, summaries, sys.stderr)
    missing = missing_absolute(summaries, options.max_threads)
    for configuration in missing:
        print(f"warning: no native counterpart for the absolute ratio of {configuration}", file=sys.stderr)
    sidecar = results_sidecar(options, ResultsOutcome(collection, exclusions, results, clock, missing))
    options.contrasts.with_suffix(".json").write_text(json.dumps(sidecar, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
