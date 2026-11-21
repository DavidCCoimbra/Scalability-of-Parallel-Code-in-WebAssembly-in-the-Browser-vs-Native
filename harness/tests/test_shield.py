import os
import tempfile
import unittest
from pathlib import Path

from harness.context import UNAVAILABLE
from harness.shield import (
    SHIELDED_UNITS,
    CgroupShield,
    CoreActivity,
    CoreSnapshot,
    CpuTimes,
    CpuUsage,
    escaped_processes,
    pin_current_process,
    process_session_seconds,
    scope_cpu_seconds,
    scope_prefix,
    scope_stop_command,
    slice_cgroup,
)

PROC_STAT = """cpu  1000 0 500 9000 0 0 0 0 0 0
cpu0 100 10 50 900 7 1 2 3 0 0
cpu1 200 0 100 800 0 0 0 0 0 0
cpu2 300 0 0 700 0 0 0 0 0 0
intr 12345
"""


def write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class CpuTimesTest(unittest.TestCase):
    def test_busy_ticks_per_cpu_exclude_idle_and_iowait(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "proc/stat", PROC_STAT)
            times = CpuTimes.read(Path(tmp))
        assert times is not None
        self.assertEqual(times.busy, {0: 166, 1: 300, 2: 300})

    def test_busy_seconds_between_two_readings_on_selected_cpus(self) -> None:
        earlier = CpuTimes({0: 100, 1: 200, 2: 300})
        later = CpuTimes({0: 150, 1: 260, 2: 999})
        self.assertEqual(later.busy_seconds_since(earlier, [0, 1], ticks_per_second=100), 1.1)

    def test_missing_proc_stat_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(CpuTimes.read(Path(tmp)))


class CpuUsageTest(unittest.TestCase):
    def test_foreign_time_is_busy_time_on_the_mask_minus_the_run(self) -> None:
        readings = iter([CpuTimes({0: 100, 2: 100}), CpuTimes({0: 400, 2: 350})])
        usage = CpuUsage([0, 2], read=lambda: next(readings), ticks_per_second=100)
        usage.start()
        self.assertEqual(usage.stop(run_seconds=5.0), (5.0, 0.5))

    def test_without_a_mask_or_proc_stat_foreign_time_is_unavailable(self) -> None:
        usage = CpuUsage(None, read=lambda: CpuTimes({0: 1}), ticks_per_second=100)
        usage.start()
        self.assertEqual(usage.stop(run_seconds=2.0), (2.0, UNAVAILABLE))
        usage = CpuUsage([0], read=lambda: None, ticks_per_second=100)
        usage.start()
        self.assertEqual(usage.stop(run_seconds=2.0), (2.0, UNAVAILABLE))


