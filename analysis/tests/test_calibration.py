import unittest

from analysis.calibration import calibration_rows
from analysis.runs import Row


def row(run: str, phase: str, ns: int, workload: str = "filter", env: str = "chrome", probe: str = "broadcast") -> Row:
    return {"run": run, "env": env, "workload": workload, "threads": "8", "phase": phase, "probe": probe, "ns": str(ns)}


class CalibrationTest(unittest.TestCase):
    def test_medians_and_means_are_taken_per_run_first(self) -> None:
        rows = [row("a", "calibration-warm", ns) for ns in (100_000, 100_000, 400_000)]
        rows += [row("b", "calibration-warm", ns) for ns in (120_000, 120_000, 120_000)]
        table = {tuple(line[:5]): line[5:] for line in calibration_rows(rows)}
        self.assertEqual(table[("chrome", "all", "8", "broadcast", "warm")], ["2", "110.0", "160.0"])

    def test_every_workload_is_also_listed_on_its_own_and_other_phases_are_ignored(self) -> None:
        rows = [
            row("a", "calibration-cold", 460_000),
            row("b", "calibration-cold", 64_000, workload="hist-local"),
            row("a", "measured", 5_000_000),
            row("a", "calibration-pause", 1_000_000),
        ]
        table = {(line[1], line[4]): line[6] for line in calibration_rows(rows)}
        self.assertEqual(table, {("all", "cold"): "262.0", ("filter", "cold"): "460.0", ("hist-local", "cold"): "64.0"})

    def test_environments_come_in_the_study_order(self) -> None:
        rows = [row("a", "calibration-warm", 1, env="firefox"), row("b", "calibration-warm", 1, env="native")]
        self.assertEqual([line[0] for line in calibration_rows(rows) if line[1] == "all"], ["native", "firefox"])


if __name__ == "__main__":
    unittest.main()
