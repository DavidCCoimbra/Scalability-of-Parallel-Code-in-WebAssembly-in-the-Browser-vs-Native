import json
import tempfile
import unittest
from typing import Any
from pathlib import Path

from harness.context import (
    DEFAULT_PASSES,
    LATER_KEYS,
    REQUIRED_KEYS,
    UNAVAILABLE,
    LinuxHost,
    RunContext,
    annotate,
    command_output,
    loadavg,
    parse_cpu_mask,
    sha256_file,
    grain_of_query,
    passes_of_query,
    validate,
)


def write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class LinuxHostTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, "proc/cpuinfo", "processor\t: 0\nmodel name\t: Intel(R) Core(TM) i9-14900KF\n")
        for cpu in range(4):
            write(self.root, f"sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor", "performance\n")
        write(self.root, "sys/devices/system/cpu/intel_pstate/no_turbo", "1\n")
        write(self.root, "proc/sys/kernel/osrelease", "6.8.0-45-generic\n")
        write(self.root, "sys/devices/system/cpu/smt/control", "on\n")
        write(self.root, "sys/devices/cpu_core/cpus", "0-15\n")
        for core in range(8):
            for cpu in (2 * core, 2 * core + 1):
                write(self.root, f"sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list", f"{2 * core}-{2 * core + 1}\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_reads_cpu_governor_turbo_and_kernel(self) -> None:
        host = LinuxHost(self.root, cpus=[0, 1, 2, 3])
        self.assertEqual(host.cpu_model(), "Intel(R) Core(TM) i9-14900KF")
        self.assertEqual(host.governor(), "performance")
        self.assertEqual(host.turbo(), "off")
        self.assertEqual(host.kernel(), "6.8.0-45-generic")

    def test_mixed_governors_are_reported(self) -> None:
        write(self.root, "sys/devices/system/cpu/cpu3/cpufreq/scaling_governor", "powersave\n")
        self.assertEqual(LinuxHost(self.root, cpus=[0, 3]).governor(), "mixed:performance,powersave")

    def test_turbo_on_and_cpufreq_boost(self) -> None:
        write(self.root, "sys/devices/system/cpu/intel_pstate/no_turbo", "0\n")
        self.assertEqual(LinuxHost(self.root, cpus=[0]).turbo(), "on")
        (self.root / "sys/devices/system/cpu/intel_pstate/no_turbo").unlink()
        write(self.root, "sys/devices/system/cpu/cpufreq/boost", "0\n")
        self.assertEqual(LinuxHost(self.root, cpus=[0]).turbo(), "off")

    def test_reads_smt_state_p_cpus_and_mask_siblings(self) -> None:
        host = LinuxHost(self.root, cpus=[0, 1])
        self.assertEqual(host.smt(), "on")
        self.assertEqual(host.p_cpus(), "0-15")
        self.assertEqual(host.mask_siblings(), ["0-1", "0-1"])

    def test_missing_files_are_explicitly_unavailable(self) -> None:
        host = LinuxHost(self.root / "nowhere", cpus=[0])
        self.assertEqual((host.cpu_model(), host.governor(), host.turbo()), (UNAVAILABLE,) * 3)


class RunContextTest(unittest.TestCase):
    def context(self, **overrides: Any) -> RunContext:
        values: dict[str, Any] = dict(
            commit="abc123",
            cpu_model="cpu",
            governor="performance",
            turbo="off",
            kernel="6.8",
            os="Linux",
            environment="chrome",
            browser_version="Google Chrome for Testing 155.0.8059.84",
            cpu_mask="0,2,4,6,8,10,12,14",
            smt="off",
            p_cpus="0-15",
            mask_siblings=["0", "2", "4", "6", "8", "10", "12", "14"],
            headless=False,
            launch_flags=["--no-first-run"],
            order_seed=7,
            order_position=3,
            started_at="2026-10-17T20:00:00+00:00",
            finished_at="2026-10-17T20:00:05+00:00",
            launch_seconds=5.0,
            artifact_sha256="ab" * 32,
            build={"features": [], "rustc": "rustc 1.101.0-nightly", "wasmBindgen": "0.2.129", "rustflags": ""},
            loadavg_before=[0.1, 0.1, 0.1],
            loadavg_after=[0.2, 0.1, 0.1],
            shield={"system.slice": "16-31", "user.slice": "16-31", "init.scope": "16-31"},
            run_cpu_seconds=40.0,
            run_cpu_method="scope",
            start_delay_ms=0,
            passes=1,
            leftover_processes=0,
            escaped_processes=0,
            foreign_cpu_seconds=0.02,
        )
        values.update(overrides)
        return RunContext(**values)

    def test_serialises_every_required_key(self) -> None:
        self.assertEqual(set(self.context().to_json()), set(REQUIRED_KEYS) | set(LATER_KEYS))

    def test_validate_accepts_a_complete_context(self) -> None:
        self.assertEqual(validate(self.context().to_json(), strict=True), [])

    def test_validate_reports_missing_keys(self) -> None:
        data = self.context().to_json()
        del data["governor"]
        self.assertEqual(validate(data), ["missing governor"])

    def test_strict_validation_rejects_unavailable_values(self) -> None:
        data = self.context(governor=UNAVAILABLE, order_seed=None).to_json()
        self.assertEqual(validate(data), [])
        self.assertIn("governor unavailable", validate(data, strict=True))
        self.assertIn("orderSeed unavailable", validate(data, strict=True))

    def test_strict_validation_rejects_build_info_with_unknown_fields(self) -> None:
        for field in ("rustc", "wasmBindgen"):
            original = self.context().build
            assert isinstance(original, dict)
            build = {**original, field: UNAVAILABLE}
            data = self.context(build=build).to_json()
            self.assertEqual(validate(data, strict=True), [f"build.{field} unavailable"], field)

    def test_strict_validation_requires_the_shield_and_foreign_cpu_time(self) -> None:
        data = self.context(shield=UNAVAILABLE, foreign_cpu_seconds=UNAVAILABLE).to_json()
        self.assertEqual(validate(data), [])
        self.assertEqual(
            validate(data, strict=True), ["shield unavailable", "foreignCpuSeconds unavailable"]
        )

    def test_strict_validation_rejects_a_shield_that_overlaps_the_mask(self) -> None:
        shield = {"system.slice": "16-31", "user.slice": "0-31", "init.scope": "16-31"}
        data = self.context(shield=shield).to_json()
        self.assertEqual(validate(data, strict=True), ["shield: user.slice can use measured CPUs 0,2,4,6,8,10,12,14"])

    def test_strict_validation_rejects_conditions_the_adrs_forbid(self) -> None:
        cases = {
            "commit is dirty": dict(commit="abc123-dirty"),
            "governor is mixed:performance,powersave, not performance": dict(governor="mixed:performance,powersave"),
            "turbo is on, not off": dict(turbo="on"),
            "cpuMask unavailable": dict(cpu_mask=""),
        }
        for problem, override in cases.items():
            self.assertEqual(validate(self.context(**override).to_json(), strict=True), [problem], problem)

    def test_strict_validation_rejects_smt_on_and_hyperthread_pairs(self) -> None:
        mask = self.context(
            smt="on",
            cpu_mask="0-7",
            mask_siblings=["0-1", "0-1", "2-3", "2-3", "4-5", "4-5", "6-7", "6-7"],
        ).to_json()
        self.assertEqual(
            validate(mask, strict=True),
            ["smt is on, not off", "cpuMask has two CPUs on one physical core"],
        )

    def test_strict_validation_accepts_the_smt_off_layout(self) -> None:
        for smt in ("off", "forceoff", "notsupported"):
            data = self.context(smt=smt, p_cpus="0,2,4,6,8,10,12,14").to_json()
            self.assertEqual(validate(data, strict=True), [], smt)

    def test_malformed_stored_mask_is_reported_not_raised(self) -> None:
        data = self.context(cpu_mask="0-7:2").to_json()
        self.assertIn("cpuMask is malformed", validate(data, strict=True))

    def test_strict_validation_rejects_cpus_that_are_not_p_cores(self) -> None:
        data = self.context(cpu_mask="14,16", mask_siblings=["14", "16"]).to_json()
        self.assertIn("cpuMask includes CPUs that are not P-cores: 16", validate(data, strict=True))

    def test_hybrid_validation_accepts_e_cores_next_to_every_p_core(self) -> None:
        data = self.context(cpu_mask="0,2,4,6,8,10,12,14,16-27", p_cpus="0,2,4,6,8,10,12,14", shield={"system.slice": "28-31", "user.slice": "28-31", "init.scope": "28-31"}, mask_siblings=[str(c) for c in (0, 2, 4, 6, 8, 10, 12, 14, *range(16, 28))]).to_json()
        self.assertEqual(validate(data, strict=True, hybrid=True), [])
        self.assertIn("cpuMask includes CPUs that are not P-cores: 16,17,18,19,20,21,22,23,24,25,26,27", validate(data, strict=True))

    def test_strict_validation_checks_the_pinned_browser_version(self) -> None:
        pinned = {"chrome": "155.0.8059.84", "firefox": "158.0"}
        self.assertEqual(validate(self.context().to_json(), strict=True, pinned=pinned), [])
        wrong = self.context(browser_version="Google Chrome 154.0.1.2").to_json()
        self.assertEqual(
            validate(wrong, strict=True, pinned=pinned),
            ["browserVersion Google Chrome 154.0.1.2 is not the pinned 155.0.8059.84"],
        )

    def test_strict_validation_rejects_browser_processes_that_left_the_run_scope(self) -> None:
        data = {**self.context().to_json(), "escapedProcesses": 2}
        self.assertEqual(validate(data, strict=True), ["escapedProcesses 2: browser processes left the run scope"])

    def test_strict_validation_requires_the_leftover_check(self) -> None:
        data = self.context(leftover_processes=UNAVAILABLE).to_json()
        self.assertEqual(validate(data), [])
        self.assertEqual(validate(data, strict=True), ["leftoverProcesses unavailable"])

    def test_pinned_browser_version_must_match_exactly(self) -> None:
        pinned = {"chrome": "155.0.8059.84", "firefox": "158.0"}
        point_release = self.context(environment="firefox", browser_version="Mozilla Firefox 158.0.1").to_json()
        self.assertEqual(
            validate(point_release, strict=True, pinned=pinned),
            ["browserVersion Mozilla Firefox 158.0.1 is not the pinned 158.0"],
        )
        exact = self.context(environment="firefox", browser_version="Mozilla Firefox 158.0").to_json()
        self.assertEqual(validate(exact, strict=True, pinned=pinned), [])


class ProvenanceTest(unittest.TestCase):
    def test_strict_validation_requires_provenance(self) -> None:
        data = RunContextTest().context(artifact_sha256=UNAVAILABLE, order_position=None).to_json()
        problems = validate(data, strict=True)
        self.assertIn("artifactSha256 unavailable", problems)
        self.assertIn("orderPosition unavailable", problems)

    def test_sha256_of_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.bin"
            path.write_bytes(b"abc")
            self.assertEqual(sha256_file(path), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
            self.assertEqual(sha256_file(Path(tmp) / "missing"), UNAVAILABLE)

    def test_loadavg_has_three_values(self) -> None:
        self.assertEqual(len(loadavg()), 3)


class AnnotateTest(unittest.TestCase):
    def test_merges_context_into_existing_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "r1.json"
            path.write_text(json.dumps({"userAgent": "ua", "clockResolutionNs": 5000}))
            annotate(path, {"commit": "abc", "environment": "chrome"})
            data = json.loads(path.read_text())
        self.assertEqual(data, {"userAgent": "ua", "clockResolutionNs": 5000, "commit": "abc", "environment": "chrome"})

    def test_creates_metadata_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "native.json"
            annotate(path, {"environment": "native"})
            self.assertEqual(json.loads(path.read_text()), {"environment": "native"})


class CommandOutputTest(unittest.TestCase):
    def test_reads_the_output_of_a_command(self) -> None:
        self.assertEqual(command_output(["echo", "Mozilla Firefox 158.0"]), "Mozilla Firefox 158.0")

    def test_failing_command_is_unavailable(self) -> None:
        self.assertEqual(command_output(["false"]), UNAVAILABLE)


class CpuMaskTest(unittest.TestCase):
    def test_parses_ranges_and_lists(self) -> None:
        self.assertEqual(parse_cpu_mask("0-3,8"), [0, 1, 2, 3, 8])

    def test_rejects_malformed_masks(self) -> None:
        for mask in ("0-7:2", "0,x", "3-1"):
            with self.assertRaises(ValueError):
                parse_cpu_mask(mask)


class PassesOfQueryTest(unittest.TestCase):
    def test_a_query_without_passes_means_one_pass(self) -> None:
        self.assertEqual(passes_of_query("workload=filter&threads=2"), DEFAULT_PASSES)
        self.assertEqual(DEFAULT_PASSES, 1)

    def test_the_passes_of_the_query_are_read(self) -> None:
        self.assertEqual(passes_of_query("workload=filter&passes=12&threads=2"), 12)


class GrainOfQueryTest(unittest.TestCase):
    def test_a_query_without_grain_means_the_adaptive_split(self) -> None:
        self.assertIsNone(grain_of_query("workload=filter&threads=2"))

    def test_the_grain_of_the_query_is_read(self) -> None:
        self.assertEqual(grain_of_query("workload=filter&grain=32&threads=2"), 32)


if __name__ == "__main__":
    unittest.main()