class CoreActivityTest(unittest.TestCase):
    def test_each_measured_cpu_gets_its_busy_time_and_both_frequencies(self) -> None:
        snapshots = iter(
            [
                CoreSnapshot(CpuTimes({0: 100, 2: 100}), {0: 3200000, 2: 800000}),
                CoreSnapshot(CpuTimes({0: 400, 2: 100}), {0: 3200000, 2: 2600000}),
            ]
        )
        activity = CoreActivity([0, 2], snapshot=lambda cpus: next(snapshots), ticks_per_second=100)
        activity.start()
        self.assertEqual(
            activity.stop(),
            {
                "0": {"busySeconds": 3.0, "khzBefore": 3200000, "khzAfter": 3200000},
                "2": {"busySeconds": 0.0, "khzBefore": 800000, "khzAfter": 2600000},
            },
        )

    def test_a_snapshot_reads_proc_stat_and_the_frequency_of_the_asked_cpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "proc/stat", PROC_STAT)
            write(root, "sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "3200000\n")
            snapshot = CoreSnapshot.take([0, 2], root)
        assert snapshot.times is not None
        self.assertEqual(snapshot.times.busy[2], 300)
        self.assertEqual(snapshot.khz, {0: 3200000, 2: None})

    def test_without_a_mask_nothing_is_recorded(self) -> None:
        activity = CoreActivity(None)
        activity.start()
        self.assertEqual(activity.stop(), UNAVAILABLE)

    def test_without_proc_stat_the_busy_time_is_missing_and_the_rest_is_kept(self) -> None:
        activity = CoreActivity([0], snapshot=lambda cpus: CoreSnapshot(None, {0: 3200000}), ticks_per_second=100)
        activity.start()
        self.assertEqual(activity.stop(), {"0": {"busySeconds": None, "khzBefore": 3200000, "khzAfter": 3200000}})


class ProcessSessionTest(unittest.TestCase):
    def test_sums_user_system_and_reaped_children_of_one_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fields = "S 1 {pgrp} {session} 0 0 0 0 0 0 0 {utime} {stime} {cutime} {cstime} 20 0 1 0 0"
            write(root, "proc/10/stat", "10 (chrome) " + fields.format(pgrp=10, session=10, utime=300, stime=100, cutime=50, cstime=50))
            write(root, "proc/11/stat", "11 (Web Content) " + fields.format(pgrp=10, session=10, utime=40, stime=10, cutime=0, cstime=0))
            write(root, "proc/12/stat", "12 (other) " + fields.format(pgrp=12, session=12, utime=999, stime=999, cutime=0, cstime=0))
            write(root, "proc/self/stat", "x")
            write(root, "proc/stat", PROC_STAT)
            self.assertEqual(process_session_seconds(10, root, ticks_per_second=100), 5.5)


class ScopeCpuTest(unittest.TestCase):
    def test_reads_the_scope_cpu_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "sys/fs/cgroup/ppc.slice/ppc-bench.slice/ppc-run-r1.scope/cpu.stat", "usage_usec 2500000\nuser_usec 2000000\n")
            self.assertEqual(scope_cpu_seconds("r1", Path(tmp)), 2.5)
            self.assertEqual(scope_cpu_seconds("r2", Path(tmp)), UNAVAILABLE)

    def test_slice_dashes_nest_like_systemd(self) -> None:
        self.assertEqual(slice_cgroup("ppc-bench.slice"), Path("ppc.slice/ppc-bench.slice"))
        self.assertEqual(slice_cgroup("a-b-c.slice"), Path("a.slice/a-b.slice/a-b-c.slice"))
        self.assertEqual(slice_cgroup("system.slice"), Path("system.slice"))


SCOPE = "0::/ppc.slice/ppc-bench.slice/ppc-run-r1.scope\n"
MOVED = "0::/user.slice/user-1000.slice/user@1000.service/app.slice/app-org.chromium.Chromium-9.scope\n"


def process(root: Path, pid: int, parent: int, cmdline: str, cgroup: str) -> None:
    write(root, f"proc/{pid}/stat", f"{pid} (x) S {parent} 0 0")
    write(root, f"proc/{pid}/cmdline", cmdline.replace(" ", "\0"))
    write(root, f"proc/{pid}/cgroup", cgroup)


class EscapedProcessesTest(unittest.TestCase):
    def test_descendants_of_the_launch_outside_the_run_scope_have_escaped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            process(root, 13, 1, "sudo -n systemd-run chrome --user-data-dir=/tmp/p", MOVED)
            process(root, 10, 13, "chrome --user-data-dir=/tmp/p", MOVED)
            process(root, 11, 10, "chrome --type=renderer", SCOPE)
            process(root, 12, 10, "chrome --type=utility", MOVED)
            process(root, 20, 1, "zen", MOVED)
            self.assertEqual(escaped_processes(Path("/tmp/p"), "r1", launched=13, root=root), 2)

    def test_a_process_of_the_profile_outside_the_tree_still_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            process(root, 13, 1, "sudo -n systemd-run chrome --user-data-dir=/tmp/p", MOVED)
            process(root, 30, 1, "chrome --user-data-dir=/tmp/p", MOVED)
            self.assertEqual(escaped_processes(Path("/tmp/p"), "r1", launched=13, root=root), 1)

