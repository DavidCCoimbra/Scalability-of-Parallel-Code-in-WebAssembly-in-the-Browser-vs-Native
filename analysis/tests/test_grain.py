import json
import tempfile
import unittest
from pathlib import Path

from analysis.configuration import Configuration
from analysis.cutoff import InvalidCutoffCampaign
from analysis.grain import same_build
from analysis.runs import RunSummary
from analysis.scaling.fork_join import ForkJoinCost
from analysis.scaling.grain import Curve, GrainPoint, best_grains, best_rows, grain_points, point_rows

FILTER_8 = Configuration("native", "filter", "noise", None, 8)
LOCAL_8 = Configuration("chrome", "hist-local", "few", 256, 8)
SIDE = 1024
# A U: fine grains pay the fork per task, coarse ones leave threads idle.
U_TIMES = {1: 300.0, 2: 200.0, 4: 100.0, 8: 101.0, 16: 180.0}
ADAPTIVE_NS = 120.0


def runs(configuration: Configuration, grain: int | None, value: float, count: int = 3) -> list[tuple[RunSummary, int | None]]:
    return [(RunSummary(f"{configuration.label}-g{grain}-{index}", configuration, value + index), grain) for index in range(count)]


def sweep(configuration: Configuration) -> list[tuple[RunSummary, int | None]]:
    every = runs(configuration, None, ADAPTIVE_NS)
    for grain, value in U_TIMES.items():
        every += runs(configuration, grain, value)
    return every


def points_of(*configurations: Configuration) -> list[GrainPoint]:
    pairs = [pair for configuration in configurations for pair in sweep(configuration)]
    return grain_points([run for run, _ in pairs], SIDE, {run.run: grain for run, grain in pairs})


class GrainPointsTest(unittest.TestCase):
    def test_runs_are_grouped_by_grain_with_the_adaptive_split_first(self) -> None:
        points = points_of(FILTER_8)
        self.assertEqual([point.label for point in points], ["adaptive", "1", "2", "4", "8", "16"])
        self.assertTrue(all(point.runs == 3 for point in points))
        self.assertTrue(all(point.interval.low <= point.time_ns <= point.interval.high for point in points))

    def test_relative_time_is_against_the_fastest_fixed_grain(self) -> None:
        rows = {row["grain"]: row for row in point_rows(points_of(FILTER_8))}
        self.assertEqual(rows["4"]["relative_to_best"], "1.000")
        self.assertGreater(float(rows["1"]["relative_to_best"]), 2.9)


class BestGrainTest(unittest.TestCase):
    def test_the_minimum_its_flat_region_and_the_adaptive_ratio(self) -> None:
        costs = {"native": ForkJoinCost(30, 10.0)}
        (best,) = best_grains(points_of(FILTER_8), costs)
        self.assertEqual(best.best.grain, 4)
        self.assertEqual([point.grain for point in best.flat], [4, 8])
        (row,) = best_rows([best])
        self.assertEqual((row["flat_from"], row["flat_to"], row["grain_unit"]), (4, 8, "rows"))
        self.assertAlmostEqual(float(row["adaptive_over_best"]), 121.0 / 101.0, places=2)

    def test_the_100f_grain_divides_100_fork_joins_by_the_work_per_unit(self) -> None:
        costs = {"native": ForkJoinCost(30, 10.0)}
        (best,) = best_grains(points_of(FILTER_8), costs)
        unit_ns = best.adaptive.time_ns * 8 / SIDE if best.adaptive else 0.0
        self.assertAlmostEqual(best.grain_100f or 0.0, 100 * 10.0 / unit_ns)

    def test_the_task_cost_spreads_the_finest_grains_extra_time_over_its_extra_tasks(self) -> None:
        (best,) = best_grains(points_of(FILTER_8), {})
        extra_tasks = SIDE / 1 - SIDE / 4
        expected = (best.finest.time_ns - best.best.time_ns) * 8 / extra_tasks
        self.assertEqual(best.finest.grain, 1)
        self.assertAlmostEqual(best.task_cost_ns or 0.0, expected)
        unit_ns = best.adaptive.time_ns * 8 / SIDE if best.adaptive else 0.0
        self.assertAlmostEqual(best.grain_100task or 0.0, 100 * expected / unit_ns)
        self.assertEqual(best_rows([best])[0]["task_cost_ns"], f"{expected:.0f}")

    def test_the_task_cost_interval_brackets_the_estimate(self) -> None:
        (best,) = best_grains(points_of(FILTER_8), {})
        interval = best.task_cost_interval
        self.assertIsNotNone(interval)
        if interval is not None:
            self.assertLessEqual(interval.low, best.task_cost_ns or 0.0)
            self.assertGreaterEqual(interval.high, best.task_cost_ns or 0.0)

    def test_the_flat_region_stops_at_the_first_grain_that_does_not_overlap(self) -> None:
        pairs = sweep(FILTER_8) + runs(FILTER_8, 32, 100.5)
        points = grain_points([run for run, _ in pairs], SIDE, {run.run: grain for run, grain in pairs})
        (best,) = best_grains(points, {})
        self.assertEqual([point.grain for point in best.flat], [4, 8])

    def test_the_local_histogram_counts_its_grain_in_kb(self) -> None:
        curve = Curve("chrome", "hist-local", 256, SIDE, 8)
        self.assertEqual((curve.unit, curve.units), ("KB", SIDE * SIDE / 1024))
        (best,) = best_grains(points_of(LOCAL_8), {})
        self.assertIsNone(best.grain_100f)
        self.assertEqual(best_rows([best])[0]["fork_join_us"], "")


class SameBuildTest(unittest.TestCase):
    def campaign(self, root: Path, name: str, commit: str) -> Path:
        directory = root / name
        directory.mkdir()
        (directory / "campaign.json").write_text(json.dumps({"build": {"commit": commit}}))
        return directory

    def test_campaigns_of_two_builds_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, second = self.campaign(root, "a", "1da6532a"), self.campaign(root, "b", "1da6532a")
            same_build([first, second])
            with self.assertRaises(InvalidCutoffCampaign):
                same_build([first, self.campaign(root, "c", "4dace4db")])


if __name__ == "__main__":
    unittest.main()
