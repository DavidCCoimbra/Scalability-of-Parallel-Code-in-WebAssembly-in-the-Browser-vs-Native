import getpass
import json
import sys
import tempfile
import unittest
from collections.abc import Sequence, Set
from pathlib import Path
from typing import Any

from harness.campaign import (
    Campaign,
    CampaignSpec,
    EnvironmentNotReady,
    ExecutionResult,
    HostEnvironment,
    InputKind,
    PlannedRun,
    Workload,
    WorkloadSpec,
    build_identity,
    plan,
)
from harness.context import UNAVAILABLE, JsonObject, RunEnvironment
from harness.campaign.identity import crate_versions, glue_digest
from harness.launcher import FIREFOX_PREFS, RunStatus
from harness.native import CSV_HEADER
from harness.shield import UNIT_NAME

SPEC = {
    "name": "mini",
    "orderSeed": 7,
    "environments": ["native", "chrome", "firefox"],
    "workloads": [
        {"workload": "filter", "input": "noise"},
        {"workload": "hist-atomic", "input": "few", "k": 4},
        {"workload": "hist-local", "input": "few", "k": 4},
    ],
    "threads": [1, 2, 4, 8],
    "repetitions": 2,
    "width": 256,
    "height": 256,
    "warmup": 1,
    "iterations": 2,
    "calibration": 10,
}


def spec(**overrides: object) -> CampaignSpec:
    return CampaignSpec.from_json({**SPEC, **overrides})


class FakeExecutor:
    def __init__(self, results: Path, failing: Set[int] = frozenset()):
        self.results = results
        self.failing = failing
        self.calls: list[PlannedRun] = []

    def execute(self, run: PlannedRun, results: Path) -> ExecutionResult:
        self.calls.append(run)
        results.mkdir(parents=True, exist_ok=True)
        if run.position in self.failing:
            (results / f"{run.run_id}.error.json").write_text(json.dumps({"error": "boom"}))
            return ExecutionResult(RunStatus.ERROR, 0.1, "boom")
        (results / f"{run.run_id}.csv").write_text("x\n")
        (results / f"{run.run_id}.json").write_text("{}")
        return ExecutionResult(RunStatus.DONE, 0.1, None)


class FakeEnvironment:
    def __init__(self, problems: Sequence[str] = ()):
        self.problems_found = list(problems)
        self.checked: list[str] = []
        self.recorded: list[Path] = []

    def problems(self, mask: str) -> list[str]:
        self.checked.append(mask)
        return self.problems_found

    def record(self, directory: Path, problems: list[str]) -> Path:
        self.recorded.append(directory)
        return directory / "sysinfo.json"


class RecordingServer:
    port = 0

    def __init__(self) -> None:
        self.serving: Path | None = None
        self.started: list[Path] = []

    def start(self, results: Path) -> int:
        self.serving = results
        self.started.append(results)
        return self.port

    def stop(self) -> None:
        self.serving = None


class ServedExecutor(FakeExecutor):
    def __init__(self, results: Path, server: RecordingServer):
        super().__init__(results)
        self.server = server
        self.mismatches: list[str] = []

    def execute(self, run: PlannedRun, results: Path) -> ExecutionResult:
        if self.server.serving != results:
            self.mismatches.append(run.run_id)
        return super().execute(run, results)


