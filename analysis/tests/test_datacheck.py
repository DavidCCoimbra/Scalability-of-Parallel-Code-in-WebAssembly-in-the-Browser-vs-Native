import tempfile
import unittest
from pathlib import Path

from analysis.configuration import Configuration
from analysis.quality.foreign_cpu import FOREIGN_CPU_THRESHOLD
from analysis.quality.order_drift import OrderedValue, order_drifts
from analysis.quality.report import quality_report
from analysis.stats.spearman import spearman
from analysis.tests.test_results import write_run


class SpearmanTest(unittest.TestCase):
    def test_a_monotonic_rise_is_one(self) -> None:
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [10.0, 20.0, 30.0, 40.0]), 1.0)

    def test_a_reversed_order_is_minus_one(self) -> None:
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [4.0, 3.0, 2.0, 1.0]), -1.0)

    def test_ties_share_their_average_rank(self) -> None:
        self.assertAlmostEqual(spearman([1, 2, 3], [1.0, 1.0, 2.0]), 0.8660254, places=6)


class DriftTest(unittest.TestCase):
    def test_configurations_whose_runs_trend_with_the_order_are_flagged(self) -> None:
        trending = Configuration("chrome", "filter", "noise", None, 8)
        flat = Configuration("native", "filter", "noise", None, 8)
        observations = {
            trending: [OrderedValue(position, 100.0 + position) for position in range(12)],
            flat: [OrderedValue(position, 100.0 + (position % 2)) for position in range(12)],
        }
        flagged = order_drifts(observations, limit=0.5, minimum_runs=10)
        self.assertEqual([item.configuration for item in flagged], [trending])
        self.assertAlmostEqual(flagged[0].rho, 1.0)


class ReportTest(unittest.TestCase):
    def test_a_checksum_conflict_blocks_the_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "r1", 1, "native", "filter", "", 1, 100, checksum="0xab")
            write_run(root, "r2", 2, "chrome", "filter", "", 1, 120, checksum="0xcd")
            report = quality_report(root)
        self.assertTrue(report.blocking)
        self.assertIn("Checksum conflicts: 1", report.text())

    def test_runs_failing_strict_validation_are_left_out_of_the_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(12):
                write_run(root, f"r{index}", index, "native", "filter", "", 1, 100 + index)
            report = quality_report(root)
        self.assertFalse(report.blocking)
        self.assertIn("Runs failing strict validation: 12", report.text())
        self.assertIn("  - native filter N=1: 12", report.text())
        self.assertIn("at least 10 runs): 0", report.text())

    def test_runs_set_aside_for_a_re_run_are_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "r1", 1, "native", "filter", "", 1, 100)
            excluded = root / "excluded"
            excluded.mkdir()
            (excluded / "r0.json").write_text("{}")
            (excluded / "README.md").write_text("reason")
            report = quality_report(root)
        self.assertEqual(report.replaced, 1)
        self.assertIn("Runs replaced by a re-run (kept in `excluded/`): 1", report.text())


class ThresholdTest(unittest.TestCase):
    def test_the_foreign_cpu_threshold_is_fixed_from_the_pilots(self) -> None:
        self.assertEqual(FOREIGN_CPU_THRESHOLD, 0.25)


if __name__ == "__main__":
    unittest.main()
