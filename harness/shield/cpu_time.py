"""CPU time of a run, and the busy time other processes left on the measured CPUs."""

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from harness.context import UNAVAILABLE, read_text, round_seconds
from harness.context.sysfs import PROC_STAT

# /proc/stat per-CPU columns: user nice system idle iowait irq softirq steal ...
# Busy time leaves out idle (3) and iowait (4). https://man7.org/linux/man-pages/man5/proc_stat.5.html
BUSY_FIELDS = (0, 1, 2, 5, 6, 7)
CPU_LINE_PREFIX = "cpu"
# Columns of /proc/<pid>/stat after the ")" that closes the command name, counted from 0
# (field 3 of proc_pid_stat(5) is index 0). https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
STAT_SESSION = 3
# These are proc_pid_stat fields 14 to 17, utime, stime, cutime and cstime, all in clock ticks
# (SC_CLK_TCK per second, usually 100).
STAT_CPU_TIMES = slice(11, 15)
FALLBACK_TICKS_PER_SECOND = 100


def clock_ticks_per_second() -> int:
    return os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else FALLBACK_TICKS_PER_SECOND


TICKS_PER_SECOND = clock_ticks_per_second()


class CpuSplit(NamedTuple):
    run_seconds: float | str
    foreign_seconds: float | str


@dataclass(frozen=True)
class CpuTimes:
    busy: dict[int, int]

    @classmethod
    def read(cls, root: Path = Path("/")) -> "CpuTimes | None":
        text = read_text(root / PROC_STAT)
        if text is None:
            return None
        busy = {}
        for line in text.splitlines():
            name, *values = line.split()
            if name.startswith(CPU_LINE_PREFIX) and name != CPU_LINE_PREFIX:
                busy[int(name.removeprefix(CPU_LINE_PREFIX))] = busy_ticks([int(value) for value in values])
        return cls(busy)

    def busy_seconds_since(self, earlier: "CpuTimes", cpus: list[int], ticks_per_second: int) -> float:
        ticks = sum(self.busy.get(cpu, 0) - earlier.busy.get(cpu, 0) for cpu in cpus)
        return round_seconds(ticks / ticks_per_second)


def busy_ticks(ticks: list[int]) -> int:
    return sum(ticks[field] for field in BUSY_FIELDS if field < len(ticks))


class CpuUsage:
    def __init__(
        self,
        cpus: list[int] | None,
        read: Callable[[], CpuTimes | None] = CpuTimes.read,
        ticks_per_second: int = TICKS_PER_SECOND,
    ):
        self.cpus = cpus
        self.read = read
        self.ticks_per_second = ticks_per_second
        self.before: CpuTimes | None = None

    def start(self) -> None:
        self.before = self.read()

    def stop(self, run_seconds: float | str) -> CpuSplit:
        after = self.read()
        if isinstance(run_seconds, str):
            return CpuSplit(UNAVAILABLE, UNAVAILABLE)
        if not self.cpus or self.before is None or after is None:
            return CpuSplit(round_seconds(run_seconds), UNAVAILABLE)
        # Busy time on the measured CPUs minus the run's own CPU time is what everything else ran
        # there during the run ("foreign" time); near 0 means the run had the CPUs to itself.
        busy = after.busy_seconds_since(self.before, self.cpus, self.ticks_per_second)
        return CpuSplit(round_seconds(run_seconds), round_seconds(busy - run_seconds))


def process_session_seconds(session: int, root: Path = Path("/"), ticks_per_second: int = TICKS_PER_SECOND) -> float | str:
    if not (root / PROC_STAT).exists():
        return UNAVAILABLE
    ticks = 0
    for stat in (root / "proc").glob("[0-9]*/stat"):
        fields = stat_fields(read_text(stat))
        if fields is not None and int(fields[STAT_SESSION]) == session:
            ticks += sum(int(value) for value in fields[STAT_CPU_TIMES])
    return round_seconds(ticks / ticks_per_second)


def stat_fields(text: str | None) -> list[str] | None:
    # The command name may contain spaces and parentheses, so split after its last ")".
    # E.g. "42 (Web Content) S 1 ...": a plain split on spaces would cut the name in two.
    if not text or ")" not in text:
        return None
    return text.rsplit(")", 1)[1].split()
