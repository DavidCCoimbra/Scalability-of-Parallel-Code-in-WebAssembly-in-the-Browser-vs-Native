"""The transient systemd scope that holds every process of one run.

systemd-run --scope: https://www.freedesktop.org/software/systemd/man/latest/systemd-run.html
"""

import re
import subprocess
from collections.abc import Mapping
from pathlib import Path

from harness.context import UNAVAILABLE, read_text, round_seconds
from harness.context.sysfs import CGROUP_ROOT

BENCH_SLICE = "ppc-bench.slice"
SCOPE_PREFIX = "ppc-run-"
SLICE_SUFFIX = ".slice"
SCOPE_SUFFIX = ".scope"
UNIT_NAME = re.compile(r"[A-Za-z0-9_-]+")
# Only what a browser needs to open a display; the session bus is left out on purpose.
SESSION_VARIABLES = (
    "HOME",
    "USER",
    "LOGNAME",
    "PATH",
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "XAUTHORITY",
    "XDG_RUNTIME_DIR",
)
SYSTEMCTL_TIMEOUT_SECONDS = 30
USAGE_KEY = "usage_usec"
MICROSECONDS_PER_SECOND = 1_000_000


def scope_unit(run_id: str) -> str:
    return f"{SCOPE_PREFIX}{run_id}"


# A command prefix: systemd-run --scope starts the measured command (taskset and the browser
# or native runner) in a new cgroup, a kernel group of processes, and every child it forks
# stays in it, so AllowedCPUs bounds the whole process tree and cpu.stat later sums its CPU
# time. sudo creates the scope; --uid runs the command as the user.
def scope_prefix(run_id: str, cpus: str, user: str, environment: Mapping[str, str]) -> list[str]:
    if not UNIT_NAME.fullmatch(run_id):
        raise ValueError(f"run id {run_id!r} is not a valid systemd unit name")
    kept = [f"{name}={environment[name]}" for name in SESSION_VARIABLES if name in environment]
    return [
        "sudo",
        "-n",
        "systemd-run",
        "--scope",
        "--quiet",
        f"--slice={BENCH_SLICE}",
        f"--unit={scope_unit(run_id)}",
        f"--uid={user}",
        "-p",
        f"AllowedCPUs={cpus}",
        "env",
        *kept,
    ]


def scope_stop_command(run_id: str) -> list[str]:
    return ["sudo", "-n", "systemctl", "stop", f"{scope_unit(run_id)}{SCOPE_SUFFIX}"]


def stop_scope(run_id: str) -> None:
    try:
        subprocess.run(scope_stop_command(run_id), capture_output=True, timeout=SYSTEMCTL_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        pass


def slice_cgroup(slice_name: str) -> Path:
    # A dash in a slice name means nesting: a-b.slice lives in a.slice/a-b.slice.
    # https://www.freedesktop.org/software/systemd/man/latest/systemd.slice.html
    parts = slice_name.removesuffix(SLICE_SUFFIX).split("-")
    return Path(*("-".join(parts[: depth + 1]) + SLICE_SUFFIX for depth in range(len(parts))))


# E.g. /sys/fs/cgroup/ppc.slice/ppc-bench.slice/ppc-run-<id>.scope, the directory whose
# cpu.stat holds the scope's CPU time.
def scope_cgroup(run_id: str, root: Path = Path("/")) -> Path:
    return root / CGROUP_ROOT / slice_cgroup(BENCH_SLICE) / f"{scope_unit(run_id)}{SCOPE_SUFFIX}"


def scope_cpu_seconds(run_id: str, root: Path = Path("/")) -> float | str:
    # cpu.stat of cgroup v2: https://docs.kernel.org/admin-guide/cgroup-v2.html#cpu-interface-files
    stat = read_text(scope_cgroup(run_id, root) / "cpu.stat") or ""
    for line in stat.splitlines():
        key, _, value = line.partition(" ")
        if key == USAGE_KEY:
            return round_seconds(int(value) / MICROSECONDS_PER_SECOND)
    return UNAVAILABLE
