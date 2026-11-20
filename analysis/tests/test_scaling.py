import unittest
from typing import TypeVar

from analysis.configuration import Configuration
from analysis.runs import Row, RunSummary, run_summaries
from analysis.scaling.karp_flatt import karp_flatt_rows, serial_fraction
from analysis.scaling.table import scaling_table
from analysis.stats.bootstrap import bootstrap_interval
from analysis.stats.summary import Summary


T = TypeVar("T")


def known(value: T | None) -> T:
    assert value is not None
    return value


def row(run: str, threads: int, phase: str, ns: int, env: str = "native", k: str = "") -> Row:
    return {
        "run": run,
        "env": env,
        "workload": "filter",
        "input": "noise",
        "k": k,
        "width": "1024",
        "height": "1024",
        "threads": str(threads),
        "phase": phase,
        "ns": str(ns),
    }


def summaries(env: str, threads: int, values: list[float]) -> list[RunSummary]:
    configuration = Configuration(env, "filter", "noise", None, threads)
    return [RunSummary(f"{env}-{threads}-{i}", configuration, value) for i, value in enumerate(values)]


class RunSummaryTest(unittest.TestCase):
    def test_only_measured_iterations_enter_the_run_summary(self) -> None:
        rows = [
            row("a", 2, "calibration-pause", 1_000_000),
            row("a", 2, "calibration-warm", 10),
            row("a", 2, "warmup", 999),
            row("a", 2, "measured", 10),
            row("a", 2, "measured", 30),
            row("a", 2, "measured", 20),
        ]
        (summary,) = run_summaries(rows, Summary.MEDIAN)
        self.assertEqual(summary.value, 20)
        self.assertEqual(summary.configuration, Configuration("native", "filter", "noise", None, 2))

    def test_mean_summary(self) -> None:
        rows = [row("a", 1, "measured", 10), row("a", 1, "measured", 40)]
        self.assertEqual(run_summaries(rows, Summary.MEAN)[0].value, 25)

    def test_one_summary_per_run_and_k_is_parsed(self) -> None:
        rows = [row("a", 1, "measured", 10, k="4"), row("b", 1, "measured", 12, k="4")]
        result = run_summaries(rows, Summary.MEDIAN)
        self.assertEqual([summary.run for summary in result], ["a", "b"])
        self.assertEqual(result[0].configuration.k, 4)


class GeometricCenterTest(unittest.TestCase):
    def test_geometric_mean_is_the_mean_of_the_logs(self) -> None:
        self.assertAlmostEqual(Summary.GEOMETRIC.of([1.0, 100.0]), 10.0)

    def test_analysis_plan_defaults_center_runs_geometrically(self) -> None:
        runs = summaries("native", 1, [100.0, 400.0]) + summaries("native", 2, [50.0, 200.0])
        row = [row for row in scaling_table(runs) if row.configuration.threads == 2][0]
        self.assertAlmostEqual(row.center_ns, 100.0)
        self.assertAlmostEqual(known(row.speedup), 2.0)


class BootstrapTest(unittest.TestCase):
    def test_interval_is_reproducible_and_contains_the_estimate(self) -> None:
        low_a, high_a = bootstrap_interval([[1.0, 2.0, 3.0, 4.0]], lambda groups: sum(groups[0]) / 4, seed=1)
        low_b, high_b = bootstrap_interval([[1.0, 2.0, 3.0, 4.0]], lambda groups: sum(groups[0]) / 4, seed=1)
        self.assertEqual((low_a, high_a), (low_b, high_b))
        self.assertLessEqual(low_a, 2.5)
        self.assertGreaterEqual(high_a, 2.5)

    def test_identical_runs_give_a_zero_width_interval(self) -> None:
        self.assertEqual(bootstrap_interval([[5.0] * 6], lambda groups: groups[0][0]), (5.0, 5.0))


class PercentileTest(unittest.TestCase):
    def test_bounds_round_to_the_nearest_order_statistic(self) -> None:
        values = iter(float(v) for v in range(51))
        low, high = bootstrap_interval([[0.0]], lambda groups: next(values), resamples=51)
        self.assertEqual((low, high), (1.0, 49.0))


class ScalingTest(unittest.TestCase):
    def test_speedup_is_relative_to_the_same_environment(self) -> None:
        runs = (
            summaries("native", 1, [100.0, 100.0, 100.0])
            + summaries("native", 4, [25.0, 25.0, 25.0])
            + summaries("chrome", 1, [300.0, 300.0, 300.0])
            + summaries("chrome", 4, [150.0, 150.0, 150.0])
        )
        table = {(row.configuration.environment, row.configuration.threads): row for row in scaling_table(runs)}
        self.assertAlmostEqual(known(table[("native", 4)].speedup), 4.0)
        self.assertAlmostEqual(known(table[("native", 4)].efficiency), 1.0)
        self.assertAlmostEqual(known(table[("chrome", 4)].speedup), 2.0)
        self.assertAlmostEqual(known(table[("chrome", 4)].efficiency), 0.5)
        self.assertEqual(table[("chrome", 1)].speedup, 1.0)
        self.assertEqual(table[("native", 4)].runs, 3)
        self.assertEqual(table[("native", 4)].baseline_runs, 3)
        low, high = known(table[("native", 4)].speedup_interval)
        self.assertAlmostEqual(low, 4.0)
        self.assertAlmostEqual(high, 4.0)

    def test_interval_widens_with_spread_between_runs(self) -> None:
        runs = summaries("native", 1, [90.0, 100.0, 110.0, 105.0]) + summaries("native", 2, [45.0, 55.0, 50.0, 52.0])
        row = [row for row in scaling_table(runs) if row.configuration.threads == 2][0]
        low, high = known(row.speedup_interval)
        self.assertLess(low, known(row.speedup))
        self.assertGreater(high, known(row.speedup))

    def test_configurations_without_a_single_thread_baseline_have_no_speedup(self) -> None:
        (row,) = scaling_table(summaries("firefox", 8, [10.0, 11.0]))
        self.assertIsNone(row.speedup)
        self.assertIsNone(row.speedup_interval)
        self.assertAlmostEqual(row.center_ns, 110**0.5)


class KarpFlattTest(unittest.TestCase):
    def test_amdahl_speedup_gives_back_its_serial_fraction(self) -> None:
        for threads in (2, 4, 8):
            amdahl = 1 / (0.1 + 0.9 / threads)
            self.assertAlmostEqual(serial_fraction(amdahl, threads), 0.1)

    def test_ideal_speedup_has_no_serial_fraction(self) -> None:
        self.assertAlmostEqual(serial_fraction(8.0, 8), 0.0)

    def test_rows_skip_n1_and_take_the_interval_from_the_speedup_ends(self) -> None:
        row = {"environment": "native", "workload": "filter", "input": "noise", "k": ""}
        scaling = [
            {**row, "threads": "1", "speedup": "1", "speedup_low": "1", "speedup_high": "1"},
            {**row, "threads": "8", "speedup": "6.4", "speedup_low": "6", "speedup_high": "7"},
        ]
        (result,) = karp_flatt_rows(scaling)
        self.assertAlmostEqual(result.serial_fraction, (1 / 6.4 - 1 / 8) / (7 / 8))
        self.assertEqual(result.interval, (serial_fraction(7.0, 8), serial_fraction(6.0, 8)))


if __name__ == "__main__":
    unittest.main()
