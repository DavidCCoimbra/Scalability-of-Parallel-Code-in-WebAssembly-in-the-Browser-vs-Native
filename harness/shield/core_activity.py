"""What each measured CPU did during a run: its busy time, and its frequency before and after."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from harness.context import UNAVAILABLE, read_text, round_seconds
from harness.context.json_value import JsonValue
from harness.context.sysfs import cpu_file
from harness.shield.cpu_time import TICKS_PER_SECOND, CpuTimes

# The kernel's figure for the CPU's frequency, in kHz. On x86 it is the average measured over
# that CPU's last scheduler tick, so it is recent for a CPU that just worked and old for one
# that sat idle. https://docs.kernel.org/admin-guide/pm/cpufreq.html
CURRENT_FREQUENCY = "cpufreq/scaling_cur_freq"


def read_khz(cpu: int, root: Path = Path("/")) -> int | None:
    text = read_text(root / cpu_file(cpu, CURRENT_FREQUENCY))
    return int(text) if text is not None and text.isdigit() else None


@dataclass(frozen=True)
class CoreSnapshot:
    times: CpuTimes | None
    khz: dict[int, int | None]

    @classmethod
    def take(cls, cpus: list[int], root: Path = Path("/")) -> "CoreSnapshot":
        return cls(CpuTimes.read(root), {cpu: read_khz(cpu, root) for cpu in cpus})


class CoreActivity:
    def __init__(
        self,
        cpus: list[int] | None,
        snapshot: Callable[[list[int]], CoreSnapshot] = CoreSnapshot.take,
        ticks_per_second: int = TICKS_PER_SECOND,
    ):
        self.cpus = cpus
        self.snapshot = snapshot
        self.ticks_per_second = ticks_per_second
        self.before: CoreSnapshot | None = None

    def start(self) -> None:
        if self.cpus:
            self.before = self.snapshot(self.cpus)

    def stop(self) -> JsonValue:
        if not self.cpus or self.before is None:
            return UNAVAILABLE
        after = self.snapshot(self.cpus)
        return {str(cpu): self.core(cpu, self.before, after) for cpu in self.cpus}

    def core(self, cpu: int, before: CoreSnapshot, after: CoreSnapshot) -> JsonValue:
        busy = None
        if before.times is not None and after.times is not None:
            busy = after.times.busy_seconds_since(before.times, [cpu], self.ticks_per_second)
        return {"busySeconds": busy, "khzBefore": before.khz.get(cpu), "khzAfter": after.khz.get(cpu)}
