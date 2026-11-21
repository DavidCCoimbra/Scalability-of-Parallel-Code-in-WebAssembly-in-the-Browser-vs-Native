import unittest

from analysis.configuration import Configuration
from analysis.rq2_decomposition import atomic_ratio, cells, decomposition_rows, excess_ratio, local_ratio, rq2_ratio

THREADS = 8


def configuration(environment: str, workload: str, k: int = 16) -> Configuration:
    return Configuration(environment, workload, "few", k, THREADS)


def values(browser: str = "firefox") -> dict[Configuration, list[float]]:
    return {
        configuration(browser, "hist-atomic"): [1010.0] * 3,
        configuration(browser, "hist-local"): [12.0] * 3,
        configuration("native", "hist-atomic"): [1000.0] * 3,
        configuration("native", "hist-local"): [10.0] * 3,
    }


class Rq2DecompositionTest(unittest.TestCase):
    def test_the_rq2_ratio_is_the_atomic_ratio_over_the_local_one(self) -> None:
        groups = cells(values(), THREADS)[0].groups
        self.assertAlmostEqual(atomic_ratio(groups), 1.01)
        self.assertAlmostEqual(local_ratio(groups), 1.2)
        self.assertAlmostEqual(rq2_ratio(groups), 1.01 / 1.2)

    def test_the_excess_compares_what_the_shared_counters_add(self) -> None:
        groups = cells(values(), THREADS)[0].groups
        self.assertAlmostEqual(excess_ratio(groups), (1010 - 12) / (1000 - 10))

    def test_a_slower_local_kernel_lowers_rq2_while_the_excess_stays_near_one(self) -> None:
        rows = {row[3]: float(row[4]) for row in decomposition_rows(values(), THREADS)}
        self.assertLess(rows["rq2"], 0.85)
        self.assertAlmostEqual(rows["excess"], 1.008, places=3)

    def test_only_browsers_with_all_four_cells_at_the_thread_count_are_listed(self) -> None:
        incomplete = values("chrome")
        del incomplete[configuration("native", "hist-local")]
        self.assertEqual(cells(incomplete, THREADS), [])
        self.assertEqual(cells(values(), 4), [])
        self.assertEqual([cell.browser_atomic.environment for cell in cells(values(), THREADS)], ["firefox"])


if __name__ == "__main__":
    unittest.main()