class SpecTest(unittest.TestCase):
    def test_reads_the_campaign_parameters(self) -> None:
        campaign = spec()
        self.assertEqual(campaign.order_seed, 7)
        self.assertEqual(campaign.workloads[1], WorkloadSpec(Workload.HIST_ATOMIC, InputKind.FEW, 4))
        self.assertEqual(campaign.threads, (1, 2, 4, 8))
        self.assertIsNone(campaign.cpus)
        self.assertFalse(campaign.discard_first_launch)
        self.assertFalse(campaign.strict)

    def test_rejects_unknown_environments_and_bad_values(self) -> None:
        overrides: tuple[dict[str, object], ...] = (
            {"environments": ["safari"]},
            {"repetitions": 0},
            {"threads": []},
            {"threads": [0]},
            {"workloads": [{"workload": "hist-atomic", "input": "few"}]},
            {"workloads": [{"workload": "filter", "input": "noise", "k": 4}]},
            {"name": "has space"},
        )
        for override in overrides:
            with self.assertRaises(ValueError, msg=override):
                spec(**override)

    def test_names_that_make_run_ids_longer_than_the_server_accepts_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            spec(name="a-very-long-campaign-name-for-the-pilot-of-october")
        spec(name="pilot-warmup")

    def test_strict_campaigns_need_a_cpu_mask(self) -> None:
        with self.assertRaises(ValueError):
            spec(strict=True)
        spec(strict=True, cpus="0,2,4,6,8,10,12,14")

    def test_scope_user_dollar_user_resolves_to_the_current_user(self) -> None:
        self.assertEqual(spec(scopeUser="$USER").resolved_scope_user, getpass.getuser())
        self.assertEqual(spec(scopeUser="david").resolved_scope_user, "david")
        self.assertIsNone(spec().resolved_scope_user)

    def test_unknown_keys_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            spec(repetitons=3)

    def test_workload_query_matches_the_runner_options(self) -> None:
        campaign = spec()
        noise = PlannedRun(0, RunEnvironment.NATIVE, campaign.workloads[0], 2, 0, "mini")
        few = PlannedRun(1, RunEnvironment.CHROME, campaign.workloads[1], 8, 1, "mini")
        self.assertEqual(
            campaign.query(noise),
            "workload=filter&input=noise&threads=2&width=256&height=256&warmup=1&iters=2&calibration=10",
        )
        self.assertEqual(
            campaign.query(few),
            "workload=hist-atomic&input=few&k=4&threads=8&width=256&height=256&warmup=1&iters=2&calibration=10",
        )


    def test_a_workload_warmup_overrides_the_campaign_warmup(self) -> None:
        campaign = spec(workloads=[{"workload": "filter", "input": "noise", "warmup": 12}, {"workload": "hist-atomic", "input": "few", "k": 4}])
        own = PlannedRun(0, RunEnvironment.FIREFOX, campaign.workloads[0], 8, 0, "mini")
        shared = PlannedRun(1, RunEnvironment.FIREFOX, campaign.workloads[1], 8, 0, "mini")
        self.assertIn("&warmup=12&", campaign.query(own))
        self.assertIn("&warmup=1&", campaign.query(shared))
        workloads = campaign.to_json()["workloads"]
        assert isinstance(workloads, list)
        self.assertEqual(workloads[0], {"workload": "filter", "input": "noise", "warmup": 12})

    def test_a_workload_warmup_cannot_be_negative(self) -> None:
        with self.assertRaises(ValueError):
            spec(workloads=[{"workload": "filter", "input": "noise", "warmup": -1}])

    def test_height_per_thread_scales_the_image_with_n(self) -> None:
        campaign = spec(heightPerThread=1024)
        two = PlannedRun(0, RunEnvironment.NATIVE, campaign.workloads[0], 2, 0, "mini")
        eight = PlannedRun(1, RunEnvironment.NATIVE, campaign.workloads[0], 8, 0, "mini")
        self.assertIn("&width=256&height=2048&", campaign.query(two))
        self.assertIn("&height=8192&", campaign.query(eight))
        self.assertEqual(campaign.to_json()["heightPerThread"], 1024)

    def test_height_per_thread_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            spec(heightPerThread=0)

    def test_a_build_variant_picks_its_own_native_binary(self) -> None:
        self.assertTrue(spec().native_binary.as_posix().endswith("bench/target/release/native"))
        self.assertTrue(spec(build="avx2").native_binary.as_posix().endswith("bench/target/avx2/release/native"))
        self.assertEqual(spec(build="scalar").to_json()["build"], "scalar")

    def test_hybrid_is_off_unless_the_spec_asks_for_it(self) -> None:
        self.assertFalse(spec().hybrid)
        self.assertTrue(spec(hybrid=True).hybrid)

    def test_an_unknown_build_variant_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            spec(build="avx512")

    def test_the_new_workloads_are_accepted(self) -> None:
        campaign = spec(workloads=[
            {"workload": "hist-atomic-private", "input": "few", "k": 4},
            {"workload": "hist-atomic-packed", "input": "few", "k": 4},
            {"workload": "sort", "input": "noise"},
        ])
        self.assertEqual([w.workload for w in campaign.workloads], ["hist-atomic-private", "hist-atomic-packed", "sort"])

