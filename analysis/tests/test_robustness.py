import math
import unittest
from dataclasses import replace

from analysis.inference.robustness import log_by_repetition, paired_log_ratios, repetition_of, robustness_checks
from analysis.runs import RunSummary
from analysis.stats.cliff import cliffs_delta
from analysis.stats.mann_whitney import average_ranks, mann_whitney_u
from analysis.tests.test_inference import histogram_campaign, runs


def with_repetitions(data: list[RunSummary]) -> list[RunSummary]:
    return [replace(run, run=f"{run.run}-r{run.run.rsplit('-', 1)[1]}") for run in data]


class MannWhitneyTest(unittest.TestCase):
    # By hand: the treatment wins all 9 pairs, U = 9, mean 4.5, variance 9 / 12 * 7 = 5.25, so
    # z = (4.5 - 0.5) / sqrt(5.25) = 1.7457 and p = erfc(z / sqrt 2) = 0.08086.
    def test_separated_groups_by_hand(self) -> None:
        result = mann_whitney_u([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        self.assertEqual(result.u, 9.0)
        self.assertAlmostEqual(result.z, 1.74574, places=5)
        self.assertAlmostEqual(result.p, 0.080856, places=6)

    # By hand: pooled ranks 1, (2, 2, 2) -> 3, (3, 3) -> 5.5, (4, 4) -> 7.5, 5 -> 9; the treatment's
    # rank sum is 32.5, U = 32.5 - 15 = 17.5; ties give sum(t^3 - t) = 24 + 6 + 6 = 36, variance
    # 20 / 12 * (10 - 36 / 72) = 15.833, z = (7.5 - 0.5) / 3.9791 = 1.7592, p = 0.07855.
    def test_ties_by_hand(self) -> None:
        result = mann_whitney_u([1.0, 2.0, 2.0, 3.0], [2.0, 3.0, 4.0, 4.0, 5.0])
        self.assertEqual(result.u, 17.5)
        self.assertAlmostEqual(result.z, 1.75919, places=5)
        self.assertAlmostEqual(result.p, 0.078546, places=6)

    # The example of the scipy.stats.mannwhitneyu documentation: males 19, 22, 16, 29, 24 against
    # females 20, 11, 17, 12; U(males) = 17, asymptotic two-sided p = 0.1113 (exact p = 0.1111).
    def test_documentation_example(self) -> None:
        result = mann_whitney_u([20.0, 11.0, 17.0, 12.0], [19.0, 22.0, 16.0, 29.0, 24.0])
        self.assertEqual(result.u, 17.0)
        self.assertAlmostEqual(result.p, 0.111347, places=6)

    def test_u_of_both_groups_sums_to_the_number_of_pairs(self) -> None:
        baseline, treatment = [0.8, 1.2, 1.9, 0.7], [1.1, 0.9, 2.3]
        self.assertEqual(mann_whitney_u(baseline, treatment).u + mann_whitney_u(treatment, baseline).u, 12.0)
        self.assertAlmostEqual(mann_whitney_u(baseline, treatment).p, mann_whitney_u(treatment, baseline).p)

    def test_u_and_cliffs_delta_measure_the_same_dominance(self) -> None:
        baseline, treatment = [1.0, 2.0, 2.0, 3.0], [2.0, 3.0, 4.0, 4.0, 5.0]
        u = mann_whitney_u(baseline, treatment).u
        self.assertAlmostEqual(2 * u / 20 - 1, cliffs_delta(baseline, treatment))

    def test_all_values_tied_gives_p_one(self) -> None:
        self.assertEqual(mann_whitney_u([1.0, 1.0], [1.0, 1.0, 1.0]).p, 1.0)

    def test_average_ranks_share_tied_ranks(self) -> None:
        self.assertEqual(average_ranks([3.0, 1.0, 3.0, 2.0]), [3.5, 1.0, 3.5, 2.0])


class PairingTest(unittest.TestCase):
    def test_repetition_comes_from_the_run_id(self) -> None:
        self.assertEqual(repetition_of("campaign-0002-native-hist-atomic-k4-n7-r19"), 19)
        with self.assertRaises(ValueError):
            repetition_of("campaign-0002-native")

    def test_ratios_pair_the_same_repetition_and_drop_the_unmatched(self) -> None:
        top = with_repetitions(runs("native", "filter", "noise", None, 1, 8.0, (1.0, 2.0, 4.0)))
        bottom = with_repetitions(runs("native", "filter", "noise", None, 8, 1.0, (1.0, 1.0)))
        values = log_by_repetition(top + bottom)
        ratios = paired_log_ratios(values, top[0].configuration, bottom[0].configuration)
        self.assertEqual([round(math.exp(r), 9) for r in ratios], [8.0, 16.0])


class RobustnessTest(unittest.TestCase):
    def test_chrome_penalty_is_rejected_and_agrees_with_the_bootstrap(self) -> None:
        checks = robustness_checks(with_repetitions(histogram_campaign(2.0)), resamples=500, repairings=20)
        self.assertEqual(len(checks), 10)
        chrome = [c for c in checks if c.contrast.question == "RQ2" and c.contrast.environment == "chrome"]
        self.assertTrue(all(c.rejected and c.cliffs_delta == 1.0 for c in chrome))
        self.assertTrue(all(math.isclose(c.browser_median / c.native_median, 2.0) for c in chrome))
        self.assertTrue(all(c.agrees and c.same_decision_share is not None for c in checks))


if __name__ == "__main__":
    unittest.main()
