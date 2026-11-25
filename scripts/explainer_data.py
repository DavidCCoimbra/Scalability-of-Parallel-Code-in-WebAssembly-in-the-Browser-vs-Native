"""Writes docs/explainer/assets/data.js: every number and code excerpt the explainer shows.

The explainer pages never hold a measured number of their own. They read window.PPC, which this
script builds from the measured/v3 tables in data/tables/*-v3/ (one key per CSV, rows as objects),
the fork-join calibration in the raw campaign-v3 runs, the two checks that are not results (the
per-core check and the atomic increment probe), and the code excerpts the pages ask for.

A page asks for an excerpt with a key "path|first line|number of lines", either as
data-code="..." or as UI.code("..."). The first line is a literal substring of the one line where the
excerpt starts (or, after a ^, its start), so the excerpt follows the code when lines move; a key that no longer matches stops
the script.

Usage: python3 -m scripts.explainer_data [--check]
--check exits 1 if data.js is not what the script would write (used by CI after a data change).
"""

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLAINER = ROOT / "docs" / "explainer"
OUT = EXPLAINER / "assets" / "data.js"
TABLES = ROOT / "data" / "tables"
CAMPAIGN = ROOT / "data" / "raw" / "campaign-v3"
CORE_CHECK = ROOT / "data" / "checks" / "core-check" / "runs"
ATOMIC_INCREMENT = ROOT / "data" / "probes" / "atomic-increment" / "passes.csv"
CORE_CHECK_RUN = re.compile(r"^core-check-c(?P<cpu>\d+)-r\d+$")
CODE_KEY = re.compile(r'(?:data-code="|UI\.code\(\s*")([^"|]+\|[^"|]+\|\d+)')
CODE_ATTRIBUTE = re.compile(r'data-code="([^"]*)"')
RUN_NAME = re.compile(r"-(?P<environment>native|chrome|firefox)-[a-z0-9-]+?-n(?P<threads>\d+)-r\d+$")
FORK_JOIN_PHASE = "calibration-warm"
NS_PER_US = 1000

Row = dict[str, str | float | int]


@dataclass(frozen=True)
class Excerpt:
    file: str
    line: int
    text: str


def number(text: str) -> str | float | int:
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def read_table(path: Path) -> list[Row]:
    with path.open(newline="") as file:
        return [{key: number(value) for key, value in row.items()} for row in csv.DictReader(file)]


def table_paths() -> list[Path]:
    return [path for path in sorted(TABLES.glob("*-v3/*.csv")) if not path.stem.endswith("-runs")]


def tables() -> dict[str, list[Row]]:
    return {path.stem: read_table(path) for path in table_paths()}


def sources() -> dict[str, str]:
    return {path.stem: path.relative_to(ROOT).as_posix() for path in table_paths()}


# The warm fork-join of every run: the median of its 20 calibration calls per probe, then the
# median of those run medians per environment and N, and the mean of all calls (the numbers of
# the paper: a median of 110 us and a mean of 171 us for Chrome's broadcast at N = 8).
def fork_join() -> list[Row]:
    medians: dict[tuple[str, int, str], list[float]] = defaultdict(list)
    calls: dict[tuple[str, int, str], list[int]] = defaultdict(list)
    for path in sorted(CAMPAIGN.glob("*.csv")):
        match = RUN_NAME.search(path.stem)
        if match is None:
            continue
        by_probe: dict[str, list[int]] = defaultdict(list)
        with path.open(newline="") as file:
            for row in csv.DictReader(file):
                if row["phase"] == FORK_JOIN_PHASE:
                    by_probe[row["probe"]].append(int(row["ns"]))
        for probe, values in by_probe.items():
            key = (match["environment"], int(match["threads"]), probe)
            medians[key].append(statistics.median(values) / NS_PER_US)
            calls[key].extend(values)
    return [
        {
            "environment": environment,
            "threads": threads,
            "probe": probe,
            "runs": len(values),
            "median_us": round(statistics.median(values), 2),
            "mean_us": round(statistics.fmean(calls[(environment, threads, probe)]) / NS_PER_US, 2),
        }
        for (environment, threads, probe), values in sorted(medians.items())
    ]


# The per-run medians (ms) of a few configurations, for the explainer's bootstrap widget: the
# value each run contributes to the analysis (the median of its 10 measured iterations).
RUN_MEDIAN_CONFIGURATIONS = (
    "filter-noise-n1",
    "filter-noise-n8",
    "hist-atomic-k1-n8",
)
RUN_FILE = re.compile(r"-(?P<environment>native|chrome|firefox)-(?P<configuration>[a-z0-9-]+?)-r(?P<repetition>\d+)$")
NS_PER_MS = 1_000_000
MEASURED_PHASE = "measured"


