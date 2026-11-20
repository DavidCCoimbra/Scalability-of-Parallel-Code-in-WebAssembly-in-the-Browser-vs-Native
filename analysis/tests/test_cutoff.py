import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from analysis.configuration import Configuration
from analysis.cutoff import InvalidCutoffCampaign, main, size_campaigns, square_side
from analysis.runs import Row, RunSummary
from analysis.scaling.crossing import (
    BREAK_EVEN_SPEEDUP,
    WORTH_IT_EFFICIENCY,
    Criterion,
    Placement,
    crossing,
    estimate_rows,
    estimates,
)
from analysis.scaling.cutoff import CutoffPoint, cutoff_points, table_rows
from analysis.scaling.fork_join import (
    LOOSE_SHARE,
    MODEL_COLUMNS,
    RULE_OF_THUMB_SHARE,
    ForkJoinCost,
    ModelPrediction,
    fork_join_costs,
    model_rows,
    predictions,
)
from analysis.stats.bootstrap import Interval
from harness.native import CSV_HEADER

SIDES = (512, 1024, 2048, 4096, 8192)
FILTER = Configuration("native", "filter", "noise", None, 1)
LOCAL_256 = Configuration("native", "hist-local", "few", 256, 1)


def summaries(configuration: Configuration, values: list[float]) -> list[RunSummary]:
    return [RunSummary(f"{configuration.label}-{index}", configuration, value) for index, value in enumerate(values)]


def point(side: int, speedup: float, threads: int = 8, spread: float = 0.0, t1_ns: float | None = None) -> CutoffPoint:
    t1 = t1_ns if t1_ns is not None else 1_000.0 * side * side / 1024
    configuration = FILTER.at_threads(threads)
    return CutoffPoint(side, configuration, 30, t1, t1 / speedup, speedup, Interval(speedup - spread, speedup + spread))


def curve(speedups: list[float], threads: int = 8, spread: float = 0.0) -> list[CutoffPoint]:
    return [point(side, speedup, threads, spread) for side, speedup in zip(SIDES, speedups)]


class CutoffPointsTest(unittest.TestCase):
    def test_times_speedup_and_work_per_region_come_from_the_same_size(self) -> None:
        runs = summaries(FILTER, [8_000.0, 8_000.0]) + summaries(FILTER.at_threads(4), [4_000.0, 4_000.0])
        by_threads = {p.threads: p for p in cutoff_points(1024, runs)}
        four = by_threads[4]
        self.assertEqual((four.side, four.t1_ns), (1024, 8_000.0))
        self.assertAlmostEqual(four.tn_ns, 4_000.0)
        self.assertAlmostEqual(four.speedup, 2.0)
        self.assertAlmostEqual(four.efficiency, 0.5)
        self.assertAlmostEqual(four.work_us, 8.0)
        self.assertEqual(by_threads[1].speedup, 1.0)

    def test_only_the_filter_and_the_local_histogram_at_k_256_are_kept(self) -> None:
        k1 = Configuration("native", "hist-local", "few", 1, 1)
        atomic = Configuration("native", "hist-atomic", "few", 256, 1)
        runs = summaries(FILTER, [1.0]) + summaries(LOCAL_256, [1.0]) + summaries(k1, [1.0]) + summaries(atomic, [1.0])
        kept = {(p.configuration.workload, p.configuration.k) for p in cutoff_points(512, runs)}
        self.assertEqual(kept, {("filter", None), ("hist-local", 256)})

    def test_configurations_without_n_1_are_dropped(self) -> None:
        self.assertEqual(cutoff_points(512, summaries(FILTER.at_threads(8), [1.0, 1.0])), [])

    def test_table_rows_are_ordered_by_environment_workload_threads_and_side(self) -> None:
        points = [point(2048, 3.0), point(512, 0.7), point(512, 1.0, threads=1)]
        rows = table_rows(points)
        self.assertEqual([(row["threads"], row["side"]) for row in rows], [(1, 512), (8, 512), (8, 2048)])
        self.assertEqual(rows[1]["speedup"], "0.700")
        self.assertEqual(rows[1]["work_us"], "256.0")


