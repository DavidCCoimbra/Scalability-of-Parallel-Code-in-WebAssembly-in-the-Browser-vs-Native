import unittest

from analysis.pilot.iteration_count import choose_iterations, iteration_agreement
from analysis.pilot.run_count import choose_runs, extrapolated_runs, half_width
from analysis.pilot.warmup import Series


class HalfWidthTest(unittest.TestCase):
    def test_more_runs_give_a_narrower_interval(self) -> None:
        groups = [[0.0 + 0.01 * (i % 7) for i in range(30)], [0.1 + 0.01 * (i % 5) for i in range(30)]]
        wide = half_width(groups, 5, subsamples=10, resamples=200, seed=1)
        narrow = half_width(groups, 30, subsamples=10, resamples=200, seed=1)
        self.assertLess(narrow, wide)

    def test_identical_runs_have_no_width(self) -> None:
        self.assertEqual(half_width([[1.0] * 10, [2.0] * 10], 10, subsamples=3, resamples=50, seed=1), 0.0)


class ChooseRunsTest(unittest.TestCase):
    def test_the_smallest_size_that_meets_the_target_everywhere_and_the_floor(self) -> None:
        widths = {"a": {5: 0.02, 10: 0.04, 15: 0.03}, "b": {5: 0.09, 10: 0.06, 15: 0.04}}
        self.assertEqual(choose_runs(widths, target=0.05, floor=10), 15)

    def test_no_size_meets_the_target(self) -> None:
        self.assertIsNone(choose_runs({"a": {10: 0.2, 20: 0.1}}, target=0.05, floor=10))


class ExtrapolationTest(unittest.TestCase):
    def test_runs_for_a_target_from_a_square_root_fit(self) -> None:
        widths = {5: 0.2, 10: 0.2 / 2**0.5, 20: 0.1}
        self.assertEqual(extrapolated_runs(widths, target=0.05), 80)


class IterationComparisonTest(unittest.TestCase):
    def test_the_first_iterations_are_compared_with_the_others_not_with_themselves(self) -> None:
        series = [Series("native", "filter", None, 8, [5.0] * 5 + [1.1] * 3 + [1.0] * 92)]
        agreement = iteration_agreement(series, {("filter", None): 5}, sizes=[3], tolerance=0.05)
        self.assertEqual(agreement, {3: 0.0})


class IterationsTest(unittest.TestCase):
    def test_a_steady_series_agrees_with_few_iterations(self) -> None:
        series = [Series("native", "filter", None, 8, [5.0] * 5 + [1.0] * 95)]
        agreement = iteration_agreement(series, {("filter", None): 5}, sizes=[1, 5], tolerance=0.01)
        self.assertEqual(agreement, {1: 1.0, 5: 1.0})

    def test_the_smallest_count_whose_runs_mostly_agree(self) -> None:
        self.assertEqual(choose_iterations({1: 0.5, 5: 0.9, 10: 0.97, 20: 1.0}, share=0.95), 10)


if __name__ == "__main__":
    unittest.main()
