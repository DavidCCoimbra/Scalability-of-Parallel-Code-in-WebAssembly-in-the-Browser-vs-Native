import unittest

from analysis.stats.cliff import cliffs_delta
from analysis.stats.ratio import ratio_of_geometric_means


class CompareTest(unittest.TestCase):
    def test_ratio_of_geometric_means_with_an_interval(self) -> None:
        baseline = [10.0, 10.0, 10.0, 10.0]
        treatment = [12.0, 12.0, 12.0, 12.0]
        ratio = ratio_of_geometric_means(baseline, treatment, resamples=200, seed=1)
        self.assertAlmostEqual(ratio.value, 1.2)
        self.assertAlmostEqual(ratio.interval.low, 1.2)
        self.assertAlmostEqual(ratio.interval.high, 1.2)

    def test_cliffs_delta_is_one_when_every_treatment_run_is_slower(self) -> None:
        self.assertEqual(cliffs_delta([1.0, 2.0], [3.0, 4.0]), 1.0)
        self.assertEqual(cliffs_delta([3.0, 4.0], [1.0, 2.0]), -1.0)


if __name__ == "__main__":
    unittest.main()
