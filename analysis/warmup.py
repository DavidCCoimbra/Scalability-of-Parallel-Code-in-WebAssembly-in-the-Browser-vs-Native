"""Warm-up W per workload from a pilot of long runs without warm-up.

Usage: python3 -m analysis.warmup data/raw/<pilot>... [--output warmup.json]
The observed W of a run is the first iteration whose next window has its
median within the tolerance of the steady state (the second half of the
run), and at least one past any iteration of the first window slower than
every steady-state iteration and than the band. The tolerance is the larger
of the band and the spread factor times the largest window deviation inside
the steady state, so noise is not read as warm-up; a steady state whose
spread exceeds max_spread, or a run with no settled window, never settles
and stops the choice. A workload's W is the margin times the largest
observed W over environments, thread counts and runs, at least the floor.
"""

import argparse
import json
import sys
from pathlib import Path

from analysis.configuration import workload_label, workload_order
from analysis.pilot.warmup import Series, WarmupRule, WorkloadKey, campaign_warmups, load_series, observed_warmup

LABEL_WIDTH = 18


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    return parser


def observed_for(series: list[Series], key: WorkloadKey, rule: WarmupRule) -> list[int | None]:
    return [observed_warmup(run.times, rule) for run in series if run.workload_key == key]


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    rule = WarmupRule()
    series = [run for directory in args.directories for run in load_series(directory)]
    warmups = campaign_warmups(series, rule)
    for key, value in sorted(warmups.items(), key=lambda item: workload_order(item[0])):
        observed = sorted(run_w for run_w in observed_for(series, key, rule) if run_w is not None)
        print(f"{workload_label(*key):{LABEL_WIDTH}} W={value:3}  observed {observed}")
    if args.output:
        rows = [{"workload": workload, "k": k, "warmup": value} for (workload, k), value in warmups.items()]
        args.output.write_text(json.dumps({"rule": rule.as_json(), "warmups": rows}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
