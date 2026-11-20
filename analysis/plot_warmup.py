"""Warm-up curves of a pilot of long runs, one panel per workload.

Usage: uv run --no-project --with matplotlib python -m analysis.plot_warmup
       data/raw/<pilot>... paper/figures
Writes warmup-n<N>.pdf for every thread count in the pilot; the dashed line
is the workload's W from analysis.warmup.
"""

import sys
from pathlib import Path

from analysis.figures.warmup import warmup_figures
from analysis.pilot.warmup import load_series


def main(argv: list[str]) -> int:
    *directories, output = (Path(argument) for argument in argv)
    warmup_figures([run for directory in directories for run in load_series(directory)], output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
