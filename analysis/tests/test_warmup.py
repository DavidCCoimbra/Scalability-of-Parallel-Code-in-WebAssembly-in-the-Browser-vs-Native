import csv
import tempfile
import unittest
from pathlib import Path

from analysis.pilot.warmup import (
    WarmupRule,
    Series,
    campaign_warmups,
    load_series,
    observed_warmup,
)

RULE = WarmupRule()


def steady(n: int, value: float = 100.0) -> list[float]:
    return [value] * n


class ObservedWarmupTest(unittest.TestCase):
    def test_a_flat_series_needs_no_warmup(self) -> None:
        self.assertEqual(observed_warmup(steady(100), RULE), 0)

    def test_a_slow_start_ends_when_most_of_the_next_window_is_steady(self) -> None:
        series = [150.0] * 30 + steady(70)
        self.assertEqual(observed_warmup(series, RULE), 26)

    def test_noise_around_the_steady_state_is_not_warmup(self) -> None:
        series = [100.0 * (1.1 if i % 2 else 0.9) for i in range(100)]
        self.assertEqual(observed_warmup(series, RULE), 0)

    def test_a_slow_first_iteration_counts_as_warmup(self) -> None:
        series = [500.0] + steady(99)
        self.assertEqual(observed_warmup(series, RULE), 1)

    def test_an_early_iteration_within_the_steady_state_range_is_not_a_spike(self) -> None:
        series = [100.0, 101.0] + steady(98)
        self.assertEqual(observed_warmup(series, RULE), 0)

    def test_a_run_that_never_settles_has_no_warmup(self) -> None:
        series = [200.0] * 60 + steady(40)
        self.assertIsNone(observed_warmup(series, RULE))


class CampaignWarmupTest(unittest.TestCase):
    def test_each_workload_takes_the_worst_environment_with_margin_and_floor(self) -> None:
        series = [
            Series("firefox", "hist-local", 1, 8, [150.0] * 30 + steady(70)),
            Series("native", "hist-local", 1, 8, steady(100)),
            Series("chrome", "filter", None, 8, steady(100)),
        ]
        self.assertEqual(campaign_warmups(series, RULE), {("hist-local", 1): 39, ("filter", None): 5})

    def test_a_run_that_never_settles_stops_the_choice(self) -> None:
        series = [Series("firefox", "filter", None, 8, [200.0] * 60 + steady(40))]
        with self.assertRaises(ValueError):
            campaign_warmups(series, RULE)


class LoadSeriesTest(unittest.TestCase):
    def test_measured_iterations_are_read_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.csv"
            with path.open("w", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["env", "workload", "input", "k", "threads", "phase", "iter", "ns"])
                writer.writerow(["chrome", "hist-local", "few", "4", "8", "calibration-warm", "0", "1"])
                writer.writerow(["chrome", "hist-local", "few", "4", "8", "measured", "1", "20"])
                writer.writerow(["chrome", "hist-local", "few", "4", "8", "measured", "0", "10"])
            (series,) = load_series(Path(tmp))
        self.assertEqual(series, Series("chrome", "hist-local", 4, 8, [10.0, 20.0]))


if __name__ == "__main__":
    unittest.main()
