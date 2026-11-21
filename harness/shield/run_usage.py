"""The two readings taken around a run on its measured CPUs."""

from dataclasses import dataclass

from harness.shield.core_activity import CoreActivity
from harness.shield.cpu_time import CpuUsage


@dataclass(frozen=True)
class RunUsage:
    cpu: CpuUsage
    cores: CoreActivity

    @classmethod
    def of_mask(cls, cpus: list[int] | None) -> "RunUsage":
        return cls(CpuUsage(cpus), CoreActivity(cpus))

    def start(self) -> None:
        self.cpu.start()
        self.cores.start()
