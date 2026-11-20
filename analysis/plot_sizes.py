"""Speedup at N = 8 against the image size, from the size sweep.

Usage: uv run --no-project --with matplotlib python -m analysis.plot_sizes
       paper/figures data/raw/pilot-size-<side>...
"""

import sys
from pathlib import Path

from analysis.figures.sizes import size_points, sizes_figure


def main(argv: list[str]) -> int:
    output, *directories = (Path(argument) for argument in argv)
    sizes_figure(size_points(directories), output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