class CrossingTest(unittest.TestCase):
    def test_break_even_is_interpolated_on_log_size(self) -> None:
        found = crossing(curve([0.5, 0.8, 1.5, 3.0, 5.0]), lambda p: p.speedup, BREAK_EVEN_SPEEDUP)
        self.assertEqual(found.placement, Placement.CROSSED)
        fraction = (1.0 - 0.8) / (1.5 - 0.8)
        assert found.side is not None and found.work_us is not None
        self.assertAlmostEqual(found.side, 1024 * 2**fraction)
        self.assertAlmostEqual(math.log2(found.work_us / 1024), math.log2(4096 / 1024) * fraction)

    def test_a_curve_that_pays_at_every_size_or_never_is_placed_outside_the_range(self) -> None:
        self.assertEqual(crossing(curve([1.2, 2, 3, 4, 5]), lambda p: p.speedup, 1.0).placement, Placement.PAYS_AT_EVERY_SIZE)
        self.assertEqual(crossing(curve([0.1, 0.2, 0.3, 0.4, 0.9]), lambda p: p.speedup, 1.0).placement, Placement.NEVER_PAYS)

    def test_reaching_the_threshold_exactly_counts_as_paying(self) -> None:
        found = crossing(curve([0.5, 1.0, 2, 3, 4]), lambda p: p.speedup, 1.0)
        self.assertEqual(found.side, 1024)

    def test_a_curve_that_dips_again_takes_the_crossing_nearest_the_largest_size(self) -> None:
        found = crossing(curve([1.5, 0.5, 2.0, 0.9, 3.0]), lambda p: p.speedup, 1.0)
        assert found.side is not None
        self.assertTrue(4096 < found.side < 8192)

    def test_worth_it_asks_for_half_of_the_threads(self) -> None:
        self.assertEqual(WORTH_IT_EFFICIENCY, 0.5)
        self.assertEqual(Criterion.WORTH_IT.threshold(8), 4.0)
        self.assertEqual(Criterion.BREAK_EVEN.threshold(8), 1.0)

    def test_estimates_cover_both_criteria_for_every_n_above_1_with_a_side_interval(self) -> None:
        points = curve([0.5, 0.8, 1.5, 3.0, 5.0], spread=0.4) + curve([1.0] * 5, threads=1)
        items = estimates(points)
        self.assertEqual([item.criterion for item in items], [Criterion.BREAK_EVEN, Criterion.WORTH_IT])
        break_even, worth_it = estimate_rows(items)
        self.assertTrue(int(break_even["side_low"]) < int(break_even["side"]) < int(break_even["side_high"]))
        self.assertEqual((worth_it["threshold_speedup"], worth_it["placement"]), ("4.000", "crossed"))
        self.assertEqual(int(worth_it["side"]), round(4096 * math.sqrt(2)))


class ForkJoinTest(unittest.TestCase):
    @staticmethod
    def calibration(run: str, env: str, threads: int, values: list[int]) -> list[Row]:
        return [{"run": run, "env": env, "threads": str(threads), "phase": "calibration-warm", "ns": str(v)} for v in values]

    def test_cost_is_the_median_over_runs_of_each_run_median_of_warm_calls(self) -> None:
        rows = self.calibration("a", "chrome", 8, [100, 110, 900]) + self.calibration("b", "chrome", 8, [120, 130, 140])
        rows += self.calibration("c", "chrome", 8, [50, 60, 70]) + self.calibration("d", "chrome", 4, [1, 1, 1])
        rows += [{"run": "a", "env": "chrome", "threads": "8", "phase": "calibration-cold", "ns": "5000"}]
        self.assertEqual(fork_join_costs(rows), {"chrome": ForkJoinCost(3, 110.0)})

    def test_schema_2_rows_are_filtered_by_probe_and_old_rows_count_as_broadcast(self) -> None:
        old = self.calibration("a", "chrome", 8, [100])
        broadcast = [{**row, "probe": "broadcast"} for row in self.calibration("b", "chrome", 8, [300])]
        par_iter = [{**row, "probe": "par-iter"} for row in self.calibration("b", "chrome", 8, [7])]
        rows = old + broadcast + par_iter
        self.assertEqual(fork_join_costs(rows), {"chrome": ForkJoinCost(2, 200.0)})
        self.assertEqual(fork_join_costs(rows, probe="par-iter"), {"chrome": ForkJoinCost(1, 7.0)})

    def test_the_model_predicts_the_work_at_which_fork_join_is_one_percent_then_five(self) -> None:
        self.assertEqual((RULE_OF_THUMB_SHARE.fraction, LOOSE_SHARE.fraction), (0.01, 0.05))
        reference = point(8192, 7.0, t1_ns=1_520_000.0)
        prediction = ModelPrediction(reference, ForkJoinCost(30, 10_000.0))
        self.assertAlmostEqual(prediction.work_at_share_ns(RULE_OF_THUMB_SHARE), 99 * 8 * 10_000.0)
        self.assertAlmostEqual(prediction.work_at_share_ns(LOOSE_SHARE), 19 * 8 * 10_000.0)
        for share in (RULE_OF_THUMB_SHARE, LOOSE_SHARE):
            tn = prediction.work_at_share_ns(share) / 8 + prediction.fork_join_ns
            self.assertAlmostEqual(prediction.fork_join_ns / tn, share.fraction)
        self.assertAlmostEqual(prediction.break_even_ns, 10_000.0 * 8 / 7)
        self.assertAlmostEqual(prediction.worth_it_ns, 80_000.0)
        self.assertAlmostEqual(prediction.side_for(1_520_000.0), 8192)
        self.assertAlmostEqual(prediction.side_for(380_000.0), 4096)

    def test_predictions_use_the_largest_size_at_n_8_of_each_environment_with_a_cost(self) -> None:
        points = [point(4096, 6.0), point(8192, 7.0), point(8192, 1.0, threads=1)]
        (prediction,) = predictions(points, {"native": ForkJoinCost(3, 7_500.0), "chrome": ForkJoinCost(3, 1.0)})
        self.assertEqual((prediction.reference.side, prediction.threads), (8192, 8))
        (row,) = model_rows([prediction])
        self.assertEqual(tuple(row), MODEL_COLUMNS)
        self.assertEqual(
            (row["fork_join_us"], row["work_1pct_us"], row["work_5pct_us"], row["model_worth_it_us"]),
            ("7.5", "5940.0", "1140.0", "60.0"),
        )


