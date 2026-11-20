"""Progress of a campaign: its plan against the latest logged outcome of every planned run."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from statistics import fmean

from harness.campaign.planned_run import PlannedRun
from harness.campaign.status.journal_files import JournalFiles
from harness.campaign.status.logged_run import LoggedRun
from harness.context import RunEnvironment


@dataclass(frozen=True)
class Tally:
    planned: int
    done: int
    failed: int

    @property
    def remaining(self) -> int:
        return self.planned - self.done - self.failed

    @property
    def fraction(self) -> float:
        return (self.done + self.failed) / self.planned if self.planned else 1.0


@dataclass(frozen=True)
class CampaignProgress:
    name: str
    plan: tuple[PlannedRun, ...]
    journal: JournalFiles

    @property
    def latest(self) -> dict[str, LoggedRun]:
        # A rerun with --retry-failed logs the same run id again; the last line is its current outcome.
        return {run.run_id: run for run in self.journal.logged}

    @property
    def planned_outcomes(self) -> dict[str, LoggedRun]:
        latest = self.latest
        return {run.run_id: latest[run.run_id] for run in self.plan if run.run_id in latest}

    @property
    def tally(self) -> Tally:
        return self.tally_of(self.plan)

    @property
    def environments(self) -> dict[str, Tally]:
        planned = {run.environment for run in self.plan}
        return {
            str(environment): self.tally_of(tuple(run for run in self.plan if run.environment == environment))
            for environment in RunEnvironment
            if environment in planned
        }

    def tally_of(self, runs: tuple[PlannedRun, ...]) -> Tally:
        outcomes = self.planned_outcomes
        logged = [outcomes[run.run_id] for run in runs if run.run_id in outcomes]
        done = sum(1 for run in logged if run.succeeded)
        return Tally(planned=len(runs), done=done, failed=len(logged) - done)

    @property
    def failed_statuses(self) -> Counter[str]:
        return Counter(run.status for run in self.planned_outcomes.values() if not run.succeeded)

    @property
    def runs_with_problems(self) -> tuple[LoggedRun, ...]:
        return tuple(run for run in self.latest.values() if run.relevant_problems)

    @property
    def problem_counts(self) -> Counter[str]:
        return Counter(problem for run in self.runs_with_problems for problem in run.relevant_problems)

    @property
    def mean_seconds(self) -> float | None:
        seconds = [run.seconds for run in self.journal.logged if not run.discarded and run.seconds is not None]
        return fmean(seconds) if seconds else None

    @property
    def last_logged(self) -> LoggedRun | None:
        return max(self.journal.logged, key=lambda run: run.logged_at, default=None)

    @property
    def last_logged_at(self) -> datetime | None:
        last = self.last_logged
        return None if last is None else last.logged_at

    @property
    def plan_matches_journal(self) -> bool:
        recorded = self.journal.planned_run_ids
        return recorded is None or recorded == tuple(run.run_id for run in self.plan)
