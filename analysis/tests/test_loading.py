import tempfile
import unittest
from pathlib import Path

from analysis.loading import load_campaign
from analysis.tests.test_results import write_run


class LoadingTest(unittest.TestCase):
    def test_the_sequential_references_are_kept_apart_from_the_scaling_curves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "r0", 0, "native", "filter", "", 1, 1000)
            write_run(root, "r1", 1, "native", "filter", "", 4, 260)
            write_run(root, "r2", 2, "native", "filter-seq", "", 1, 990)
            write_run(root, "r3", 3, "native", "hist-seq", "4", 1, 500)
            campaign = load_campaign(root)
        self.assertEqual([row["run"] for row in campaign.rows], ["r0", "r1"])
        self.assertEqual([row["run"] for row in campaign.sequential_rows], ["r2", "r3"])


if __name__ == "__main__":
    unittest.main()
