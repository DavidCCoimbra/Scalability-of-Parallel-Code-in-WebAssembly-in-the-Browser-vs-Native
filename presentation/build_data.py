"""Writes the numbers of the interactive demos into index.html, from the measured/v3 tables.

Run from the repository root: python3 presentation/build_data.py
It replaces the block between the `demo-data` markers of presentation/index.html, so the
values a demo shows are never typed by hand.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "data" / "tables"
CAMPAIGN = ROOT / "data" / "raw" / "campaign-v3"
DECK = ROOT / "presentation" / "index.html"

ENVIRONMENTS = ("native", "chrome", "firefox")
THREADS = (1, 2, 4, 6, 7, 8)
MAX_THREADS = "8"
RUNS_PER_ENVIRONMENT = 1770
REPETITIONS = 30
ORDER_DIGITS = 3
# The run whose iterations the timeline of slide 4 draws: a browser run, so it has the start delay.
TIMELINE_RUN = "campaign-v3-0188-chrome-filter-noise-n8-r1"
SCALING_WORKLOADS = {
    "filter": ("filter", ""),
    "local256": ("hist-local", "256"),
    "atomic1": ("hist-atomic", "1"),
    "atomic256": ("hist-atomic", "256"),
}
CUTOFF_WORKLOADS = {"filter": ("filter", "")}
# SpiderMonkey's `lock add` has no probe sequence of its own.
PROBE_SEQUENCES = {"inc": "lock-inc", "cas": "compare-and-swap", "xadd": "lock-xadd-checked"}
# Which engine runs each sequence, and the arm of the tier campaign that measured it.
ENGINE_OF_SEQUENCE = {
    "inc": ("native", "-"),
    "add": ("firefox", "optimizing"),
    "cas": ("chrome", "optimizing"),
    "xadd": ("chrome", "baseline"),
}
ATOMIC_K = ("1", "4", "16", "256")
NS_PER_MS = 1e6


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def scaling() -> dict[str, dict[str, list[dict[str, float]]]]:
    table = rows(TABLES / "campaign-v3" / "campaign-v3-scaling.csv")
    result: dict[str, dict[str, list[dict[str, float]]]] = {}
    for name, (workload, k) in SCALING_WORKLOADS.items():
        result[name] = {}
        for environment in ENVIRONMENTS:
            cells = {
                int(row["threads"]): row
                for row in table
                if row["environment"] == environment and row["workload"] == workload and row["k"] == k
            }
            result[name][environment] = [
                {
                    "ms": round(float(cells[n]["center_ns"]) / NS_PER_MS, 4),
                    "s": float(cells[n]["speedup"]),
                    "sl": float(cells[n]["speedup_low"]),
                    "sh": float(cells[n]["speedup_high"]),
                    "e": float(cells[n]["efficiency"]),
                    "el": float(cells[n]["efficiency_low"]),
                    "eh": float(cells[n]["efficiency_high"]),
                }
                for n in THREADS
            ]
    return result


def cutoff() -> dict[str, object]:
    table = rows(TABLES / "cutoff-v3" / "cutoff-table.csv")
    model = rows(TABLES / "cutoff-v3" / "cutoff-model.csv")
    sides = sorted({int(row["side"]) for row in table})
    cells: dict[str, dict[str, list[dict[str, float]]]] = {}
    for name, (workload, k) in CUTOFF_WORKLOADS.items():
        cells[name] = {}
        for environment in ENVIRONMENTS:
            by_side = {
                int(row["side"]): row
                for row in table
                if row["environment"] == environment
                and row["workload"] == workload
                and row["k"] == k
                and row["threads"] == MAX_THREADS
            }
            cells[name][environment] = [
                {
                    "e": float(by_side[side]["efficiency"]),
                    "t8us": round(float(by_side[side]["tn_ns"]) / 1000, 1),
                    "workus": float(by_side[side]["work_us"]),
                }
                for side in sides
            ]
    fork_join = {
        row["environment"]: float(row["fork_join_us"]) for row in model if row["workload"] == "filter"
    }
    return {"sides": sides, "cells": cells, "forkJoinUs": fork_join}


def probe_times() -> dict[str, dict[str, dict[str, float]]]:
    """The result table of the atomic increment probe: sequence -> k -> {n1, n8} in ms."""
    text = (ROOT / "data" / "probes" / "atomic-increment" / "README.md").read_text()
    header = re.search(r"^\| Sequence \| k = 1, N = 1 .*$", text, re.MULTILINE)
    if header is None:
        raise SystemExit("the probe README no longer has its result table")
    columns = [cell.strip() for cell in header.group(0).strip("|").split("|")][1:]
    result: dict[str, dict[str, dict[str, float]]] = {}
    for line in text[header.end() :].splitlines()[2:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        result[cells[0]] = {}
        for column, value in zip(columns, cells[1:]):
            match = re.fullmatch(r"k = (\d+), N = (\d+)", column)
            if match is None:
                raise SystemExit(f"unexpected probe column: {column}")
            result[cells[0]].setdefault(match.group(1), {})["n" + match.group(2)] = float(value)
    return result


def atomic() -> dict[str, object]:
    arms = rows(TABLES / "tier-v3" / "tier-v3-arms.csv")
    main = rows(TABLES / "campaign-v3" / "campaign-v3-scaling.csv")
    probe = probe_times()

    def tier_ms(environment: str, variant: str, k: str, threads: str) -> float | None:
        for row in arms:
            if (
                row["environment"] == environment
                and row["workload"] == "hist-atomic"
                and row["variant"] == variant
                and row["k"] == k
                and row["threads"] == threads
            ):
                return round(float(row["center_ns"]) / NS_PER_MS, 1)
        return None

    def main_ms(environment: str, k: str, threads: str) -> float:
        for row in main:
            if (
                row["environment"] == environment
                and row["workload"] == "hist-atomic"
                and row["k"] == k
                and row["threads"] == threads
            ):
                return round(float(row["center_ns"]) / NS_PER_MS, 1)
        raise SystemExit(f"no main campaign cell for {environment} k={k} N={threads}")

    engine: dict[str, dict[str, dict[str, object] | None]] = {}
    probes: dict[str, dict[str, dict[str, float] | None]] = {}
    for sequence, (environment, variant) in ENGINE_OF_SEQUENCE.items():
        engine[sequence] = {}
        if sequence in PROBE_SEQUENCES:
            probes[sequence] = {}
        for k in ATOMIC_K:
            one, eight = tier_ms(environment, variant, k, "1"), tier_ms(environment, variant, k, MAX_THREADS)
            if one is not None and eight is not None:
                engine[sequence][k] = {"n1": one, "n8": eight, "src": "tier campaign"}
            elif variant != "baseline":
                # The tier campaign has k = 1 and 256 only; the arm as shipped is the main campaign's.
                engine[sequence][k] = {
                    "n1": main_ms(environment, k, "1"),
                    "n8": main_ms(environment, k, MAX_THREADS),
                    "src": "main campaign",
                }
            else:
                engine[sequence][k] = None
            if sequence in PROBE_SEQUENCES:
                probes[sequence][k] = probe[PROBE_SEQUENCES[sequence]].get(k)
    retries = {
        f"{row['environment']}-{row['k']}": float(row["excess_lock_loads"])
        for row in rows(TABLES / "perf-v3" / "perf-v3-retries.csv")
        if row["workload"] == "hist-atomic"
    }
    return {"engine": engine, "probe": probes, "retries": retries}


class JournalRun(NamedTuple):
    """One run of the campaign's journal, in the order it ran."""

    position: int
    environment: str
    workload: str
    k: int
    threads: int
    repetition: int

    @property
    def configuration(self) -> tuple[str, int, int]:
        return (self.workload, self.k, self.threads)


