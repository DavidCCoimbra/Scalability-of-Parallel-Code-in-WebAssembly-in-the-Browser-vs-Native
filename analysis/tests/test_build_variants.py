import argparse
import unittest
from pathlib import Path

from analysis.extras.build_variants import Series, parse_series
from analysis.configuration import Configuration
from analysis.runs import RunSummary
from analysis.scaling.build_variants import table_rows, variant_points


def runs(environment: str, workload: str, threads: int, values: list[float]) -> list[RunSummary]:
    configuration = Configuration(environment, workload, "noise", None, threads)
    return [RunSummary(f"{environment}{workload}{threads}{i}", configuration, value) for i, value in enumerate(values)]


class BuildVariantsTest(unittest.TestCase):
    def test_a_series_is_a_build_and_a_directory(self) -> None:
        self.assertEqual(parse_series("scalar=data/raw/simd-scalar"), Series("scalar", Path("data/raw/simd-scalar")))

    def test_a_series_without_a_build_is_rejected(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_series("data/raw/simd-scalar")

    def test_only_the_filter_is_kept(self) -> None:
        data = runs("native", "filter", 1, [8.0, 8.0]) + runs("native", "hist-local", 1, [3.0, 3.0])
        (point,) = variant_points("baseline", data)
        self.assertEqual((point.environment, point.threads, point.efficiency), ("native", 1, 1.0))

    def test_times_are_compared_with_the_baseline_and_with_native(self) -> None:
        baseline = variant_points("baseline", runs("native", "filter", 1, [2.0, 2.0]) + runs("chrome", "filter", 1, [3.0, 3.0]))
        scalar = variant_points("scalar", runs("native", "filter", 1, [8.0, 8.0]) + runs("chrome", "filter", 1, [12.0, 12.0]))
        rows = {(row["build"], row["environment"]): row for row in table_rows(baseline + scalar)}
        self.assertEqual(rows[("scalar", "chrome")]["over_baseline"], "4.000")
        self.assertEqual(rows[("scalar", "chrome")]["over_native"], "1.500")
        self.assertEqual(rows[("baseline", "native")]["over_native"], "1.000")

    def test_a_missing_native_or_baseline_leaves_the_ratio_empty(self) -> None:
        scalar = variant_points("scalar", runs("chrome", "filter", 1, [12.0, 12.0]))
        (row,) = table_rows(scalar)
        self.assertEqual((row["over_native"], row["over_baseline"]), ("", ""))

    def test_excess_is_time_above_a_perfect_split(self) -> None:
        data = variant_points("baseline", runs("native", "filter", 1, [8.0, 8.0]) + runs("native", "filter", 2, [5.0, 5.0]))
        rows = {row["threads"]: row for row in table_rows(data)}
        self.assertEqual(rows[2]["excess_ns"], 1)
        self.assertEqual(rows[1]["excess_ns"], 0)

    def test_inputs_are_not_mixed(self) -> None:
        other = [RunSummary(f"few{i}", Configuration("native", "filter", "few", None, 1), 4.0) for i in range(2)]
        data = variant_points("baseline", runs("native", "filter", 1, [8.0, 8.0]) + other)
        self.assertEqual(sorted(row["center_ns"] for row in table_rows(data)), [4, 8])


if __name__ == "__main__":
    unittest.main()
