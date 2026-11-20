"""One run of the plan, and the id its files and systemd scope are named after."""

from dataclasses import dataclass

from harness.campaign.workload import WorkloadSpec
from harness.context import RunEnvironment

DISCARDED_POSITION = -1
POSITION_DIGITS = 4


@dataclass(frozen=True)
class PlannedRun:
    position: int
    environment: RunEnvironment
    workload: WorkloadSpec
    threads: int
    repetition: int
    campaign: str
    discarded: bool = False
    session: int = 0

    @property
    def run_id(self) -> str:
        return f"{self.prefix}-{self.environment}-{self.workload.workload}-{self.workload.label}-n{self.threads}-r{self.repetition}"

    @property
    def prefix(self) -> str:
        if self.discarded:
            return f"{self.campaign}-discard{self.session}"
        return f"{self.campaign}-{self.position:0{POSITION_DIGITS}d}"

    @property
    def order_position(self) -> int | None:
        return None if self.discarded else self.position
