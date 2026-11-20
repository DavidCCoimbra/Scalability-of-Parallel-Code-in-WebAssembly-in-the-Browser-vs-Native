import csv
import json
import tempfile
import unittest
from pathlib import Path

from analysis.inference.output import CONTRAST_COLUMNS
from analysis.results import main
from harness.native import CSV_HEADER


def write_run(root: Path, run_id: str, position: int, env: str, workload: str, k: str, threads: int, ns: int, foreign: float = 0.0, checksum: str = "0xab") -> None:
    input_ = "few" if k else "noise"
    row = f"{env},{workload},{input_},{k},64,64,24301,{threads},measured,0,{ns},0x01,{checksum}"
    (root / f"{run_id}.csv").write_text(CSV_HEADER + "\n" + row + "\n")
    (root / f"{run_id}.json").write_text(json.dumps({"orderPosition": position, "foreignCpuSeconds": foreign}))


class ResultsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        position = 0
        for env in ("native", "chrome"):
            for threads in (1, 4):
                for rep in range(4):
                    write_run(self.root, f"r{position:03d}", position, env, "filter", "", threads, 1000 // threads + rep, foreign=0.5 if position == 0 else 0.0)
                    position += 1

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_writes_contrasts_and_shape_tables(self) -> None:
        contrasts, shape = self.root / "contrasts.csv", self.root / "shape.csv"
        self.assertEqual(main([str(self.root), "--contrasts", str(contrasts), "--shape", str(shape), "--max-threads", "4", "--partial", "--resamples", "500"]), 0)
        rows = list(csv.DictReader(contrasts.open()))
        self.assertEqual(list(rows[0]), list(CONTRAST_COLUMNS))
        self.assertEqual((rows[0]["question"], rows[0]["environment"], rows[0]["primary"]), ("RQ1", "chrome", "exploratory"))
        self.assertEqual(len(list(csv.DictReader(shape.open()))), 4)

    def test_the_plan_threshold_applies_by_default(self) -> None:
        contrasts = self.root / "contrasts.csv"
        main([str(self.root), "--contrasts", str(contrasts), "--max-threads", "4", "--partial", "--resamples", "200"])
        meta = json.loads(contrasts.with_suffix(".json").read_text())
        self.assertEqual(meta["foreignCpuThreshold"], 0.25)
        self.assertEqual(meta["excluded"]["foreignCpuSeconds"], 1)

    def test_runs_over_the_foreign_cpu_threshold_are_excluded_and_counted(self) -> None:
        contrasts = self.root / "contrasts.csv"
        main([str(self.root), "--contrasts", str(contrasts), "--foreign-cpu-threshold", "0.1", "--max-threads", "4", "--partial", "--resamples", "500"])
        meta = json.loads(contrasts.with_suffix(".json").read_text())
        self.assertEqual(meta["excluded"], {"foreignCpuSeconds": 1, "strictValidation": 0})
        self.assertEqual(meta["excludedByEnvironment"], {"native": {"foreignCpuSeconds": 1}})
        self.assertEqual(
            meta["excludedByConfiguration"],
            [{"environment": "native", "workload": "filter", "input": "noise", "k": None, "threads": 1, "foreignCpuSeconds": 1}],
        )
        self.assertTrue(meta["partial"])
        self.assertEqual(meta["foreignCpuThreshold"], 0.1)

    def test_configurations_too_short_for_the_clock_are_warned_in_the_sidecar(self) -> None:
        for path in self.root.glob("r*.json"):
            meta = json.loads(path.read_text())
            path.write_text(json.dumps({**meta, "clockResolutionNs": 5_000}))
        contrasts = self.root / "contrasts.csv"
        main([str(self.root), "--contrasts", str(contrasts), "--max-threads", "4", "--partial", "--resamples", "200"])
        meta = json.loads(contrasts.with_suffix(".json").read_text())
        self.assertEqual(meta["clockFactor"], 100)
        self.assertEqual(len(meta["clockWarnings"]), 4)
        self.assertEqual(meta["clockWarnings"][0]["resolutionNs"], 5_000)
        self.assertEqual(meta["clockUnchecked"], 0)
        self.assertEqual(meta["missingAbsolute"], [])

    def test_checksum_conflicts_stop_before_any_table(self) -> None:
        write_run(self.root, "r999", 999, "chrome", "filter", "", 4, 250, checksum="0xcd")
        contrasts = self.root / "contrasts.csv"
        self.assertEqual(main([str(self.root), "--contrasts", str(contrasts), "--max-threads", "4", "--partial"]), 1)
        self.assertFalse(contrasts.exists())

    def test_campaign_metadata_is_copied_into_the_sidecar(self) -> None:
        (self.root / "campaign.json").write_text(json.dumps({"orderSeed": 7, "build": {"commit": "abc"}, "runs": []}))
        contrasts = self.root / "contrasts.csv"
        main([str(self.root), "--contrasts", str(contrasts), "--max-threads", "4", "--partial", "--resamples", "200"])
        meta = json.loads(contrasts.with_suffix(".json").read_text())
        self.assertEqual(meta["campaignOrderSeed"], 7)
        self.assertEqual(meta["campaignBuild"], {"commit": "abc"})


if __name__ == "__main__":
    unittest.main()