def run_medians() -> dict[str, list[float]]:
    medians: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for path in sorted(CAMPAIGN.glob("*.csv")):
        match = RUN_FILE.search(path.stem)
        if match is None or match["configuration"] not in RUN_MEDIAN_CONFIGURATIONS:
            continue
        with path.open(newline="") as file:
            measured = [int(row["ns"]) for row in csv.DictReader(file) if row["phase"] == MEASURED_PHASE]
        key = f"{match['environment']}-{match['configuration']}"
        medians[key].append((int(match["repetition"]), round(statistics.median(measured) / NS_PER_MS, 4)))
    return {key: [value for _, value in sorted(values)] for key, values in sorted(medians.items())}


# The per-core check (never results): the native filter at one thread pinned to one P-core at a
# time. One value per run, as in the analysis, then the median over the runs of each CPU.
def core_check() -> list[Row]:
    by_cpu: dict[int, list[float]] = defaultdict(list)
    for path in sorted(CORE_CHECK.glob("*.csv")):
        match = CORE_CHECK_RUN.match(path.stem)
        if match is None:
            continue
        with path.open(newline="") as file:
            measured = [int(row["ns"]) for row in csv.DictReader(file) if row["phase"] == MEASURED_PHASE]
        by_cpu[int(match["cpu"])].append(statistics.median(measured) / NS_PER_MS)
    every_run = statistics.median(value for values in by_cpu.values() for value in values)
    return [
        {
            "cpu": cpu,
            "runs": len(values),
            "median_ms": round(statistics.median(values), 2),
            "over_all_runs": round(statistics.median(values) / every_run, 3),
        }
        for cpu, values in sorted(by_cpu.items())
    ]


# The atomic increment probe (never results): the median pass of each increment sequence, per k
# and thread count, over its counted rounds.
def atomic_increment() -> list[Row]:
    passes: dict[tuple[str, int, int], list[int]] = defaultdict(list)
    with ATOMIC_INCREMENT.open(newline="") as file:
        for row in csv.DictReader(file):
            if row["counted"] == "yes":
                passes[(row["sequence"], int(row["k"]), int(row["threads"]))].append(int(row["ns"]))
    return [
        {"sequence": sequence, "k": k, "threads": threads, "passes": len(values), "median_ms": round(statistics.median(values) / NS_PER_MS, 1)}
        for (sequence, k, threads), values in sorted(passes.items())
    ]


# The anchor must be on exactly one line: on two, the excerpt could silently show the wrong code.
def excerpt(key: str) -> Excerpt:
    file, first, count = key.split("|")
    lines = (ROOT / file).read_text().splitlines()
    # "^{" matches a line that starts with "{" (the top of a JSON file, say), not any line holding it.
    if first.startswith("^"):
        found = [index for index, line in enumerate(lines) if line.startswith(first[1:])]
    else:
        found = [index for index, line in enumerate(lines) if first in line]
    if len(found) != 1:
        raise ValueError(f"excerpt {key!r}: {first!r} is on {len(found)} lines of {file}, not 1")
    index = found[0]
    return Excerpt(file, index + 1, "\n".join(lines[index : index + int(count)]))


# Any data-code attribute that is not "path|anchor|lines" (an anchor holding "|", say) would be
# skipped by CODE_KEY and show "excerpt not found" on the page, so it stops the script instead.
def malformed_keys(text: str) -> list[str]:
    return [value for value in CODE_ATTRIBUTE.findall(text) if not CODE_KEY.fullmatch(f'data-code="{value}')]


def excerpts() -> dict[str, Excerpt]:
    keys = set()
    for page in sorted(EXPLAINER.glob("*.html")):
        text = page.read_text()
        malformed = malformed_keys(text)
        if malformed:
            raise ValueError(f"{page.name}: data-code keys not of the form path|anchor|lines: {malformed}")
        keys.update(CODE_KEY.findall(text))
    return {key: excerpt(key) for key in sorted(keys)}


def render() -> str:
    data = {
        "tables": tables(),
        "sources": sources(),
        "forkJoin": fork_join(),
        "runMedians": run_medians(),
        "coreCheck": core_check(),
        "atomicIncrement": atomic_increment(),
        "code": {key: vars(value) for key, value in excerpts().items()},
    }
    body = json.dumps(data, indent=1, sort_keys=True, ensure_ascii=False)
    return f"// Generated by scripts/explainer_data.py from data/tables/*-v3, data/raw/campaign-v3, data/checks and data/probes. Do not edit.\nwindow.PPC = {body};\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = render()
    if args.check:
        current = OUT.read_text() if OUT.exists() else ""
        if current != text:
            print(f"{OUT.relative_to(ROOT)} is out of date: run python3 -m scripts.explainer_data", file=sys.stderr)
            return 1
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text) // 1024} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
