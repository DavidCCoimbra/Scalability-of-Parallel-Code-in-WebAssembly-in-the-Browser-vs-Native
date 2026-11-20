import math
import unittest

from analysis.configuration import Configuration
from analysis.inference.cells import missing_absolute
from analysis.inference.contrast import Contrast
from analysis.inference.estimation import contrasts
from analysis.inference.family import IncompleteFamily
from analysis.inference.shape import shape_table
from analysis.runs import RunSummary
from analysis.stats.bootstrap import two_sided_p
from analysis.stats.holm import holm_adjusted

SPREAD = (0.9, 1.0, 1.1, 0.95, 1.05, 1.0, 0.98, 1.02, 0.97, 1.03)


def runs(
    environment: str, workload: str, input: str, k: int | None, threads: int, value: float, spread: tuple[float, ...] = SPREAD
) -> list[RunSummary]:
    configuration = Configuration(environment, workload, input, k, threads)
    return [RunSummary(f"{configuration}-{i}", configuration, value * factor) for i, factor in enumerate(spread)]


def histogram_campaign(chrome_atomic_factor: float, threads: tuple[int, ...] = (1, 8)) -> list[RunSummary]:
    data = []
    for k in (1, 4, 16, 256):
        for n in threads:
            for environment in ("native", "chrome", "firefox"):
                atomic = 100.0 * (chrome_atomic_factor if environment == "chrome" else 1.0)
                data += runs(environment, "hist-atomic", "few", k, n, atomic / n)
                data += runs(environment, "hist-local", "few", k, n, 100.0 / n)
    for n in threads:
        data += runs("native", "filter", "noise", None, n, 100.0 / n)
        data += runs("chrome", "filter", "noise", None, n, 300.0 / min(n, 2))
        data += runs("firefox", "filter", "noise", None, n, 200.0 / n)
    return data


class HolmTest(unittest.TestCase):
    def test_adjusted_p_values_follow_holm_step_down(self) -> None:
        adjusted = holm_adjusted([0.01, 0.04, 0.03, 0.005])
        for value, expected in zip(adjusted, [0.03, 0.06, 0.06, 0.02]):
            self.assertAlmostEqual(value, expected)

    def test_adjusted_p_values_never_exceed_one(self) -> None:
        self.assertEqual(holm_adjusted([0.6, 0.9]), [1.0, 1.0])


class PValueTest(unittest.TestCase):
    def test_distribution_on_one_side_of_zero_gets_the_floor(self) -> None:
        self.assertEqual(two_sided_p([0.1, 0.2, 0.3, 0.4]), 1 / 4)

    def test_distribution_centred_on_zero_gets_one(self) -> None:
        self.assertEqual(two_sided_p([-0.2, -0.1, 0.1, 0.2]), 1.0)


class ContrastTest(unittest.TestCase):
    def setUp(self) -> None:
        self.results = contrasts(histogram_campaign(chrome_atomic_factor=2.0), max_threads=8, resamples=2_000)

    def find(
        self, question: str, environment: str, workload: str = "hist-atomic", k: int | None = None, threads: int = 8
    ) -> Contrast:
        return next(
            c for c in self.results
            if (c.question, c.environment, c.workload, c.k, c.threads) == (question, environment, workload, k, threads)
        )

    def test_rq2_is_the_difference_of_log_atomic_over_local_against_native(self) -> None:
        chrome = self.find("RQ2", "chrome", k=4)
        self.assertAlmostEqual(chrome.estimate, math.log(2.0))
        self.assertAlmostEqual(chrome.effect, 2.0)
        firefox = self.find("RQ2", "firefox", k=4)
        self.assertAlmostEqual(firefox.effect, 1.0)

    def test_rq1_is_the_log_speedup_ratio_against_native(self) -> None:
        chrome = self.find("RQ1", "chrome", workload="filter")
        self.assertAlmostEqual(chrome.effect, 0.25)
        firefox = self.find("RQ1", "firefox", workload="filter")
        self.assertAlmostEqual(firefox.effect, 1.0)

    def test_absolute_ratio_compares_browser_time_with_native_time_at_the_same_n(self) -> None:
        one = self.find("ABS", "chrome", workload="filter", threads=1)
        eight = self.find("ABS", "chrome", workload="filter", threads=8)
        self.assertAlmostEqual(one.effect, 3.0)
        self.assertAlmostEqual(eight.effect, 12.0)
        self.assertAlmostEqual(self.find("ABS", "firefox", workload="filter", threads=8).effect, 2.0)

    def test_absolute_ratios_are_exploratory(self) -> None:
        absolute = [c for c in self.results if c.question == "ABS"]
        self.assertTrue(absolute)
        self.assertTrue(all(not c.primary and c.p is None for c in absolute))
        self.assertEqual(len([c for c in absolute if c.workload == "filter"]), 2 * 2)

    def test_primary_family_is_rq2_at_max_n_and_rq1_filter_at_max_n(self) -> None:
        primary = [c for c in self.results if c.primary]
        self.assertEqual(len(primary), 10)
        self.assertTrue(all(c.threads == 8 for c in primary))
        self.assertEqual({c.workload for c in primary if c.question == "RQ1"}, {"filter"})
        self.assertTrue(all(c.p is not None and c.holm_p is not None for c in primary))
        self.assertTrue(all(c.p is None for c in self.results if not c.primary))

    def test_primary_intervals_are_wider_bonferroni_intervals(self) -> None:
        chrome = self.find("RQ2", "chrome", k=4)
        assert chrome.primary_interval is not None
        self.assertLessEqual(chrome.primary_interval[0], chrome.interval[0])
        self.assertGreaterEqual(chrome.primary_interval[1], chrome.interval[1])

    def test_clear_effects_are_rejected_and_null_effects_are_not(self) -> None:
        self.assertTrue(self.find("RQ2", "chrome", k=4).rejected)
        self.assertFalse(self.find("RQ2", "firefox", k=4).rejected)
        self.assertTrue(self.find("RQ1", "chrome", workload="filter").rejected)
        self.assertFalse(self.find("RQ1", "firefox", workload="filter").rejected)

    def test_contrasts_are_reproducible(self) -> None:
        again = contrasts(histogram_campaign(chrome_atomic_factor=2.0), max_threads=8, resamples=2_000)
        self.assertEqual([c.interval for c in again], [c.interval for c in self.results])


