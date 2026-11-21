import tempfile
import unittest
from pathlib import Path

from harness.context import UNAVAILABLE
from harness.environment import EnvironmentCheck, p_core_mask, quiet_mode, sysinfo
from harness.environment.host_state import host_state

MASK = "0,2,4,6,8,10,12,14"


def write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def raptor_lake(root: Path, smt: str = "off", turbo: str = "1", governor: str = "performance", shield: str = "16-31") -> None:
    write(root, "proc/cpuinfo", "model name\t: Intel(R) Core(TM) i9-14900KF\nmicrocode\t: 0x133\n")
    write(root, "etc/os-release", 'NAME="Ubuntu"\nPRETTY_NAME="Ubuntu 26.04.1 LTS"\nVERSION_ID="26.04"\n')
    write(root, "proc/sys/kernel/osrelease", "6.8.0")
    write(root, "sys/devices/system/cpu/smt/control", smt)
    write(root, "sys/devices/system/cpu/intel_pstate/no_turbo", turbo)
    write(root, "sys/devices/cpu_core/cpus", "0-15")
    online = "0,2,4,6,8,10,12,14,16-31" if smt == "off" else "0-31"
    write(root, "sys/devices/system/cpu/online", online)
    for cpu in range(32):
        siblings = f"{cpu - cpu % 2}-{cpu - cpu % 2 + 1}" if cpu < 16 else str(cpu)
        base = f"sys/devices/system/cpu/cpu{cpu}"
        write(root, f"{base}/topology/thread_siblings_list", str(cpu) if smt == "off" and cpu < 16 else siblings)
        write(root, f"{base}/topology/core_cpus_list", siblings)
        write(root, f"{base}/cpufreq/scaling_governor", governor)
        write(root, f"{base}/cpufreq/cpuinfo_min_freq", "800000")
        write(root, f"{base}/cpufreq/cpuinfo_max_freq", "3200000")
        write(root, f"{base}/cpufreq/scaling_cur_freq", "3200000")
    for unit in ("system.slice", "user.slice", "init.scope"):
        write(root, f"sys/fs/cgroup/{unit}/cpuset.cpus.effective", shield)


class MaskTest(unittest.TestCase):
    def test_one_cpu_per_physical_p_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp), smt="on")
            self.assertEqual(p_core_mask(Path(tmp)), MASK)

    def test_mask_is_the_same_with_smt_off(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp))
            self.assertEqual(p_core_mask(Path(tmp)), MASK)

    def test_machine_without_hybrid_topology_has_no_mask(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(p_core_mask(Path(tmp)))


class CheckTest(unittest.TestCase):
    def problems(self, **machine: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp), **machine)
            return EnvironmentCheck(Path(tmp)).problems(MASK)

    def test_prepared_machine_passes(self) -> None:
        self.assertEqual(self.problems(), [])

    def test_turbo_on_fails(self) -> None:
        self.assertEqual(self.problems(turbo="0"), ["turbo is on, not off"])

    def test_governor_other_than_performance_fails(self) -> None:
        self.assertEqual(self.problems(governor="powersave"), ["governor is powersave, not performance"])

    def test_smt_on_fails(self) -> None:
        problems = self.problems(smt="on")
        self.assertIn("smt is on, not off", problems)

    def test_unshielded_system_fails(self) -> None:
        self.assertEqual(
            self.problems(shield="0-31"),
            [f"shield: {unit} can use measured CPUs {MASK}" for unit in ("system.slice", "user.slice", "init.scope")],
        )

    def test_mask_must_be_every_physical_p_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp))
            self.assertEqual(
                EnvironmentCheck(Path(tmp)).problems("0,2,4,6"),
                [f"cpuMask is 0,2,4,6, but the physical P-cores are {MASK}"],
            )

    def test_a_hybrid_mask_adds_e_cores_to_every_p_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp), shield="28-31")
            self.assertEqual(EnvironmentCheck(Path(tmp)).problems(f"{MASK},16-27", hybrid=True), [])

    def test_a_hybrid_mask_still_needs_every_p_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp), shield="28-31")
            self.assertEqual(
                EnvironmentCheck(Path(tmp)).problems("0,2,16-27", hybrid=True),
                ["hybrid cpuMask leaves out P-cores: 4,6,8,10,12,14"],
            )

    def test_a_hybrid_mask_on_a_machine_without_p_cores_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn(
                "hybrid cpuMask cannot be checked: the P-cores are unknown",
                EnvironmentCheck(Path(tmp)).problems("0-3", hybrid=True),
            )

    def test_e_cores_are_refused_without_hybrid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp), shield="28-31")
            self.assertIn(
                "cpuMask includes CPUs that are not P-cores: 16,17,18,19,20,21,22,23,24,25,26,27",
                EnvironmentCheck(Path(tmp)).problems(f"{MASK},16-27"),
            )


