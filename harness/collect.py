"""Join a campaign's runs into one table: one row per CSV row,
with the run id and its context. Failed runs are counted, never joined.

Usage: python3 -m harness.collect data/raw/<campaign> [--output table.csv]
"""

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO, TypedDict, cast

from harness.context import JsonObject
from harness.context.results import CSV_SUFFIX, ERROR_SUFFIX, METADATA_SUFFIX
from harness.native import CSV_HEADER

CONTEXT_COLUMNS = ("orderPosition", "startedAt", "foreignCpuSeconds", "startDelayMs")
CAMPAIGN_METADATA = "campaign"
UNKNOWN_ENVIRONMENT = "unknown"



# One joined row: the run id, the context columns (CONTEXT_COLUMNS, as the run's JSON holds
# them) and the bench's CSV columns (CSV_HEADER), which stay the strings the bench wrote.
# A test keeps the keys equal to those two lists.
class Row(TypedDict):
    run: str
    orderPosition: object
    startedAt: object
    foreignCpuSeconds: object
    startDelayMs: object
    env: str
    workload: str
    input: str
    k: str
    width: str
    height: str
    seed: str
    threads: str
    phase: str
    iter: str
    ns: str
    input_fingerprint: str
    checksum: str
    probe: str
    mem_before_bytes: str
    mem_after_bytes: str
    input_addr_mod4096: str
    input_addr_mod64: str
    output_addr_mod4096: str
    output_addr_mod64: str
    pitch: str
    palette: str
    schema: str
    passes: str
    grain: str


class IncompleteRun(ValueError):
    pass


class ForeignSchema(ValueError):
    """A CSV whose header is not the current CSV_HEADER: a run of another build."""


@dataclass
class Collection:
    rows: list[Row] = field(default_factory=list)
    failed: Counter[str] = field(default_factory=Counter)
    missing: list[str] = field(default_factory=list)
    checksum_conflicts: dict[str, list[str]] = field(default_factory=dict)


def run_ids(directory: Path, suffix: str) -> set[str]:
    return {
        path.name.removesuffix(suffix)
        for path in directory.glob(f"*{suffix}")
        if not path.name.endswith(".error" + suffix)
    }


def error_run_ids(directory: Path) -> set[str]:
    return {path.name.removesuffix(ERROR_SUFFIX) for path in directory.glob(f"*{ERROR_SUFFIX}")}


def read_json(path: Path) -> JsonObject:
    document: JsonObject = json.loads(path.read_text())
    return document


def collect(directory: Path) -> Collection:
    csvs = complete_runs(directory)
    collection = Collection()
    collection.missing = missing_runs(directory, csvs)
    collection.failed = failures_by_environment(directory)
    collection.rows = joined_rows(directory, csvs)
    collection.checksum_conflicts = checksum_conflicts(collection.rows)
    return collection


def complete_runs(directory: Path) -> set[str]:
    csvs = run_ids(directory, CSV_SUFFIX)
    metadata = run_ids(directory, METADATA_SUFFIX) - {CAMPAIGN_METADATA}
    incomplete = sorted(csvs ^ metadata)
    if incomplete:
        raise IncompleteRun(f"runs without both CSV and JSON: {', '.join(incomplete)}")
    return csvs


def missing_runs(directory: Path, csvs: set[str]) -> list[str]:
    campaign = directory / f"{CAMPAIGN_METADATA}{METADATA_SUFFIX}"
    if not campaign.exists():
        return []
    errors = error_run_ids(directory)
    planned = read_json(campaign).get("runs", [])
    if not isinstance(planned, list):
        return []
    return [run for run in planned if isinstance(run, str) and run not in csvs and run not in errors]


def failures_by_environment(directory: Path) -> Counter[str]:
    failed: Counter[str] = Counter()
    for error in sorted(directory.glob(f"*{ERROR_SUFFIX}")):
        failed[str(read_json(error).get("environment", UNKNOWN_ENVIRONMENT))] += 1
    return failed


def joined_rows(directory: Path, csvs: set[str]) -> list[Row]:
    contexts = {run_id: read_json(directory / f"{run_id}{METADATA_SUFFIX}") for run_id in csvs}

    def order(run_id: str) -> tuple[int, str]:
        position = contexts[run_id].get("orderPosition")
        return (position if isinstance(position, int) else 0, run_id)

    rows: list[Row] = []
    for run_id in sorted(csvs, key=order):
        context = contexts[run_id]
        with (directory / f"{run_id}{CSV_SUFFIX}").open() as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise ForeignSchema(f"{run_id}: empty CSV")
            if reader.fieldnames != CSV_HEADER.split(","):
                raise ForeignSchema(f"{run_id}: CSV header is not the current schema")
            for row in reader:
                rows.append(cast(Row, {"run": run_id, **{key: context.get(key) for key in CONTEXT_COLUMNS}, **row}))
    return rows


def checksum_conflicts(rows: list[Row]) -> dict[str, list[str]]:
    checksums: dict[str, set[str]] = {}
    for row in rows:
        # The palette changes the input and so the checksum; the pitch does not (only the width
        # of each row is hashed).
        palette = f" {row['palette']}" if row["input"] == "few" else ""
        key = f"{row['workload']} {row['input']} k={row['k']}{palette} {row['width']}x{row['height']} seed {row['seed']}"
        checksums.setdefault(key, set()).add(str(row["checksum"]))
    return {key: sorted(values) for key, values in checksums.items() if len(values) > 1}


def write_table(collection: Collection, output: TextIO) -> None:
    writer = csv.DictWriter(output, fieldnames=["run", *CONTEXT_COLUMNS, *CSV_HEADER.split(",")], lineterminator="\n")
    writer.writeheader()
    writer.writerows(collection.rows)


def report(collection: Collection) -> int:
    for environment, count in sorted(collection.failed.items()):
        print(f"failed runs in {environment}: {count}", file=sys.stderr)
    for run in collection.missing:
        print(f"planned run without any file: {run}", file=sys.stderr)
    for key, checksums in collection.checksum_conflicts.items():
        print(f"checksums differ for {key}: {', '.join(checksums)}", file=sys.stderr)
    return 1 if collection.missing or collection.checksum_conflicts else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    collection = collect(args.directory)
    if args.output:
        with args.output.open("w") as file:
            write_table(collection, file)
    else:
        write_table(collection, sys.stdout)
    return report(collection)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
