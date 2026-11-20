import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from harness.collect import IncompleteRun, collect, write_table
from harness.native import CSV_HEADER

ROW = "chrome,filter,noise,,8,8,24301,2,measured,0,123,0x01,0xab"


class CollectTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_pair(self, run_id: str, position: int, rows: int = 2) -> None:
        (self.root / f"{run_id}.csv").write_text(CSV_HEADER + "\n" + "\n".join([ROW] * rows) + "\n")
        (self.root / f"{run_id}.json").write_text(
            json.dumps({"orderPosition": position, "startedAt": "t", "foreignCpuSeconds": 0.01, "startDelayMs": 0, "environment": "chrome"})
        )

    def test_joins_each_pair_with_its_run_id_and_context(self) -> None:
        self.run_pair("c-0001-a", 1)
        self.run_pair("c-0000-b", 0, rows=1)
        collection = collect(self.root)
        self.assertEqual([row["run"] for row in collection.rows], ["c-0000-b", "c-0001-a", "c-0001-a"])
        self.assertEqual(collection.rows[0]["orderPosition"], 0)
        self.assertEqual(collection.rows[0]["ns"], "123")
        self.assertEqual(collection.rows[0]["foreignCpuSeconds"], 0.01)

    def test_failed_runs_are_counted_per_environment_and_never_joined(self) -> None:
        self.run_pair("c-0000-a", 0)
        (self.root / "c-0001-b.error.json").write_text(json.dumps({"error": "timeout", "environment": "firefox"}))
        (self.root / "c-0002-c.error.json").write_text(json.dumps({"error": "boom", "environment": "firefox"}))
        collection = collect(self.root)
        self.assertEqual({row["run"] for row in collection.rows}, {"c-0000-a"})
        self.assertEqual(collection.failed, {"firefox": 2})

    def test_an_incomplete_pair_stops_the_loader(self) -> None:
        self.run_pair("c-0000-a", 0)
        (self.root / "c-0000-a.json").unlink()
        with self.assertRaises(IncompleteRun):
            collect(self.root)
        (self.root / "c-0000-a.csv").unlink()
        (self.root / "c-0001-b.json").write_text("{}")
        with self.assertRaises(IncompleteRun):
            collect(self.root)

    def test_planned_runs_without_any_file_are_reported_missing(self) -> None:
        self.run_pair("c-0000-a", 0)
        (self.root / "c-0001-b.error.json").write_text(json.dumps({"environment": "chrome"}))
        (self.root / "campaign.json").write_text(json.dumps({"runs": ["c-0000-a", "c-0001-b", "c-0002-c"]}))
        self.assertEqual(collect(self.root).missing, ["c-0002-c"])

    def test_checksums_that_differ_for_one_workload_and_input_are_conflicts(self) -> None:
        self.run_pair("c-0000-a", 0)
        other = ROW.replace("chrome", "native").replace(",2,measured", ",4,measured").replace("0xab", "0xcd")
        (self.root / "c-0001-b.csv").write_text(CSV_HEADER + "\n" + other + "\n")
        (self.root / "c-0001-b.json").write_text(json.dumps({"orderPosition": 1}))
        self.assertEqual(collect(self.root).checksum_conflicts, {"filter noise k= 8x8 seed 24301": ["0xab", "0xcd"]})

    def test_runs_of_the_schema_1_builds_load_with_the_current_columns(self) -> None:
        legacy_header = "env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum"
        (self.root / "c-0000-a.csv").write_text(legacy_header + "\n" + ROW + "\n")
        (self.root / "c-0000-a.json").write_text(json.dumps({"orderPosition": 0, "passes": 2}))
        row = collect(self.root).rows[0]
        self.assertEqual((row["ns"], row["schema"], row["passes"], row["pitch"], row["probe"]), ("123", "1", "2", "8", ""))
        output = io.StringIO()
        write_table(collect(self.root), output)
        self.assertEqual(next(csv.reader(io.StringIO(output.getvalue())))[5:], CSV_HEADER.split(","))

    def test_the_two_palettes_of_one_k_are_not_a_checksum_conflict(self) -> None:
        few = "chrome,hist-local,few,4,8,8,24301,2,measured,0,123,0x01,{checksum},,,,,,,,8,{palette},2,1,"
        for position, (palette, checksum) in enumerate((("spread", "0xab"), ("consecutive", "0xcd"))):
            (self.root / f"c-000{position}-a.csv").write_text(CSV_HEADER + "\n" + few.format(checksum=checksum, palette=palette) + "\n")
            (self.root / f"c-000{position}-a.json").write_text(json.dumps({"orderPosition": position}))
        self.assertEqual(collect(self.root).checksum_conflicts, {})

    def test_campaign_files_logs_and_discarded_runs_are_ignored(self) -> None:
        self.run_pair("c-0000-a", 0)
        (self.root / "campaign.json").write_text("{}")
        (self.root / "campaign.jsonl").write_text("")
        (self.root / "c-0001-b.browser.log").write_text("log")
        (self.root / "discarded").mkdir()
        (self.root / "discarded" / "c-discard-chrome.csv").write_text(CSV_HEADER + "\n")
        self.assertEqual(len(collect(self.root).rows), 2)

    def test_table_has_run_context_then_csv_columns(self) -> None:
        self.run_pair("c-0000-a", 0, rows=1)
        output = io.StringIO()
        write_table(collect(self.root), output)
        rows = list(csv.reader(io.StringIO(output.getvalue())))
        self.assertEqual(rows[0][:5], ["run", "orderPosition", "startedAt", "foreignCpuSeconds", "startDelayMs"])
        self.assertEqual(rows[0][5:], CSV_HEADER.split(","))
        self.assertEqual(rows[1][:2], ["c-0000-a", "0"])


if __name__ == "__main__":
    unittest.main()
