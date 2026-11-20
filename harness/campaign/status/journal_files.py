"""Read-only view of what a campaign wrote about itself: campaign.json and campaign.jsonl."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from harness.campaign.fields import SpecFields
from harness.campaign.journal import LOG_FILE, METADATA_FILE
from harness.campaign.status.logged_run import LoggedRun


@dataclass(frozen=True)
class JournalFiles:
    planned_run_ids: tuple[str, ...] | None
    started_at: datetime | None
    resumed_at: tuple[datetime, ...]
    logged: tuple[LoggedRun, ...]

    @classmethod
    def read(cls, results: Path) -> "JournalFiles":
        metadata = results / METADATA_FILE
        log = results / LOG_FILE
        meta = SpecFields(json.loads(metadata.read_text()) if metadata.exists() else {})
        lines = log.read_text().splitlines() if log.exists() else []
        started = meta.optional_text("startedAt")
        runs = meta.raw("runs", None)
        return cls(
            planned_run_ids=tuple(str(run) for run in runs) if isinstance(runs, list) else None,
            started_at=datetime.fromisoformat(started) if started else None,
            resumed_at=tuple(datetime.fromisoformat(str(stamp)) for stamp in list_or_empty(meta.raw("resumedAt", []))),
            logged=tuple(LoggedRun.from_json(json.loads(line)) for line in lines if line.strip()),
        )

    @property
    def sessions(self) -> int:
        return 0 if self.started_at is None else 1 + len(self.resumed_at)


def list_or_empty(value: object) -> list[object]:
    return value if isinstance(value, list) else []