class CgroupShieldTest(unittest.TestCase):
    def shield(self, root: Path, cpus: dict[str, str]) -> CgroupShield:
        for unit, value in cpus.items():
            write(root, f"sys/fs/cgroup/{unit}/cpuset.cpus.effective", value)
        return CgroupShield(root)

    def test_state_reports_each_shielded_unit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            shield = self.shield(Path(tmp), {unit: "16-31" for unit in SHIELDED_UNITS})
            self.assertEqual(shield.state(), {unit: "16-31" for unit in SHIELDED_UNITS})
            self.assertEqual(shield.problems("0,2,4,6,8,10,12,14"), [])

    def test_units_that_overlap_the_mask_are_problems(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            shield = self.shield(Path(tmp), {"system.slice": "16-31", "user.slice": "0-31", "init.scope": "14-31"})
            self.assertEqual(
                shield.problems("0,2,4,6,8,10,12,14"),
                ["user.slice can use measured CPUs 0,2,4,6,8,10,12,14", "init.scope can use measured CPUs 14"],
            )

    def test_unreadable_units_are_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            shield = self.shield(Path(tmp), {"system.slice": "16-31"})
            self.assertEqual(shield.state(), UNAVAILABLE)
            self.assertEqual(shield.problems("0,2"), ["user.slice cpuset unavailable", "init.scope cpuset unavailable"])


class ScopeTest(unittest.TestCase):
    def test_the_session_bus_is_not_passed_to_the_browser(self) -> None:
        prefix = scope_prefix("r-1", "0,2,4", "david", {"HOME": "/home/david", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/x"})
        self.assertNotIn("DBUS_SESSION_BUS_ADDRESS=unix:path=/x", prefix)

    def test_scope_runs_the_command_as_the_user_in_its_own_slice(self) -> None:
        self.assertEqual(
            scope_prefix("r-1", "0,2,4", "david", {"HOME": "/home/david", "DISPLAY": ":0"}),
            [
                "sudo",
                "-n",
                "systemd-run",
                "--scope",
                "--quiet",
                "--slice=ppc-bench.slice",
                "--unit=ppc-run-r-1",
                "--uid=david",
                "-p",
                "AllowedCPUs=0,2,4",
                "env",
                "HOME=/home/david",
                "DISPLAY=:0",
            ],
        )

    def test_scope_keeps_only_the_session_variables_browsers_need(self) -> None:
        environment = {"HOME": "/h", "SECRET": "x", "WAYLAND_DISPLAY": "wayland-0"}
        self.assertEqual(scope_prefix("r", "0", "u", environment)[-3:], ["env", "HOME=/h", "WAYLAND_DISPLAY=wayland-0"])

    def test_run_ids_that_are_not_valid_unit_names_are_rejected(self) -> None:
        for run_id in ("", "a b", "x/y", "é"):
            with self.assertRaises(ValueError, msg=run_id):
                scope_prefix(run_id, "0", "u", {})

    def test_stopping_a_scope_stops_its_unit(self) -> None:
        self.assertEqual(scope_stop_command("r-1"), ["sudo", "-n", "systemctl", "stop", "ppc-run-r-1.scope"])


class PinTest(unittest.TestCase):
    def test_no_mask_leaves_the_affinity_alone(self) -> None:
        pin_current_process(None)

    @unittest.skipUnless(hasattr(os, "sched_setaffinity"), "Linux only")
    def test_pins_the_harness_to_the_given_cpus(self) -> None:
        allowed = os.sched_getaffinity(0)
        first = min(allowed)
        try:
            pin_current_process(str(first))
            self.assertEqual(os.sched_getaffinity(0), {first})
        finally:
            os.sched_setaffinity(0, allowed)


if __name__ == "__main__":
    unittest.main()
