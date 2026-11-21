"""Host settings that can move a measurement and that no check enforces: recorded, not judged."""

from pathlib import Path
from typing import TypedDict

from harness.context import read_text
from harness.context.sysfs import CPU_DIRECTORY, cpu_file

TRANSPARENT_HUGEPAGE = "sys/kernel/mm/transparent_hugepage"
KERNEL_CMDLINE = "proc/cmdline"
VULNERABILITIES = f"{CPU_DIRECTORY}/vulnerabilities"
CPUIDLE_DRIVER = f"{CPU_DIRECTORY}/cpuidle/current_driver"
MEMINFO = "proc/meminfo"
MEMORY_TOTAL_KEY = "MemTotal"
DMI = "sys/class/dmi/id"
DMI_FIELDS = ("bios_vendor", "bios_version", "bios_date", "board_name")
DEFAULT_IRQ_AFFINITY = "proc/irq/default_smp_affinity"
SYSFS_TRUE = "1"


class HugePages(TypedDict):
    enabled: str | None
    defrag: str | None


class IdleState(TypedDict):
    name: str | None
    disabled: bool | None


class CpuIdle(TypedDict):
    driver: str | None
    states: list[IdleState]


class HostState(TypedDict):
    transparentHugepage: HugePages
    kernelCmdline: str | None
    mitigations: dict[str, str]
    cpuIdle: CpuIdle
    memTotalKb: int | None
    firmware: dict[str, str | None]
    defaultIrqAffinity: str | None


# The kernel shows the active mode in brackets, "always [madvise] never"; the text is kept whole.
def huge_pages(root: Path) -> HugePages:
    return HugePages(
        enabled=read_text(root / TRANSPARENT_HUGEPAGE / "enabled"),
        defrag=read_text(root / TRANSPARENT_HUGEPAGE / "defrag"),
    )


def mitigations(root: Path) -> dict[str, str]:
    directory = root / VULNERABILITIES
    if not directory.is_dir():
        return {}
    return {path.name: read_text(path) or "" for path in sorted(directory.iterdir())}


# The idle states of one measured CPU: a deep state costs a wake-up latency on every fork-join.
def cpu_idle(root: Path, cpu: int) -> CpuIdle:
    directory = root / cpu_file(cpu, "cpuidle")
    states = sorted(directory.glob("state*"), key=lambda path: int(path.name.removeprefix("state")))
    return CpuIdle(
        driver=read_text(root / CPUIDLE_DRIVER),
        states=[IdleState(name=read_text(state / "name"), disabled=flag(read_text(state / "disable"))) for state in states],
    )


def flag(text: str | None) -> bool | None:
    return None if text is None else text == SYSFS_TRUE


def memory_total_kb(root: Path) -> int | None:
    for line in (read_text(root / MEMINFO) or "").splitlines():
        key, _, value = line.partition(":")
        if key == MEMORY_TOTAL_KEY:
            return int(value.split()[0])
    return None


def host_state(root: Path, cpus: list[int]) -> HostState:
    return HostState(
        transparentHugepage=huge_pages(root),
        kernelCmdline=read_text(root / KERNEL_CMDLINE),
        mitigations=mitigations(root),
        cpuIdle=cpu_idle(root, cpus[0] if cpus else 0),
        memTotalKb=memory_total_kb(root),
        firmware={name: read_text(root / DMI / name) for name in DMI_FIELDS},
        defaultIrqAffinity=read_text(root / DEFAULT_IRQ_AFFINITY),
    )