class PassesTest(unittest.TestCase):
    LOCAL_AND_FILTER = [{"workload": "filter", "input": "noise"}, {"workload": "hist-local", "input": "few", "k": 256}]

    def run_of(self, campaign: CampaignSpec, index: int) -> PlannedRun:
        return PlannedRun(index, RunEnvironment.NATIVE, campaign.workloads[index], 8, 0, "mini")

    def test_one_pass_leaves_the_query_and_the_stored_spec_as_before(self) -> None:
        campaign = spec()
        self.assertEqual(campaign.passes, 1)
        self.assertNotIn("passes", campaign.query(self.run_of(campaign, 0)))
        self.assertNotIn("passes", campaign.to_json())
        self.assertNotIn("comment", campaign.to_json())
        self.assertEqual(spec(passes=1).to_json(), campaign.to_json())

    def test_campaign_passes_reach_the_query_and_the_stored_spec(self) -> None:
        campaign = spec(workloads=self.LOCAL_AND_FILTER, passes=16, comment="K from the mini-pilot")
        self.assertTrue(campaign.query(self.run_of(campaign, 1)).endswith("&calibration=10&passes=16"))
        self.assertEqual(campaign.to_json()["passes"], 16)
        self.assertEqual(campaign.to_json()["comment"], "K from the mini-pilot")
        self.assertEqual(CampaignSpec.from_json(campaign.to_json()), campaign)

    def test_a_workload_passes_overrides_the_campaign_passes(self) -> None:
        workloads = [{"workload": "filter", "input": "noise", "passes": 4}, self.LOCAL_AND_FILTER[1]]
        campaign = spec(workloads=workloads, passes=2)
        self.assertTrue(campaign.query(self.run_of(campaign, 0)).endswith("&passes=4"))
        self.assertTrue(campaign.query(self.run_of(campaign, 1)).endswith("&passes=2"))

    def test_passes_must_be_a_positive_integer(self) -> None:
        for passes in (0, -1, True, 2.0, "2"):
            with self.assertRaises(ValueError, msg=repr(passes)):
                spec(workloads=self.LOCAL_AND_FILTER, passes=passes)
        for passes in (0, True):
            with self.assertRaises(ValueError, msg=repr(passes)):
                spec(workloads=[{"workload": "filter", "input": "noise", "passes": passes}])

    def test_workloads_that_accumulate_or_sort_take_only_one_pass(self) -> None:
        for workload in ({"workload": "hist-atomic", "input": "few", "k": 4}, {"workload": "sort", "input": "noise"}):
            with self.assertRaises(ValueError, msg=workload):
                spec(workloads=[workload], passes=2)
            with self.assertRaises(ValueError, msg=workload):
                spec(workloads=[{**workload, "passes": 2}])
            spec(workloads=[workload], passes=1)

    def test_a_grain_reaches_the_query_and_the_run_id_and_round_trips(self) -> None:
        workloads = [{"workload": "filter", "input": "noise", "grain": 4}, {"workload": "filter", "input": "noise"}]
        campaign = spec(workloads=workloads)
        fixed, adaptive = self.run_of(campaign, 0), self.run_of(campaign, 1)
        self.assertIn("&grain=4", campaign.query(fixed))
        self.assertNotIn("grain", campaign.query(adaptive))
        self.assertIn("-noise-g4-", fixed.run_id)
        self.assertNotEqual(fixed.run_id.split("-", 2)[2], adaptive.run_id.split("-", 2)[2])
        self.assertEqual(campaign.to_json()["workloads"], [workloads[0], {"workload": "filter", "input": "noise"}])
        self.assertEqual(CampaignSpec.from_json(campaign.to_json()), campaign)

    def test_only_the_filter_and_the_local_histogram_take_a_positive_grain(self) -> None:
        spec(workloads=[{"workload": "hist-local", "input": "few", "k": 256, "grain": 64}])
        for workload in ({"workload": "hist-atomic", "input": "few", "k": 4, "grain": 4}, {"workload": "filter", "input": "noise", "grain": 0}):
            with self.assertRaises(ValueError, msg=workload):
                spec(workloads=[workload])

    def test_a_pitch_reaches_the_query_and_the_run_id_for_the_filter_only(self) -> None:
        workloads = [{"workload": "filter", "input": "noise", "pitch": 4160}]
        campaign = spec(workloads=workloads)
        padded = self.run_of(campaign, 0)
        self.assertIn("&pitch=4160", campaign.query(padded))
        self.assertIn("-noise-p4160-", padded.run_id)
        self.assertEqual(CampaignSpec.from_json(campaign.to_json()), campaign)
        for workload in ({"workload": "hist-local", "input": "few", "k": 4, "pitch": 64}, {"workload": "filter", "input": "noise", "pitch": 0}):
            with self.assertRaises(ValueError, msg=workload):
                spec(workloads=[workload])

    def test_a_palette_reaches_the_query_and_the_run_id_for_few_colors_only(self) -> None:
        campaign = spec(workloads=[{"workload": "hist-atomic-packed", "input": "few", "k": 4, "palette": "consecutive"}])
        run = self.run_of(campaign, 0)
        self.assertIn("&k=4&palette=consecutive", campaign.query(run))
        self.assertIn("-k4-consecutive-", run.run_id)
        self.assertEqual(CampaignSpec.from_json(campaign.to_json()), campaign)
        for workload in ({"workload": "filter", "input": "noise", "palette": "spread"}, {"workload": "hist-atomic", "input": "few", "k": 4, "palette": "rainbow"}):
            with self.assertRaises(ValueError, msg=workload):
                spec(workloads=[workload])

    def test_the_comment_must_be_text(self) -> None:
        with self.assertRaises(ValueError):
            spec(comment=3)


