"""The status report of a campaign as text lines."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta

from harness.campaign.status.durations import format_duration
from harness.campaign.status.progress import CampaignProgress, Tally

BAR_WIDTH = 40
BAR_DONE = "#"
BAR_TODO = "."
LABEL_WIDTH = 10
ENVIRONMENT_WIDTH = 8
SHOWN_PROBLEMS = 5
SHOWN_PERCENT_DECIMALS = 1


@dataclass(frozen=True)
class StatusReport:
    progress: CampaignProgress
    now: datetime

    def lines(self) -> list[str]:
        return [
            f"campaign  {self.progress.name}",
            *self.plan_warning(),
            self.row("progress", self.overall()),
            *self.environment_rows(),
            *self.failure_rows(),
            *self.problem_rows(),
            self.row("sessions", self.sessions()),
            self.row("elapsed", self.elapsed()),
            self.row("eta", self.eta()),
            self.row("last run", self.last_run()),
        ]

    def row(self, label: str, value: str) -> str:
        return f"{label:<{LABEL_WIDTH}}{value}"

    def plan_warning(self) -> list[str]:
        if self.progress.plan_matches_journal:
            return []
        return [self.row("warning", "campaign.json lists other runs than this spec plans; counts follow the spec")]

    def overall(self) -> str:
        tally = self.progress.tally
        return f"{bar(tally)} {percent(tally)}  {counts(tally)}"

    def environment_rows(self) -> list[str]:
        return [
            self.row("", f"{name:<{ENVIRONMENT_WIDTH}}{counts(tally)}")
            for name, tally in self.progress.environments.items()
        ]

    def failure_rows(self) -> list[str]:
        statuses = self.progress.failed_statuses
        return [self.row("failed", most_common(statuses))] if statuses else []

    def problem_rows(self) -> list[str]:
        runs = self.progress.runs_with_problems
        if not runs:
            return [self.row("problems", "none")]
        return [self.row("problems", f"{len(runs)} run(s): {most_common(self.progress.problem_counts)}")]

    def sessions(self) -> str:
        journal = self.progress.journal
        if journal.started_at is None:
            return "not started (no campaign.json yet)"
        return f"{journal.sessions}, started {clock(journal.started_at)}"

    def elapsed(self) -> str:
        started = self.progress.journal.started_at
        if started is None:
            return "-"
        if self.finished:
            last = self.progress.last_logged_at or started
            return f"{format_duration(last - started)} (finished {clock(last)})"
        paused = ", pauses between sessions included" if self.progress.journal.sessions > 1 else ""
        return format_duration(self.now - started) + paused

    def eta(self) -> str:
        if self.finished:
            return "finished"
        mean = self.progress.mean_seconds
        if mean is None:
            return "unknown until a run is logged"
        left = timedelta(seconds=mean * self.progress.tally.remaining)
        return f"{format_duration(left)} at {mean:.1f} s per run, around {clock(self.now + left)}"

    def last_run(self) -> str:
        last = self.progress.last_logged
        if last is None:
            return "none yet"
        discarded = ", discarded launch" if last.discarded else ""
        ago = format_duration(self.now - last.logged_at)
        return f"{last.run_id} ({last.status}{discarded}), {ago} ago"

    @property
    def finished(self) -> bool:
        return self.progress.tally.remaining == 0

    @property
    def text(self) -> str:
        return "\n".join(self.lines())


def bar(tally: Tally) -> str:
    filled = round(tally.fraction * BAR_WIDTH)
    return "[" + BAR_DONE * filled + BAR_TODO * (BAR_WIDTH - filled) + "]"


def percent(tally: Tally) -> str:
    return f"{100 * tally.fraction:.{SHOWN_PERCENT_DECIMALS}f}%"


def counts(tally: Tally) -> str:
    return f"{tally.done} done, {tally.failed} failed, {tally.remaining} remaining of {tally.planned}"


def most_common(counter: Counter[str]) -> str:
    shown = ", ".join(f"{count} x {item}" for item, count in counter.most_common(SHOWN_PROBLEMS))
    hidden = len(counter) - SHOWN_PROBLEMS
    return shown + (f", and {hidden} more" if hidden > 0 else "")


def clock(moment: datetime) -> str:
    return moment.astimezone().strftime("%Y-%m-%d %H:%M %Z")
