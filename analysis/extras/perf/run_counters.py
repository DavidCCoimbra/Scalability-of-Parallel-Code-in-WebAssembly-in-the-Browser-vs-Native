from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from analysis.configuration import Configuration, configuration_of
from analysis.extras.perf.intervals import COUNTERS, Interval
from analysis.loading import InvalidCampaign, LoadedCampaign
from analysis.run_context import run_context

TIMED_PHASES = ("warmup", "measured")


@dataclass(frozen=True)
class Run:
    run_id: str
    configuration: Configuration
    start: float
    end: float
    operations: int


@dataclass(frozen=True)
class RunCounters:
    run: Run
    intervals: int
    per_operation: dict[str, float]


def timestamp(run_id: str, text: str | None) -> float:
    if text is None:
        raise InvalidCampaign(f"{run_id}: no startedAt or finishedAt in the run's context")
    return datetime.fromisoformat(text).timestamp()


# One atomic operation per pixel per pass of every warm-up or measured iteration.
def runs_of(campaign: LoadedCampaign) -> list[Run]:
    operations: dict[str, int] = defaultdict(int)
    configurations: dict[str, Configuration] = {}
    for row in campaign.rows:
        configurations[row["run"]] = configuration_of(row)
        if row["phase"] in TIMED_PHASES:
            operations[row["run"]] += int(row["width"]) * int(row["height"]) * int(row["passes"] or 1)
    runs = []
    for run_id in sorted(configurations):
        context = run_context(campaign.directory, run_id)
        start, end = timestamp(run_id, context.started_at), timestamp(run_id, context.finished_at)
        if not operations[run_id]:
            raise InvalidCampaign(f"{run_id}: no warm-up or measured iteration to count operations from")
        runs.append(Run(run_id, configurations[run_id], start, end, operations[run_id]))
    return runs


# Runs are sequential, so the intervals that end inside a run's window belong to that run.
def counters_of(run: Run, intervals: Iterable[Interval]) -> RunCounters:
    inside = [interval for interval in intervals if run.start < interval.end <= run.end]
    totals = {name: sum(interval.counts.get(name, 0.0) for interval in inside) for name in COUNTERS}
    return RunCounters(run, len(inside), {name: totals[name] / run.operations for name in COUNTERS})