class PlanTest(unittest.TestCase):
    def test_every_combination_appears_once_per_repetition(self) -> None:
        runs = plan(spec())
        self.assertEqual(len(runs), 3 * 3 * 4 * 2)
        keys = {(run.environment, run.workload, run.threads, run.repetition) for run in runs}
        self.assertEqual(len(keys), len(runs))
        self.assertEqual([run.position for run in runs], list(range(len(runs))))

    def test_run_ids_are_unique_unit_names_that_carry_the_position(self) -> None:
        runs = plan(spec())
        self.assertEqual(len({run.run_id for run in runs}), len(runs))
        self.assertTrue(all(UNIT_NAME.fullmatch(run.run_id) for run in runs))
        self.assertTrue(runs[0].run_id.startswith("mini-0000-"))

    def test_order_depends_only_on_the_seed(self) -> None:
        self.assertEqual(plan(spec()), plan(spec()))
        self.assertNotEqual(plan(spec()), plan(spec(orderSeed=8)))

    def test_environments_are_interleaved_not_grouped(self) -> None:
        runs = plan(spec())
        first_quarter = {run.environment for run in runs[: len(runs) // 4]}
        self.assertEqual(first_quarter, {"native", "chrome", "firefox"})


class CampaignTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.results = Path(self.tmp.name) / "mini"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def campaign(
        self,
        executor: FakeExecutor,
        build: JsonObject | None = None,
        retry_failed: bool = False,
        environment: FakeEnvironment | None = None,
        **overrides: object,
    ) -> Campaign:
        return Campaign(
            spec(**overrides),
            self.results,
            {name: executor for name in ("native", "chrome", "firefox")},
            build=build or {"commit": "abc"},
            retry_failed=retry_failed,
            environment=environment,
        )

    def log(self) -> list[dict[str, Any]]:
        return [json.loads(line) for line in (self.results / "campaign.jsonl").read_text().splitlines()]

    def test_runs_the_whole_plan_in_order_and_logs_every_run(self) -> None:
        executor = FakeExecutor(self.results)
        summary = self.campaign(executor).run()
        self.assertEqual([run.position for run in executor.calls], list(range(72)))
        self.assertEqual((summary.done, summary.failed, summary.skipped), (72, 0, 0))
        self.assertTrue(summary.ok)
        entries = self.log()
        self.assertEqual(len(entries), 72)
        self.assertEqual(entries[0]["position"], 0)
        self.assertEqual(entries[0]["status"], "done")
        self.assertIn("query", entries[0])

    def test_failed_runs_are_logged_with_their_message_and_the_campaign_goes_on(self) -> None:
        executor = FakeExecutor(self.results, failing={3})
        summary = self.campaign(executor).run()
        self.assertEqual((summary.done, summary.failed), (71, 1))
        failed = [entry for entry in self.log() if entry["status"] == "error"]
        self.assertEqual(len(failed), 1)
        self.assertEqual((failed[0]["position"], failed[0]["message"]), (3, "boom"))

    def test_resume_skips_runs_that_already_left_files(self) -> None:
        first = FakeExecutor(self.results, failing={5})
        runs = plan(spec())
        self.results.mkdir(parents=True)
        for run in runs[:10]:
            first.execute(run, self.results)
        second = FakeExecutor(self.results)
        summary = self.campaign(second).run()
        self.assertEqual([run.position for run in second.calls], list(range(10, 72)))
        self.assertEqual((summary.skipped, summary.earlier_failures), (9, 1))

    def test_resume_counts_earlier_failures_and_does_not_retry_them(self) -> None:
        self.campaign(FakeExecutor(self.results, failing={5})).run()
        again = FakeExecutor(self.results)
        summary = self.campaign(again).run()
        self.assertEqual(again.calls, [])
        self.assertEqual((summary.skipped, summary.earlier_failures), (71, 1))
        self.assertFalse(summary.ok)

    def test_retry_failed_keeps_the_failure_record_and_runs_it_again(self) -> None:
        self.campaign(FakeExecutor(self.results, failing={5})).run()
        failed_id = plan(spec())[5].run_id
        again = FakeExecutor(self.results)
        summary = self.campaign(again, retry_failed=True).run()
        self.assertEqual([run.position for run in again.calls], [5])
        self.assertTrue((self.results / "failed" / f"{failed_id}.error.json").exists())
        self.assertTrue(summary.ok)

    def test_resume_with_a_different_build_is_refused(self) -> None:
        self.campaign(FakeExecutor(self.results)).run()
        with self.assertRaises(ValueError):
            self.campaign(FakeExecutor(self.results), build={"commit": "def"}).run()

    def test_metadata_records_the_seed_spec_and_plan(self) -> None:
        self.campaign(FakeExecutor(self.results)).run()
        meta = json.loads((self.results / "campaign.json").read_text())
        self.assertEqual(meta["orderSeed"], 7)
        self.assertEqual(meta["plannedRuns"], 72)
        self.assertEqual(meta["spec"]["repetitions"], 2)
        self.assertEqual(meta["build"], {"commit": "abc"})
        self.assertIn("startedAt", meta)
        self.assertEqual(meta["runs"][0], plan(spec())[0].run_id)

    def test_a_different_spec_cannot_resume_into_the_same_directory(self) -> None:
        self.campaign(FakeExecutor(self.results)).run()
        with self.assertRaises(ValueError):
            self.campaign(FakeExecutor(self.results), orderSeed=8).run()

    def test_discarded_first_launch_runs_once_per_browser_outside_the_plan(self) -> None:
        executor = FakeExecutor(self.results)
        self.campaign(executor, discardFirstLaunch=True).run()
        discarded = [run for run in executor.calls if run.discarded]
        self.assertEqual(sorted(run.environment for run in discarded), ["chrome", "firefox"])
        self.assertEqual(executor.calls[:2], discarded)
        self.assertTrue((self.results / "discarded").is_dir())
        self.assertEqual(len([run for run in executor.calls if not run.discarded]), 72)
        logged = [entry for entry in self.log() if entry["discarded"]]
        self.assertEqual(sorted(entry["environment"] for entry in logged), ["chrome", "firefox"])

    def test_discarded_browser_launches_post_to_the_directory_they_wait_on(self) -> None:
        server = RecordingServer()
        executor = ServedExecutor(self.results, server)
        campaign = Campaign(
            spec(discardFirstLaunch=True),
            self.results,
            {name: executor for name in ("native", "chrome", "firefox")},
            server=server,
            build={"commit": "abc"},
        )
        campaign.run()
        self.assertEqual(executor.mismatches, [])
        self.assertEqual(server.started, [self.results / "discarded", self.results])
        self.assertFalse(any(path.name.startswith("mini-discard") for path in self.results.glob("*.csv")))

    def test_strict_campaigns_log_validation_problems(self) -> None:
        executor = FakeExecutor(self.results)
        self.campaign(executor, environment=FakeEnvironment(), strict=True, cpus="0,2").run()
        self.assertTrue(all(entry["problems"] for entry in self.log()))

    def test_strict_campaign_refuses_an_unprepared_machine_and_records_it(self) -> None:
        executor = FakeExecutor(self.results)
        environment = FakeEnvironment(["turbo is on, not off"])
        with self.assertRaises(EnvironmentNotReady) as error:
            self.campaign(executor, environment=environment, strict=True, cpus="0,2").run()
        self.assertIn("turbo is on", str(error.exception))
        self.assertEqual(executor.calls, [])
        self.assertEqual(environment.recorded, [self.results / "sysinfo"])

    def test_strict_campaign_refuses_a_browser_that_is_not_the_pinned_version(self) -> None:
        executor = FakeExecutor(self.results)
        build: JsonObject = {"commit": "abc", "browsers": {"firefox": "Mozilla Firefox 160.0"}}
        campaign = self.campaign(executor, build=build, environment=FakeEnvironment(), strict=True, cpus="0,2")
        campaign.pinned = {"firefox": "158.0"}
        with self.assertRaises(EnvironmentNotReady) as error:
            campaign.run()
        self.assertIn("firefox is Mozilla Firefox 160.0, not the pinned 158.0", str(error.exception))
        self.assertIn("harness/browsers.py", str(error.exception))
        self.assertEqual(executor.calls, [])

    def test_strict_campaign_refuses_a_browser_whose_version_was_not_read(self) -> None:
        executor = FakeExecutor(self.results)
        build: JsonObject = {"commit": "abc", "browsers": {"chrome": "Google Chrome for Testing 155.0.8059.84"}}
        campaign = self.campaign(executor, build=build, environment=FakeEnvironment(), strict=True, cpus="0,2")
        campaign.pinned = {"chrome": "155.0.8059.84", "firefox": "158.0"}
        with self.assertRaises(EnvironmentNotReady) as error:
            campaign.run()
        self.assertIn("firefox reported no version", str(error.exception))

    def test_strict_campaign_accepts_the_pinned_browser_versions(self) -> None:
        executor = FakeExecutor(self.results)
        build: JsonObject = {
            "commit": "abc",
            "browsers": {"chrome": "Google Chrome for Testing 155.0.8059.84", "firefox": "Mozilla Firefox 158.0"},
        }
        campaign = self.campaign(executor, build=build, environment=FakeEnvironment(), strict=True, cpus="0,2")
        campaign.pinned = {"chrome": "155.0.8059.84", "firefox": "158.0"}
        self.assertEqual(campaign.run().done, 72)

    def test_strict_campaign_checks_the_machine_again_on_every_resume(self) -> None:
        environment = FakeEnvironment()
        self.campaign(FakeExecutor(self.results), environment=environment, strict=True, cpus="0,2").run()
        self.campaign(FakeExecutor(self.results), environment=environment, strict=True, cpus="0,2").run()
        self.assertEqual(environment.checked, ["0,2", "0,2"])

    def test_a_refused_start_does_not_count_as_a_resume(self) -> None:
        good = FakeEnvironment()
        self.campaign(FakeExecutor(self.results), environment=good, strict=True, cpus="0,2").run()
        with self.assertRaises(EnvironmentNotReady):
            self.campaign(FakeExecutor(self.results), environment=FakeEnvironment(["smt is on, not off"]), strict=True, cpus="0,2").run()
        meta = json.loads((self.results / "campaign.json").read_text())
        self.assertEqual(meta.get("resumedAt", []), [])

    def test_strict_campaign_without_an_environment_gate_is_refused(self) -> None:
        with self.assertRaises(EnvironmentNotReady):
            self.campaign(FakeExecutor(self.results), strict=True, cpus="0,2").run()

    def test_discarded_launch_is_redone_in_every_session_with_its_own_id(self) -> None:
        first, second = FakeExecutor(self.results), FakeExecutor(self.results)
        self.campaign(first, discardFirstLaunch=True).run()
        self.campaign(second, discardFirstLaunch=True).run()
        first_ids = {run.run_id for run in first.calls if run.discarded}
        second_ids = {run.run_id for run in second.calls if run.discarded}
        self.assertEqual(len(second_ids), 2)
        self.assertTrue(first_ids.isdisjoint(second_ids))


class BuildIdentityTest(unittest.TestCase):
    def test_the_runtime_crates_are_read_from_the_lock_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "Cargo.lock"
            lock.write_text(
                '[[package]]\nname = "rayon-core"\nversion = "1.13.0"\n\n'
                '[[package]]\nname = "libc"\nversion = "0.2.1"\n\n'
                '[[package]]\nname = "wasm-bindgen-rayon"\nversion = "1.3.0"\n'
            )
            self.assertEqual(crate_versions(lock), {"rayon-core": "1.13.0", "wasm-bindgen-rayon": "1.3.0"})
            self.assertEqual(crate_versions(Path(tmp) / "absent.lock"), {})

    def test_a_crate_locked_twice_keeps_both_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "Cargo.lock"
            lock.write_text('[[package]]\nname = "rayon"\nversion = "1.12.0"\n\n[[package]]\nname = "rayon"\nversion = "1.8.0"\n')
            self.assertEqual(crate_versions(lock), {"rayon": "1.12.0, 1.8.0"})

    def test_the_glue_digest_covers_the_bindings_and_the_snippets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            self.assertEqual(glue_digest(package), UNAVAILABLE)
            (package / "snippets/rayon").mkdir(parents=True)
            (package / "bench.js").write_text("bindings")
            (package / "snippets/rayon/workerHelpers.js").write_text("worker")
            first = glue_digest(package)
            (package / "snippets/rayon/workerHelpers.js").write_text("changed")
            self.assertNotEqual(glue_digest(package), first)

    def test_the_identity_names_the_crates_and_the_firefox_profile_settings(self) -> None:
        browsers = {"firefox": Path("/nonexistent/firefox")}
        identity = build_identity(spec(environments=["firefox"]), None, browsers)
        crates = identity["crates"]
        assert isinstance(crates, dict)
        self.assertEqual(set(crates), {"rayon", "rayon-core", "wasm-bindgen", "wasm-bindgen-rayon"})
        self.assertIn("wasmGlueSha256", identity)
        self.assertEqual(identity["firefoxPrefs"], dict(FIREFOX_PREFS))
        self.assertNotIn("firefoxPrefs", build_identity(spec(environments=["native"]), None, {}))


class HostEnvironmentTest(unittest.TestCase):
    def test_records_the_system_state_with_the_problems_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            environment = HostEnvironment(Path(tmp) / "browsers", "0,2")
            path = environment.record(Path(tmp) / "sysinfo", ["turbo is on, not off"])
            stored = json.loads(path.read_text())
        self.assertEqual(stored["problems"], ["turbo is on, not off"])
        self.assertIn("frequenciesKHz", stored)


class CampaignSpecsTest(unittest.TestCase):
    def test_every_shipped_spec_loads(self) -> None:
        specs = sorted((Path(__file__).resolve().parents[1] / "campaigns").glob("*.json"))
        self.assertTrue(specs)
        for path in specs:
            CampaignSpec.from_json(json.loads(path.read_text()))

    def test_smoke_spec_runs_strict_in_a_scope_as_the_current_user(self) -> None:
        path = Path(__file__).resolve().parents[1] / "campaigns" / "smoke.json"
        smoke = CampaignSpec.from_json(json.loads(path.read_text()))
        self.assertTrue(smoke.strict)
        self.assertEqual(smoke.scope_user, "$USER")
        self.assertEqual(smoke.cpus, "0,2,4,6,8,10,12,14")
        self.assertEqual(smoke.harness_cpus, "16-31")


class NativeCampaignTest(unittest.TestCase):
    def test_mini_campaign_with_a_native_runner_stores_every_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner = Path(tmp) / "runner.py"
            runner.write_text(
                "import json, sys\n"
                "if sys.argv[1:] == ['--build-info']: print(json.dumps({'features': [], 'rustc': 'rustc x', 'wasmBindgen': '0.2.129', 'rustflags': ''})); sys.exit(0)\n"
                f"print({CSV_HEADER!r}); print('native,filter')\n"
            )
            results = Path(tmp) / "mini"
            campaign = Campaign.for_spec(
                spec(environments=["native"], threads=[1, 2]),
                results,
                native=[sys.executable, str(runner)],
                browsers={},
            )
            summary = campaign.run()
            self.assertEqual((summary.done, summary.failed), (3 * 2 * 2, 0))
            stored = json.loads(next(results.glob("mini-0000-*.json")).read_text())
            self.assertEqual((stored["orderSeed"], stored["orderPosition"]), (7, 0))


if __name__ == "__main__":
    unittest.main()


class BooleanAsNumberTest(unittest.TestCase):
    def test_a_boolean_is_not_an_integer_field(self) -> None:
        with self.assertRaises(ValueError):
            spec(repetitions=True)

    def test_a_boolean_is_not_a_thread_count(self) -> None:
        with self.assertRaises(ValueError):
            spec(threads=[1, True])

    def test_a_boolean_is_not_a_timeout(self) -> None:
        with self.assertRaises(ValueError):
            spec(timeoutSeconds=True)
