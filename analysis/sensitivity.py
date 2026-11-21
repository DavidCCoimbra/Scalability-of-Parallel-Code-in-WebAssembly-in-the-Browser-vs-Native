"""The analysis plan's sensitivity checks on the primary contrasts, side by side.

Usage: python3 -m analysis.sensitivity --primary contrasts.csv
       --check NAME=contrasts.csv [--check NAME=contrasts.csv ...] --output sensitivity.csv
Each file is a contrasts table of analysis.results: the primary one, and one
per check (per-run mean, median centre, no foreign-CPU exclusion). Per primary
contrast, the output has the effect, the Bonferroni interval, the Holm p-value
and the decision under the primary analysis and under every check, and
`robust`: "yes" when every check takes the primary decision. The plan reports
a conclusion that changes under a check as not robust.
"""

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

PRIMARY = "primary"
PRIMARY_FLAG = "yes"
KEY_COLUMNS = ("question", "environment", "workload", "input", "k", "threads")
VALUE_COLUMNS = ("effect", "primary_low", "primary_high", "holm_p", "rejected")

Key = tuple[str, ...]


class IncompleteCheck(ValueError):
    pass


@dataclass(frozen=True)
class Analysis:
    name: str
    contrasts: dict[Key, dict[str, str]]

    @classmethod
    def read(cls, name: str, path: Path) -> "Analysis":
        with path.open() as file:
            rows = [row for row in csv.DictReader(file) if row[PRIMARY] == PRIMARY_FLAG]
        return cls(name, {tuple(row[column] for column in KEY_COLUMNS): row for row in rows})

    def decision(self, key: Key) -> str:
        return self.contrasts[key]["rejected"]

    def cells(self, key: Key) -> list[str]:
        return [self.contrasts[key][column] for column in VALUE_COLUMNS]

    @property
    def columns(self) -> list[str]:
        return [f"{self.name}_{column}" for column in VALUE_COLUMNS]


def named_check(text: str) -> tuple[str, Path]:
    name, separator, path = text.partition("=")
    if not separator or not name or not path:
        raise argparse.ArgumentTypeError(f"expected NAME=contrasts.csv, found {text!r}")
    return name, Path(path)


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--check", type=named_check, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def sensitivity_rows(primary: Analysis, checks: list[Analysis]) -> list[list[str]]:
    for check in checks:
        if set(check.contrasts) != set(primary.contrasts):
            raise IncompleteCheck(f"{check.name} does not have the primary contrasts of the primary analysis")
    rows = []
    for key in primary.contrasts:
        robust = all(check.decision(key) == primary.decision(key) for check in checks)
        cells = [cell for analysis in (primary, *checks) for cell in analysis.cells(key)]
        rows.append([*key, *cells, "yes" if robust else "no"])
    return rows


def header(primary: Analysis, checks: list[Analysis]) -> list[str]:
    return [*KEY_COLUMNS, *(column for analysis in (primary, *checks) for column in analysis.columns), "robust"]


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    primary = Analysis.read(PRIMARY, args.primary)
    checks = [Analysis.read(name, path) for name, path in args.check]
    try:
        rows = sensitivity_rows(primary, checks)
    except IncompleteCheck as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    with args.output.open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(header(primary, checks))
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