def write_run(directory: Path, run: str, threads: int, side: int, values: list[int], checksum: str = "0x1") -> None:
    lines = [CSV_HEADER]
    for phase, samples in (("calibration-warm", [7_000, 8_000, 9_000]), ("measured", values)):
        lines += [
            f"native,filter,noise,,{side},{side},24301,{threads},{phase},{index},{ns},0x{side:016x},{checksum}"
            for index, ns in enumerate(samples)
        ]
    (directory / f"{run}.csv").write_text("\n".join(lines) + "\n")
    (directory / f"{run}.json").write_text(json.dumps({"environment": "native", "passes": 4}))


def synthetic_campaign(root: Path, side: int, t1: int, t8: int) -> Path:
    directory = root / f"cutoff-{side}"
    directory.mkdir()
    for repetition in range(3):
        write_run(directory, f"cutoff-{side}-one-{repetition}", 1, side, [t1, t1 + 10])
        write_run(directory, f"cutoff-{side}-eight-{repetition}", 8, side, [t8, t8 + 10])
    return directory


class CommandTest(unittest.TestCase):
    def test_the_tables_are_written_from_one_directory_per_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            small = synthetic_campaign(root, 512, 100_000, 125_000)
            large = synthetic_campaign(root, 1024, 400_000, 80_000)
            table, found, model = root / "table.csv", root / "estimates.csv", root / "model.csv"
            arguments = [str(large), str(small), "--table", str(table), "--estimates", str(found), "--model", str(model)]
            self.assertEqual(main(arguments), 0)
            rows = list(csv.DictReader(table.open()))
            self.assertEqual([(row["side"], row["threads"]) for row in rows], [("512", "1"), ("1024", "1"), ("512", "8"), ("1024", "8")])
            (break_even, _) = list(csv.DictReader(found.open()))
            self.assertEqual(break_even["placement"], "crossed")
            self.assertTrue(512 < int(break_even["side"]) < 1024)
            (prediction,) = list(csv.DictReader(model.open()))
            self.assertEqual((prediction["fork_join_runs"], prediction["fork_join_us"]), ("6", "8.0"))

    def test_two_directories_of_the_same_size_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = synthetic_campaign(root, 512, 100, 50)
            second = root / "copy"
            second.mkdir()
            for path in first.iterdir():
                (second / path.name).write_text(path.read_text())
            with self.assertRaises(InvalidCutoffCampaign):
                size_campaigns([first, second])

    def test_a_campaign_must_hold_one_square_size(self) -> None:
        rows: list[Row] = [{"width": "512", "height": "256"}]
        with self.assertRaises(InvalidCutoffCampaign):
            square_side(rows, Path("x"))
        with self.assertRaises(InvalidCutoffCampaign):
            square_side([{"width": "512", "height": "512"}, {"width": "1024", "height": "1024"}], Path("x"))
        self.assertEqual(square_side([{"width": "512", "height": "512"}], Path("x")), 512)


if __name__ == "__main__":
    unittest.main()
