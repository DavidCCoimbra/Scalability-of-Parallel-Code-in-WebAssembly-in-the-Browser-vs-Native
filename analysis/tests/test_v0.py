import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from analysis.scaling.output import STRONG_COLUMNS, WEAK_COLUMNS, Scaling, write_scaling
from analysis.scaling.report import InvalidCampaign, analyse
from analysis.v0 import main
from harness.native import CSV_HEADER


def write_run(root: Path, run_id: str, position: int, threads: int, times: list[int]) -> None:
    rows = [f"native,filter,noise,,64,64,24301,{threads},warmup,0,999,0x01,0xab"]
    rows += [f"native,filter,noise,,64,64,24301,{threads},measured,{i},{ns},0x01,0xab" for i, ns in enumerate(times)]
    (root / f"{run_id}.csv").write_text(CSV_HEADER + "\n" + "\n".join(rows) + "\n")
    (root / f"{run_id}.json").write_text(json.dumps({"orderPosition": position}))


class AnalyseTest(unittest.TestCase):
    def test_campaign_directory_becomes_a_scaling_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "c-0000", 0, 1, [100, 110, 90])
            write_run(root, "c-0001", 1, 2, [50, 60, 40])
            write_run(root, "c-0002", 2, 1, [100, 100, 100])
            write_run(root, "c-0003", 3, 2, [50, 50, 50])
            output = io.StringIO()
            report = analyse(root)
            write_scaling(report.rows, output)
        rows = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(list(rows[0]), list(STRONG_COLUMNS))
        two = [row for row in rows if row["threads"] == "2"][0]
        self.assertEqual((two["environment"], two["runs"], two["speedup"]), ("native", "2", "2.000"))
        self.assertEqual(two["efficiency"], "1.000")
        self.assertEqual(two["baseline_runs"], "2")
        self.assertEqual(report.failed, {})

    def test_weak_scaling_writes_t1_over_tn_as_weak_efficiency_without_speedup_over_n(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "c-0000", 0, 1, [100, 100, 100])
            write_run(root, "c-0001", 1, 2, [125, 125, 125])
            output = io.StringIO()
            write_scaling(analyse(root).rows, output, Scaling.WEAK)
        rows = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(list(rows[0]), list(WEAK_COLUMNS))
        self.assertNotIn("efficiency", rows[0])
        two = [row for row in rows if row["threads"] == "2"][0]
        self.assertEqual(two["weak_efficiency"], "0.800")

    def test_checksum_conflicts_stop_the_analysis_before_any_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "c-0000", 0, 1, [100])
            write_run(root, "c-0001", 1, 2, [50])
            conflicting = (root / "c-0001.csv").read_text().replace("0xab", "0xcd")
            (root / "c-0001.csv").write_text(conflicting)
            with self.assertRaises(InvalidCampaign):
                analyse(root)
            output = root / "scaling.csv"
            self.assertEqual(main([str(root), "--output", str(output)]), 1)
            self.assertFalse(output.exists())

    def test_per_run_summary_is_only_median_or_mean(self) -> None:
        with self.assertRaises(SystemExit):
            main(["unused", "--summary", "geometric"])

    def test_output_gets_a_sidecar_with_options_seed_and_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "c-0000", 0, 1, [100])
            output = root / "scaling.csv"
            self.assertEqual(main([str(root), "--output", str(output), "--summary", "mean"]), 0)
            meta = json.loads(output.with_suffix(".json").read_text())
        self.assertEqual((meta["summary"], meta["center"]), ("mean", "geometric"))
        self.assertEqual(meta["bootstrapSeed"], 0x5EED)
        self.assertIn("commit", meta)
        self.assertEqual(meta["campaign"], str(root))
        self.assertEqual(meta["clockWarnings"], [])


if __name__ == "__main__":
    unittest.main()
