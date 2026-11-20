"""Files of /proc and /sys that describe the CPU, read relative to a root so tests can fake them."""

from pathlib import Path

CPUINFO = "proc/cpuinfo"
PROC_STAT = "proc/stat"
KERNEL_RELEASE = "proc/sys/kernel/osrelease"
OS_RELEASE = "etc/os-release"
CPU_DIRECTORY = "sys/devices/system/cpu"
ONLINE_CPUS = f"{CPU_DIRECTORY}/online"
SMT_CONTROL = f"{CPU_DIRECTORY}/smt/control"
INTEL_NO_TURBO = f"{CPU_DIRECTORY}/intel_pstate/no_turbo"
CPUFREQ_BOOST = f"{CPU_DIRECTORY}/cpufreq/boost"
# Hybrid Intel CPUs list their P-core CPUs here; E-cores are under cpu_atom.
P_CORE_CPUS = "sys/devices/cpu_core/cpus"
CGROUP_ROOT = "sys/fs/cgroup"


def cpu_file(cpu: int, name: str) -> str:
    return f"{CPU_DIRECTORY}/cpu{cpu}/{name}"


def read_text(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except OSError:
        return None
