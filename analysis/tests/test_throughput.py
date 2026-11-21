import io
import unittest

from analysis.configuration import Configuration
from analysis.runs import RunSummary
from analysis.scaling.throughput import COLUMNS, throughput_table, write_throughput

PIXELS = 1_000_000


def runs(environment: str, threads: int, values: list[float]) -> list[RunSummary]:
    configuration = Configuration(environment, "filter", "noise", None, threads)
    return [RunSummary(f"{environment}-{threads}-{index}", configuration, value) for index, value in enumerate(values)]


class ThroughputTest(unittest.TestCase):
    def table(self) -> dict[tuple[str, int], dict[str, str]]:
        measured = runs("native", 1, [2e6] * 4) + runs("native", 2, [1e6] * 4) + runs("chrome", 2, [4e6] * 4)
        pixels = {run.configuration: PIXELS for run in measured}
        output = io.StringIO()
        write_throughput(throughput_table(measured, pixels), output)
        header, *lines = [line.split(",") for line in output.getvalue().splitlines()]
        self.assertEqual(tuple(header), COLUMNS)
        rows = [dict(zip(header, line)) for line in lines]
        return {(row["environment"], int(row["threads"])): row for row in rows}

    def test_time_per_pixel_and_pixels_per_second_come_from_the_centre(self) -> None:
        row = self.table()[("native", 1)]
        self.assertEqual((row["ns_per_pixel"], row["megapixels_per_second"]), ("2", "500.0"))

    def test_the_absolute_speedup_divides_the_native_one_thread_time(self) -> None:
        table = self.table()
        self.assertEqual(table[("native", 1)]["absolute_speedup"], "1")
        self.assertEqual(table[("native", 2)]["absolute_speedup"], "2")
        self.assertEqual(table[("chrome", 2)]["absolute_speedup"], "0.5")

    def test_without_a_native_one_thread_cell_there_is_no_absolute_speedup(self) -> None:
        measured = runs("chrome", 2, [4e6] * 4)
        [row] = throughput_table(measured, {measured[0].configuration: PIXELS})
        self.assertIsNone(row.absolute)
        self.assertEqual(row.cells()[-3:], ["", "", ""])


if __name__ == "__main__":
    unittest.main()