def journal() -> list[JournalRun]:
    with (CAMPAIGN / "campaign.jsonl").open() as handle:
        entries = [json.loads(line) for line in handle]
    runs = [
        JournalRun(
            int(entry["position"]),
            str(entry["environment"]),
            str(entry["workload"]),
            int(entry["k"] or 0),
            int(entry["threads"]),
            int(entry["repetition"]),
        )
        for entry in entries
        if not entry.get("discarded")
    ]
    return sorted(runs)


def base36(value: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    text = ""
    for _ in range(ORDER_DIGITS):
        text = digits[value % len(digits)] + text
        value //= len(digits)
    return text


def execution_order() -> dict[str, object]:
    """The order the campaign ran in, as one cell index per run: environment, configuration, repetition."""
    runs = journal()
    configurations = sorted({run.configuration for run in runs})
    encoded = "".join(
        base36(
            ENVIRONMENTS.index(run.environment) * RUNS_PER_ENVIRONMENT
            + configurations.index(run.configuration) * REPETITIONS
            + run.repetition
        )
        for run in runs
    )
    return {"runs": len(runs), "configurations": len(configurations), "order": encoded}


def timeline_run() -> dict[str, object]:
    table = rows(CAMPAIGN / f"{TIMELINE_RUN}.csv")
    warmup = [round(float(row["ns"]) / NS_PER_MS, 3) for row in table if row["phase"] == "warmup"]
    measured = [round(float(row["ns"]) / NS_PER_MS, 3) for row in table if row["phase"] == "measured"]
    return {"id": TIMELINE_RUN, "warmupMs": warmup, "measuredMs": measured}


def main() -> None:
    data = {
        "scaling": scaling(),
        "cutoff": cutoff(),
        "atomic": atomic(),
        "campaign": execution_order(),
        "run": timeline_run(),
    }
    block = "// <demo-data> written by presentation/build_data.py, do not edit\nconst DEMO = " + json.dumps(
        data, separators=(",", ":")
    ) + ";\n// </demo-data>"
    text = DECK.read_text()
    pattern = re.compile(r"// <demo-data>.*?// </demo-data>", re.DOTALL)
    if pattern.search(text) is None:
        raise SystemExit("presentation/index.html has no demo-data block")
    DECK.write_text(pattern.sub(lambda _: block, text))


if __name__ == "__main__":
    main()
