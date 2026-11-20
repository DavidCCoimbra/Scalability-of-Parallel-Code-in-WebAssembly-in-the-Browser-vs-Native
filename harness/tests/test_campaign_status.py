import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from harness.campaign import CampaignSpec, PlannedRun, plan
from harness.campaign.status import (
    DISCARDED_LAUNCH_PROBLEM,
    CampaignProgress,
    JournalFiles,
    StatusReport,
    campaign_progress,
    format_duration,
)
from harness.context import JsonObject

SPEC: JsonObject = {
    "name": "fake",
    "orderSeed": 3,
    "environments": ["native", "chrome"],
    "workloads": [{"workload": "filter", "input": "noise"}],
    "threads": [1, 2],
    "repetitions": 2,
    "width": 8,
    "height": 8,
    "warmup": 1,
    "iterations": 1,
    "calibration": 1,
    "discardFirstLaunch": True,
}
START = datetime(2026, 11, 9, 10, 0, tzinfo=timezone.utc)
RUN_SECONDS = 60.0


class CampaignStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spec_path = self.root / "fake.json"
        self.spec_path.write_text(json.dumps(SPEC))
        self.results = self.root / "raw"
        self.campaign = self.results / "fake"
        self.runs = plan(CampaignSpec.from_json(SPEC))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def start(self, resumes: int = 0) -> None:
        self.campaign.mkdir(parents=True)
        meta = {
            "name": "fake",
            "plannedRuns": len(self.runs),
            "startedAt": START.isoformat(),
            "runs": [run.run_id for run in self.runs],
        }
        if resumes:
            meta["resumedAt"] = [(START + timedelta(hours=hour + 1)).isoformat() for hour in range(resumes)]
        (self.campaign / "campaign.json").write_text(json.dumps(meta))

    def log(self, run_id: str, environment: str, minute: int, status: str = "done", **extra: object) -> None:
        entry = {
            "runId": run_id,
            "environment": environment,
            "status": status,
            "seconds": RUN_SECONDS,
            "problems": [],
            "discarded": False,
            "loggedAt": (START + timedelta(minutes=minute)).isoformat(),
            **extra,
        }
        with (self.campaign / "campaign.jsonl").open("a") as file:
            file.write(json.dumps(entry) + "\n")

    def log_planned(self, run: PlannedRun, minute: int, status: str = "done", **extra: object) -> None:
        self.log(run.run_id, str(run.environment), minute, status, **extra)

    def progress(self) -> CampaignProgress:
        return campaign_progress(self.spec_path, self.results)

    def report(self, minutes_after_start: int) -> str:
        return StatusReport(self.progress(), START + timedelta(minutes=minutes_after_start)).text

    def test_nothing_run_yet_counts_every_planned_run_as_remaining(self) -> None:
        tally = self.progress().tally
        self.assertEqual((tally.planned, tally.done, tally.failed, tally.remaining), (8, 0, 0, 8))
        text = self.report(0)
        self.assertIn("0.0%", text)
        self.assertIn("not started", text)
        self.assertIn("unknown until a run is logged", text)
        self.assertIn("none yet", text)

    def test_counts_done_failed_and_remaining_overall_and_per_environment(self) -> None:
        self.start()
        self.log_planned(self.runs[0], 1)
        self.log_planned(self.runs[1], 2, status="timeout")
        self.log_planned(self.runs[2], 3)
        progress = self.progress()
        self.assertEqual((progress.tally.done, progress.tally.failed, progress.tally.remaining), (2, 1, 5))
        environments = progress.environments
        self.assertEqual(list(environments), ["native", "chrome"])
        self.assertEqual(sum(tally.done for tally in environments.values()), 2)
        self.assertEqual(sum(tally.planned for tally in environments.values()), 8)
        self.assertIn("37.5%", self.report(4))
        self.assertIn("1 x timeout", self.report(4))

    def test_a_retried_run_counts_by_its_latest_outcome(self) -> None:
        self.start()
        self.log_planned(self.runs[0], 1, status="error")
        self.log_planned(self.runs[0], 2)
        tally = self.progress().tally
        self.assertEqual((tally.done, tally.failed), (1, 0))

    def test_discarded_launches_are_not_progress_and_their_missing_position_is_no_problem(self) -> None:
        self.start()
        self.log("fake-discard1-chrome-filter-noise-n1-r0", "chrome", 1, discarded=True, problems=[DISCARDED_LAUNCH_PROBLEM])
        progress = self.progress()
        self.assertEqual(progress.tally.done, 0)
        self.assertEqual(progress.runs_with_problems, ())
        self.assertIn("problems  none", self.report(2))
        self.assertIn("discarded launch", self.report(2))

    def test_runs_with_problems_are_counted_with_their_problems(self) -> None:
        self.start()
        self.log_planned(self.runs[0], 1, problems=["turbo on", "governor powersave"])
        self.log_planned(self.runs[1], 2, problems=["turbo on"])
        self.log("fake-discard1-chrome-filter-noise-n1-r0", "chrome", 3, discarded=True, problems=[DISCARDED_LAUNCH_PROBLEM, "turbo on"])
        self.assertEqual(len(self.progress().runs_with_problems), 3)
        self.assertIn("3 run(s): 3 x turbo on, 1 x governor powersave", self.report(4))

    def test_eta_is_the_mean_seconds_per_run_times_the_remaining_runs(self) -> None:
        self.start()
        self.log_planned(self.runs[0], 1, seconds=30.0)
        self.log_planned(self.runs[1], 2, seconds=90.0)
        self.log("fake-discard1-chrome-filter-noise-n1-r0", "chrome", 3, discarded=True, seconds=1000.0)
        progress = self.progress()
        self.assertEqual(progress.mean_seconds, RUN_SECONDS)
        text = self.report(10)
        self.assertIn("eta       6m 00s at 60.0 s per run", text)
        self.assertIn("elapsed   10m 00s", text)
        self.assertIn("7m 00s ago", text)

    def test_a_finished_campaign_reports_its_total_duration(self) -> None:
        self.start(resumes=1)
        for minute, run in enumerate(self.runs, start=1):
            self.log_planned(run, minute)
        text = self.report(120)
        self.assertIn("100.0%", text)
        self.assertIn("eta       finished", text)
        self.assertIn("elapsed   8m 00s (finished", text)
        self.assertIn("sessions  2,", text)

    def test_warns_when_campaign_json_lists_another_plan(self) -> None:
        self.start()
        meta = json.loads((self.campaign / "campaign.json").read_text())
        meta["runs"] = ["other-0000"]
        (self.campaign / "campaign.json").write_text(json.dumps(meta))
        self.assertIn("warning", self.report(1))

    def test_reading_never_writes_into_the_results(self) -> None:
        self.start()
        self.log_planned(self.runs[0], 1)
        before = {path: path.stat().st_mtime_ns for path in self.campaign.iterdir()}
        self.report(2)
        JournalFiles.read(self.campaign)
        self.assertEqual({path: path.stat().st_mtime_ns for path in self.campaign.iterdir()}, before)


class DurationTest(unittest.TestCase):
    def test_shows_the_two_largest_units(self) -> None:
        self.assertEqual(format_duration(timedelta(seconds=42)), "42s")
        self.assertEqual(format_duration(timedelta(minutes=3, seconds=5)), "3m 05s")
        self.assertEqual(format_duration(timedelta(hours=1, minutes=2, seconds=59)), "1h 02m")
        self.assertEqual(format_duration(timedelta(days=2, hours=3)), "2d 03h")
        self.assertEqual(format_duration(timedelta(seconds=-5)), "0s")


if __name__ == "__main__":
    unittest.main()