class SysinfoTest(unittest.TestCase):
    def test_records_cpu_frequencies_system_versions_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp))
            info = sysinfo(Path(tmp), MASK, versions={"rustc": "rustc 1.101.0-nightly"})
        self.assertEqual(info["cpuModel"], "Intel(R) Core(TM) i9-14900KF")
        self.assertEqual(info["kernel"], "6.8.0")
        self.assertEqual(info["distro"], "Ubuntu 26.04.1 LTS")
        self.assertEqual(info["microcode"], "0x133")
        self.assertEqual(info["pCoreMask"], MASK)
        self.assertEqual(info["frequenciesKHz"]["0"], {"min": 800000, "max": 3200000, "current": 3200000})
        self.assertEqual(sorted(info["frequenciesKHz"], key=int), MASK.split(","))
        self.assertEqual(info["versions"]["rustc"], "rustc 1.101.0-nightly")
        self.assertEqual(info["shield"], {unit: "16-31" for unit in ("system.slice", "user.slice", "init.scope")})
        self.assertIn("commit", info)
        self.assertIn("loadavg", info)
        self.assertIn("collectedAt", info)

    def test_missing_system_files_are_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            info = sysinfo(Path(tmp), MASK, versions={})
        self.assertEqual(info["distro"], UNAVAILABLE)
        self.assertEqual(info["microcode"], UNAVAILABLE)


class HostStateTest(unittest.TestCase):
    def test_the_settings_no_check_enforces_are_recorded_as_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "sys/kernel/mm/transparent_hugepage/enabled", "always [madvise] never\n")
            write(root, "sys/kernel/mm/transparent_hugepage/defrag", "always defer defer+madvise [madvise] never\n")
            write(root, "proc/cmdline", "BOOT_IMAGE=/vmlinuz root=/dev/nvme0n1p2 ro quiet splash\n")
            write(root, "sys/devices/system/cpu/vulnerabilities/spectre_v2", "Mitigation: Enhanced / Automatic IBRS\n")
            write(root, "sys/devices/system/cpu/vulnerabilities/meltdown", "Not affected\n")
            write(root, "sys/devices/system/cpu/cpuidle/current_driver", "intel_idle\n")
            for index, (name, disabled) in enumerate([("POLL", "0"), ("C1E", "0"), ("C10", "1")]):
                write(root, f"sys/devices/system/cpu/cpu2/cpuidle/state{index}/name", name)
                write(root, f"sys/devices/system/cpu/cpu2/cpuidle/state{index}/disable", disabled)
            write(root, "proc/meminfo", "MemTotal:       65536000 kB\nMemFree:        1 kB\n")
            write(root, "sys/class/dmi/id/bios_version", "1801\n")
            write(root, "proc/irq/default_smp_affinity", "ffff0000\n")
            state = host_state(root, [2, 4])
        self.assertEqual(state["transparentHugepage"]["enabled"], "always [madvise] never")
        self.assertEqual(state["kernelCmdline"], "BOOT_IMAGE=/vmlinuz root=/dev/nvme0n1p2 ro quiet splash")
        self.assertEqual(state["mitigations"], {"meltdown": "Not affected", "spectre_v2": "Mitigation: Enhanced / Automatic IBRS"})
        self.assertEqual(state["cpuIdle"]["driver"], "intel_idle")
        self.assertEqual([(idle["name"], idle["disabled"]) for idle in state["cpuIdle"]["states"]], [("POLL", False), ("C1E", False), ("C10", True)])
        self.assertEqual(state["memTotalKb"], 65_536_000)
        self.assertEqual(state["firmware"]["bios_version"], "1801")
        self.assertIsNone(state["firmware"]["bios_date"])
        self.assertEqual(state["defaultIrqAffinity"], "ffff0000")

    def test_a_host_without_these_files_records_nothing_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = host_state(Path(tmp), [])
            info = sysinfo(Path(tmp), MASK, versions={}, quiet_state=Path(tmp) / "missing")
        self.assertEqual((state["kernelCmdline"], state["mitigations"], state["memTotalKb"]), (None, {}, None))
        self.assertEqual(state["cpuIdle"], {"driver": None, "states": []})
        self.assertEqual(info["hostState"], state)


class QuietModeTest(unittest.TestCase):
    def test_quiet_mode_lists_the_units_it_stopped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "ppc-quiet.state"
            state.write_text("system docker.service\nuser localsearch-3.service\n")
            self.assertEqual(quiet_mode(state), {"on": True, "stopped": ["docker.service", "localsearch-3.service"]})

    def test_paused_claude_processes_are_not_listed_as_units(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "ppc-quiet.state"
            state.write_text("system docker.service\nclaude 4242\n")
            self.assertEqual(quiet_mode(state), {"on": True, "stopped": ["docker.service"]})

    def test_quiet_mode_is_off_without_a_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(quiet_mode(Path(tmp) / "missing"), {"on": False, "stopped": []})

    def test_sysinfo_records_quiet_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp))
            info = sysinfo(Path(tmp), MASK, versions={}, quiet_state=Path(tmp) / "missing")
        self.assertEqual(info["quietMode"], {"on": False, "stopped": []})

    def test_sysinfo_records_perf_event_paranoid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp))
            write(Path(tmp), "proc/sys/kernel/perf_event_paranoid", "1\n")
            info = sysinfo(Path(tmp), MASK, versions={}, quiet_state=Path(tmp) / "missing")
        self.assertEqual(info["perfEventParanoid"], 1)

    def test_sysinfo_without_perf_event_paranoid_records_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raptor_lake(Path(tmp))
            info = sysinfo(Path(tmp), MASK, versions={}, quiet_state=Path(tmp) / "missing")
        self.assertIsNone(info["perfEventParanoid"])

if __name__ == "__main__":
    unittest.main()
