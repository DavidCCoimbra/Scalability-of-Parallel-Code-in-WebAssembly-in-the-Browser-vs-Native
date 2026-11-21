import json
import tempfile
import unittest
from pathlib import Path

from analysis.gate import main
from analysis.loading import ExclusionRule
from analysis.quality.gate import gate_problems
from harness.native import CSV_HEADER

COLUMNS = CSV_HEADER.split(",")


def write_run(root: Path, run_id: str, workload: str, times: list[int], checksum: str = "0xab", k: str = "", resolution: int = 100) -> None:
    rows = []
    for index, ns in enumerate(times):
        cells = dict.fromkeys(COLUMNS, "")
        cells.update(env="native", workload=workload, input="few" if k else "noise", k=k, width="64", height="64", seed="1", threads="1")
        cells.update(phase="measured", iter=str(index), ns=str(ns), input_fingerprint="0x01", checksum=checksum, schema="3", passes="1")
        rows.append(",".join(cells[column] for column in COLUMNS))
    (root / f"{run_id}.csv").write_text(CSV_HEADER + "\n" + "\n".join(rows) + "\n")
    (root / f"{run_id}.json").write_text(json.dumps({"orderPosition": 0, "foreignCpuSeconds": 0.0, "clockResolutionNs": resolution}))


STEADY = [100_000, 100_100, 99_900, 100_000, 100_050, 99_950]


class GateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def problems(self) -> list[str]:
        # The strict rule needs a full run context, which these runs do not have; the gate's
        # own checks are what these tests are about.
        return gate_problems(self.root, ExclusionRule())

    def test_steady_runs_with_agreeing_outputs_pass(self) -> None:
        write_run(self.root, "r0", "filter", STEADY)
        write_run(self.root, "r1", "filter-seq", STEADY)
        self.assertEqual(self.problems(), [])

    def test_a_sequential_reference_with_another_output_is_a_problem(self) -> None:
        write_run(self.root, "r0", "hist-local", STEADY, checksum="0x01", k="4")
        write_run(self.root, "r1", "hist-atomic", STEADY, checksum="0x01", k="4")
        write_run(self.root, "r2", "hist-seq", STEADY, checksum="0x02", k="4")
        (problem,) = self.problems()
        self.assertIn("few k=4: outputs differ between workloads", problem)

    def test_a_sample_under_100_times_the_clock_resolution_is_a_problem(self) -> None:
        write_run(self.root, "r0", "filter", [*STEADY[:-1], 9_000])
        self.assertTrue(any("r0: a sample of 9000 ns is under 100x the clock resolution 100 ns" in problem for problem in self.problems()))

    def test_measured_iterations_that_drift_more_than_5_percent_are_a_problem(self) -> None:
        write_run(self.root, "r0", "filter", [120_000, 118_000, 119_000, 100_000, 100_000, 100_000])
        (problem,) = self.problems()
        self.assertIn("native filter noise k=None N=1: the first 3 measured iterations are 1.190 times the last 3", problem)

    def test_a_run_without_a_clock_resolution_is_a_problem(self) -> None:
        write_run(self.root, "r0", "filter", STEADY)
        (self.root / "r0.json").write_text(json.dumps({"orderPosition": 0, "foreignCpuSeconds": 0.0}))
        self.assertEqual(self.problems(), ["r0: no clock resolution recorded"])

    def test_the_command_is_strict_and_fails_on_a_run_that_strict_validation_excludes(self) -> None:
        write_run(self.root, "r0", "filter", STEADY)
        self.assertEqual(main([str(self.root)]), 1)
        self.assertEqual(gate_problems(self.root), ["1 run(s) excluded by strictValidation"])


if __name__ == "__main__":
    unittest.main()
