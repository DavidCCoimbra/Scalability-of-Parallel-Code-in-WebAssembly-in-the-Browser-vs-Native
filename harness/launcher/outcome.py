"""What one launch ended with, and what it measured on the way."""

from dataclasses import dataclass
from enum import StrEnum

from harness.shield import CpuSplit


class RunStatus(StrEnum):
    DONE = "done"
    ERROR = "error"
    TIMEOUT = "timeout"
    EXITED = "exited"


@dataclass(frozen=True)
class RunOutcome:
    run_id: str
    status: RunStatus
    seconds: float
    exit_code: int | None = None
    message: str | None = None


@dataclass(frozen=True)
class Teardown:
    cpu_seconds: CpuSplit
    leftover_processes: int | str
    escaped_processes: int | str


@dataclass(frozen=True)
class LaunchRecord:
    argv: list[str]
    started_at: str
    seconds: float
    loadavg_before: list[float] | str
    teardown: Teardown
    passes: int
    grain: int | None = None
