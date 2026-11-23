import csv
import json
import tempfile
import unittest
from collections.abc import Mapping
from pathlib import Path

from analysis.configuration import Configuration
from analysis.extras import core_split, variants
from analysis.extras.perf.loop import loop_counters
from analysis.extras.perf.run_counters import Run, RunCounters
from analysis import sequential
from harness.native import CSV_HEADER

COLUMNS = CSV_HEADER.split(",")


def write_run(root: Path, run_id: str, workload: str, threads: int, ns: int, context: Mapping[str, object] | None = None, warmup_ns: int | None = None) -> None:
    def row(phase: str, value: int) -> str:
        cells = dict.fromkeys(COLUMNS, "")
        cells.update(env="chrome", workload=workload, input="noise", width="8", height="8", seed="1", threads=str(threads))
        cells.update(phase=phase, iter="0", ns=str(value), input_fingerprint="0x01", checksum="0xab", schema="3", passes="1")
        return ",".join(cells[column] for column in COLUMNS)

    rows = ([row("warmup", warmup_ns)] if warmup_ns is not None else []) + [row("measured", ns)]
    (root / f"{run_id}.csv").write_text(CSV_HEADER + "\n" + "\n".join(rows) + "\n")
    (root / f"{run_id}.json").write_text(json.dumps({"orderPosition": 0, "foreignCpuSeconds": 0.0, **(context or {})}))


def busy_on_12(seconds: float) -> dict[str, object]:
    return {"cores": {"12": {"busySeconds": seconds}, "14": {"busySeconds": 1.0}}}


def table(path: Path) -> list[dict[str, str]]:
    with path.open() as file:
        return list(csv.DictReader(file))


def counters(configuration: Configuration, operations: int, instructions: float) -> RunCounters:
    return RunCounters(Run("r", configuration, 0.0, 1.0, operations), 1, {"instructions": instructions / operations})


class V3TablesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.output = self.root / "table.csv"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_each_engine_arm_scales_against_its_own_one_thread_runs(self) -> None:
        for index, (arm, one, eight) in enumerate((("baseline", 400, 100), ("optimizing", 800, 400))):
            context = {"engineArm": {"name": arm}}
            write_run(self.root, f"r{index}a", "filter", 1, one, context, warmup_ns=one // 2)
            write_run(self.root, f"r{index}b", "filter", 8, eight, context)
        self.assertEqual(variants.main([str(self.root), "--by", "engine-arm", "--output", str(self.output)]), 0)
        rows = {(row["variant"], row["threads"]): row for row in table(self.output)}
        self.assertEqual(rows[("baseline", "8")]["speedup"], "4")
        self.assertEqual(rows[("optimizing", "8")]["speedup"], "2")
        self.assertEqual(rows[("baseline", "1")]["first_warmup_over_value"], "0.5")

    def test_a_run_without_a_grain_is_the_adaptive_variant(self) -> None:
        write_run(self.root, "r0", "filter", 1, 100)
        write_run(self.root, "r1", "filter", 1, 100, {"grain": 256})
        self.assertEqual(variants.main([str(self.root), "--by", "grain", "--output", str(self.output)]), 0)
        self.assertEqual([row["variant"] for row in table(self.output)], ["256", "adaptive"])

    def test_the_sequential_reference_divides_the_parallel_times(self) -> None:
        write_run(self.root, "r0", "filter-seq", 1, 900)
        write_run(self.root, "r1", "filter", 1, 1000)
        write_run(self.root, "r2", "filter", 8, 150)
        self.assertEqual(sequential.main([str(self.root), "--output", str(self.output)]), 0)
        rows = {row["threads"]: row for row in table(self.output)}
        self.assertEqual(rows["1"]["speedup_vs_sequential"], "0.9")
        self.assertEqual(rows["8"]["speedup_vs_sequential"], "6")

    def test_one_thread_runs_are_split_by_their_busiest_cpu(self) -> None:
        write_run(self.root, "r0", "filter", 1, 100, busy_on_12(3.0))
        write_run(self.root, "r1", "filter", 1, 120, busy_on_12(0.1))
        write_run(self.root, "r2", "filter", 8, 20, busy_on_12(3.0))
        self.assertEqual(core_split.main([str(self.root), "--output", str(self.output)]), 0)
        self.assertEqual([(row["cpu"], row["runs"], row["threads"]) for row in table(self.output)], [("12", "1", "1"), ("14", "1", "1")])

    def test_the_loop_counter_is_the_difference_of_counts_over_the_difference_of_pixels(self) -> None:
        cell = Configuration("native", "hist-local", "few", 256, 1)
        few = [counters(cell, 1_000, 13_000.0), counters(cell, 1_000, 13_000.0)]
        many = [counters(cell, 8_000, 34_000.0), counters(cell, 8_000, 34_000.0)]
        (row,) = loop_counters(few, many)
        self.assertAlmostEqual(row.per_pixel, 3.0)
        self.assertEqual((row.runs_few, row.runs_many, row.counter), (2, 2, "instructions"))


if __name__ == "__main__":
    unittest.main()
