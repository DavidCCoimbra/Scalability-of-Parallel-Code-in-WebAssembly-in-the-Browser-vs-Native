import json
import tempfile
import unittest
from pathlib import Path

from analysis.configuration import Configuration
from analysis.campaign import passes_of
from analysis.quality.clock import (
    CLOCK_FACTOR,
    clock_resolution,
    clock_warnings,
    run_passes,
    run_resolutions,
    unchecked_configurations,
)
from analysis.runs import RunSummary

FAST = Configuration("firefox", "filter", "noise", None, 8)
SLOW = Configuration("firefox", "filter", "noise", None, 1)


class ClockResolutionTest(unittest.TestCase):
    def test_browser_runs_record_it_in_the_page_metadata_and_native_in_the_build(self) -> None:
        self.assertEqual(clock_resolution({"clockResolutionNs": 20_000}), 20_000)
        self.assertEqual(clock_resolution({"build": {"clockResolutionNs": 41}}), 41)
        self.assertIsNone(clock_resolution({"build": "unavailable"}))

    def test_resolutions_are_read_from_each_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.json").write_text(json.dumps({"clockResolutionNs": 5_000}))
            self.assertEqual(run_resolutions(Path(tmp), {"a"}), {"a": 5_000})


class PassesTest(unittest.TestCase):
    def test_runs_stored_before_passes_ran_one(self) -> None:
        self.assertEqual(passes_of({}), 1)
        self.assertEqual(passes_of({"passes": 16}), 16)
        self.assertEqual(passes_of({"passes": True}), 1)

    def test_passes_are_read_from_each_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.json").write_text(json.dumps({"passes": 4}))
            (Path(tmp) / "b.json").write_text(json.dumps({}))
            self.assertEqual(run_passes(Path(tmp), {"a", "b"}), {"a": 4, "b": 1})


class ClockWarningTest(unittest.TestCase):
    def test_default_factor_is_a_hundred(self) -> None:
        self.assertEqual(CLOCK_FACTOR, 100)

    def test_configurations_too_short_for_the_clock_are_flagged(self) -> None:
        runs = [RunSummary("f1", FAST, 1_200_000.0), RunSummary("f2", FAST, 1_600_000.0)]
        runs += [RunSummary("s1", SLOW, 9_000_000.0)]
        resolutions = {"f1": 20_000, "f2": 20_000, "s1": 20_000}
        (warning,) = clock_warnings(runs, resolutions)
        self.assertEqual(warning.configuration, FAST)
        self.assertEqual((warning.median_ns, warning.resolution_ns), (1_400_000.0, 20_000))

    def test_the_check_is_on_the_timed_sample_of_k_passes(self) -> None:
        runs = [RunSummary("f1", FAST, 15_000.0), RunSummary("f2", FAST, 15_000.0)]
        resolutions = {"f1": 20_000, "f2": 20_000}
        self.assertEqual(clock_warnings(runs, resolutions, passes={"f1": 256, "f2": 256}), [])
        (warning,) = clock_warnings(runs, resolutions, passes={"f1": 64, "f2": 64})
        self.assertEqual((warning.median_ns, warning.passes), (960_000.0, 64))
        self.assertEqual(warning.as_json()["passes"], 64)
        self.assertIn("64 passes", warning.message())

    def test_one_pass_keeps_the_warning_as_before(self) -> None:
        runs = [RunSummary("f1", FAST, 10.0)]
        (warning,) = clock_warnings(runs, {"f1": 20_000})
        self.assertNotIn("passes", warning.as_json())
        self.assertNotIn("passes", warning.message())

    def test_runs_without_a_known_resolution_are_not_flagged_but_counted_as_unchecked(self) -> None:
        runs = [RunSummary("f1", FAST, 10.0), RunSummary("s1", SLOW, 1e9)]
        self.assertEqual(clock_warnings(runs, {"s1": 1}), [])
        self.assertEqual(unchecked_configurations(runs, {"s1": 1}), [FAST])


if __name__ == "__main__":
    unittest.main()