class FamilyTest(unittest.TestCase):
    def test_family_other_than_the_planned_ten_is_an_error(self) -> None:
        data = [run for run in histogram_campaign(2.0) if run.configuration.environment != "firefox"]
        with self.assertRaises(IncompleteFamily):
            contrasts(data, max_threads=8, resamples=200)

    def test_max_threads_comes_from_the_plan_not_the_data(self) -> None:
        with self.assertRaises(IncompleteFamily):
            contrasts(histogram_campaign(2.0), max_threads=16, resamples=200)

    def test_partial_data_is_all_exploratory(self) -> None:
        data = [run for run in histogram_campaign(2.0) if run.configuration.environment != "firefox"]
        results = contrasts(data, max_threads=8, partial=True, resamples=200)
        self.assertTrue(results)
        self.assertTrue(all(not c.primary and c.p is None for c in results))

    def test_only_the_noise_filter_is_primary_for_rq1(self) -> None:
        data = histogram_campaign(2.0)
        for environment in ("native", "chrome", "firefox"):
            data += runs(environment, "filter", "few", 4, 1, 100.0) + runs(environment, "filter", "few", 4, 8, 20.0)
        primary = [c for c in contrasts(data, max_threads=8, resamples=200) if c.primary and c.question == "RQ1"]
        self.assertEqual({c.input for c in primary}, {"noise"})


class MissingAbsoluteTest(unittest.TestCase):
    def test_browser_configurations_without_native_at_one_or_max_n_are_listed(self) -> None:
        data = [r for r in histogram_campaign(2.0) if not (r.configuration.environment == "native" and r.configuration.workload == "filter" and r.configuration.threads == 8)]
        missing = missing_absolute(data, max_threads=8)
        self.assertEqual(
            sorted((c.environment, c.workload, c.threads) for c in missing),
            [("chrome", "filter", 8), ("firefox", "filter", 8)],
        )

    def test_complete_data_has_nothing_missing(self) -> None:
        self.assertEqual(missing_absolute(histogram_campaign(2.0), max_threads=8), [])


class ShapeTest(unittest.TestCase):
    def test_symmetric_runs_have_zero_skewness_and_counts(self) -> None:
        (row,) = shape_table(runs("native", "filter", "noise", None, 1, 1.0, spread=(1.0, 2.0, 3.0)))
        self.assertEqual(row.runs, 3)
        self.assertAlmostEqual(row.skewness, 0.0)

    def test_right_skewed_runs_have_positive_skewness(self) -> None:
        (row,) = shape_table(runs("native", "filter", "noise", None, 1, 1.0, spread=(1.0, 2.0, 3.0, 20.0)))
        self.assertGreater(row.skewness, 0)
        self.assertLess(row.log_skewness, row.skewness)


if __name__ == "__main__":
    unittest.main()
