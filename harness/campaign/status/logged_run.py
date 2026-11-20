"""One line of campaign.jsonl: the outcome of one run as the journal logged it."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from harness.campaign.fields import SpecFields
from harness.launcher import RunStatus

# A discarded first launch has no position in the order, so its context always lacks one.
DISCARDED_LAUNCH_PROBLEM = "orderPosition unavailable"


@dataclass(frozen=True)
class LoggedRun:
    run_id: str
    environment: str
    status: str
    seconds: float | None
    discarded: bool
    problems: tuple[str, ...]
    logged_at: datetime

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "LoggedRun":
        fields = SpecFields(data)
        seconds = fields.raw("seconds", None)
        return cls(
            run_id=fields.text("runId"),
            environment=fields.text("environment"),
            status=fields.text("status"),
            seconds=float(seconds) if isinstance(seconds, int | float) and not isinstance(seconds, bool) else None,
            discarded=fields.flag("discarded", False),
            problems=tuple(str(problem) for problem in fields.items("problems")),
            logged_at=datetime.fromisoformat(fields.text("loggedAt")),
        )

    @property
    def succeeded(self) -> bool:
        return self.status == RunStatus.DONE

    @property
    def relevant_problems(self) -> tuple[str, ...]:
        if not self.discarded:
            return self.problems
        return tuple(problem for problem in self.problems if problem != DISCARDED_LAUNCH_PROBLEM)
