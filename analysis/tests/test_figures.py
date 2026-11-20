import math
import unittest

from analysis.configuration import Configuration
from analysis.figures.points import absolute_ratios, rq2_ratios, scaling_curves
from analysis.figures.spread import CAMPAIGN_PANELS, Spread, panel_spreads
from analysis.runs import RunSummary


def runs(environment: str, workload: str, k: int | None, threads: int, values: list[float]) -> list[RunSummary]:
    configuration = Configuration(environment, workload, "noise" if k is None else "few", k, threads)
    return [RunSummary(f"{environment}{workload}{k}{threads}{i}", configuration, value) for i, value in enumerate(values)]


class FiguresTest(unittest.TestCase):
    def test_scaling_curves_hold_speedup_per_environment_and_workload(self) -> None:
        data = runs("native", "filter", None, 1, [8.0, 8.0]) + runs("native", "filter", None, 2, [4.0, 4.0])
        curves = scaling_curves(data)
        (point_1, point_2) = curves[("filter", None)]["native"]
        self.assertEqual((point_1.threads, point_1.speedup), (1, 1.0))
        self.assertEqual(point_2.threads, 2)
        self.assertAlmostEqual(point_2.speedup, 2.0)
        self.assertAlmostEqual(point_2.efficiency, 1.0)

    def test_absolute_ratio_is_browser_over_native_at_each_n(self) -> None:
        data = runs("native", "filter", None, 8, [2.0, 2.0]) + runs("chrome", "filter", None, 8, [3.0, 3.0])
        (point,) = absolute_ratios(data)[("filter", None)]["chrome"]
        self.assertAlmostEqual(point.value, 1.5)
        self.assertAlmostEqual(point.low, 1.5)

    def test_rq2_ratio_is_atomic_over_local_per_environment(self) -> None:
        data = runs("firefox", "hist-atomic", 4, 8, [10.0, 10.0]) + runs("firefox", "hist-local", 4, 8, [2.0, 2.0])
        (point,) = rq2_ratios(data)[4]["firefox"]
        self.assertAlmostEqual(point.value, 5.0)
        self.assertAlmostEqual(math.log(point.high), math.log(5.0))


class SpreadTest(unittest.TestCase):
    def test_panel_holds_run_values_in_milliseconds_per_present_environment(self) -> None:
        data = runs("firefox", "filter", None, 1, [3e6, 1e6, 2e6]) + runs("native", "filter", None, 1, [5e5])
        data += runs("chrome", "filter", None, 8, [1e6])
        spreads = panel_spreads(CAMPAIGN_PANELS[0], data)
        self.assertEqual([s.environment for s in spreads], ["native", "firefox"])
        self.assertEqual(spreads[1].milliseconds, [1.0, 2.0, 3.0])

    def test_quartiles_are_the_inclusive_quartiles(self) -> None:
        self.assertEqual(Spread("native", [1.0, 2.0, 3.0, 4.0, 5.0]).quartiles, (2.0, 3.0, 4.0))

    def test_cells_give_spread_relative_to_the_median(self) -> None:
        cells = Spread("native", [1.0, 2.0, 3.0, 4.0, 6.0]).cells()
        self.assertEqual(cells[0], 5)
        self.assertEqual(cells[-2:], ["0.6667", "2.0000"])


if __name__ == "__main__":
    unittest.main()
