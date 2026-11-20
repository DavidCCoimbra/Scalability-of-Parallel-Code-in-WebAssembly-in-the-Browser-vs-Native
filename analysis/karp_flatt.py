"""Karp-Flatt serial fraction per configuration and N > 1, from a strong
scaling table written by `analysis.v0`.

Usage: python3 -m analysis.karp_flatt data/tables/<campaign>/<campaign>-scaling.csv
       --output data/tables/<campaign>/<campaign>-karp-flatt.csv
The interval comes from the speedup's 95 % bootstrap interval.
"""

import argparse
import csv
import sys
from pathlib import Path

from analysis.scaling.karp_flatt import karp_flatt_rows, write_karp_flatt


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("scaling", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    with args.scaling.open(newline="") as file:
        rows = karp_flatt_rows(csv.DictReader(file))
    with args.output.open("w") as file:
        write_karp_flatt(rows, file)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
