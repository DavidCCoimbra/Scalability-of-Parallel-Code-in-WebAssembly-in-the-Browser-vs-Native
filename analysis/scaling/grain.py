"""The U-curve of the grain sweep: time per pass against the task size."""

import math
import statistics
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from analysis.runs import RunSummary
from analysis.scaling.fork_join import ForkJoinCost
from analysis.stats.bootstrap import Interval, bootstrap_interval

NS_PER_US = 1_000
BYTES_PER_KB = 1024
# The lecture's rule of thumb (PPC 2026/27): a task's sequential work should be at least 100 times
# the fork overhead.
RULE_OF_THUMB_RATIO = 100
FILTER = "filter"
ADAPTIVE = "adaptive"
POINT_COLUMNS = ("environment", "workload", "k", "side", "grain", "runs", "time_us", "ci_low_us", "ci_high_us", "relative_to_best")
BEST_COLUMNS = (
    "environment",
    "workload",
    "k",
    "side",
    "grain_unit",
    "best_grain",
    "best_us",
    "flat_from",
    "flat_to",
    "adaptive_us",
    "adaptive_over_best",
    "fork_join_us",
    "grain_100f",
    "task_cost_ns",
    "task_cost_low_ns",
    "task_cost_high_ns",
    "grain_100task",
)


@dataclass(frozen=True, order=True)
class Curve:
    environment: str
    workload: str
    k: int | None
    side: int
    threads: int

    @property
    def unit(self) -> str:
        return "rows" if self.workload == FILTER else "KB"

    # How many grain units the image holds: rows for the filter, KB for the local histogram.
    @property
    def units(self) -> float:
        return self.side if self.workload == FILTER else self.side * self.side / BYTES_PER_KB


@dataclass(frozen=True)
class GrainPoint:
    curve: Curve
    grain: int | None
    runs: int
    time_ns: float
    interval: Interval

    @property
    def label(self) -> str:
        return ADAPTIVE if self.grain is None else str(self.grain)


def geometric_mean(groups: list[list[float]]) -> float:
    return statistics.geometric_mean(groups[0])


def grain_points(summaries: Iterable[RunSummary], side: int, grains: Mapping[str, int | None]) -> list[GrainPoint]:
    groups: dict[tuple[Curve, int | None], list[float]] = {}
    for run in summaries:
        c = run.configuration
        curve = Curve(c.environment, c.workload, c.k, side, c.threads)
        groups.setdefault((curve, grains.get(run.run)), []).append(run.value)
    return [
        GrainPoint(curve, grain, len(values), statistics.geometric_mean(values), bootstrap_interval([values], geometric_mean))
        for (curve, grain), values in sorted(groups.items(), key=lambda item: (item[0][0], sort_grain(item[0][1])))
    ]


def sort_grain(grain: int | None) -> float:
    return -math.inf if grain is None else grain


def curves(points: Iterable[GrainPoint]) -> dict[Curve, list[GrainPoint]]:
    series: dict[Curve, list[GrainPoint]] = {}
    for point in points:
        series.setdefault(point.curve, []).append(point)
    return series


@dataclass(frozen=True)
class BestGrain:
    curve: Curve
    best: GrainPoint
    flat: list[GrainPoint]
    adaptive: GrainPoint | None
    fork_join: ForkJoinCost | None
    finest: GrainPoint

    # The sequential work of one grain unit, from the adaptive split: N threads for its time per
    # pass, spread over the image's units. An estimate: it charges the fork-join to the work.
    @property
    def unit_work_ns(self) -> float | None:
        if self.adaptive is None:
            return None
        return self.adaptive.time_ns * self.curve.threads / self.curve.units

    # The smallest grain whose task work is at least 100 F (the lecture's rule).
    @property
    def grain_100f(self) -> float | None:
        unit = self.unit_work_ns
        if unit is None or self.fork_join is None:
            return None
        return RULE_OF_THUMB_RATIO * self.fork_join.median_ns / unit

    # The cost of one more task inside a running region: the finest grain's extra time over the
    # best, times N, over its extra tasks. It is read off the same sweep, so the grain it
    # gives below is a consistency check, not an independent prediction.
    # The best is the minimum of noisy means, so the estimate leans high; the interval combines the
    # two points' intervals at their extremes (a rough bound, like the flat region).
    @property
    def task_cost_ns(self) -> float | None:
        return self.task_cost(self.finest.time_ns, self.best.time_ns)

    @property
    def task_cost_interval(self) -> Interval | None:
        low = self.task_cost(self.finest.interval.low, self.best.interval.high)
        high = self.task_cost(self.finest.interval.high, self.best.interval.low)
        return None if low is None or high is None else Interval(low, high)

    def task_cost(self, finest_ns: float, best_ns: float) -> float | None:
        finest, best = self.finest.grain, self.best.grain
        if finest is None or best is None or finest >= best:
            return None
        extra_tasks = self.curve.units / finest - self.curve.units / best
        return (finest_ns - best_ns) * self.curve.threads / extra_tasks

    # The smallest grain whose task work is at least 100 times the cost per task.
    @property
    def grain_100task(self) -> float | None:
        unit, cost = self.unit_work_ns, self.task_cost_ns
        if unit is None or cost is None:
            return None
        return RULE_OF_THUMB_RATIO * cost / unit


# The best grain is the fixed grain with the lowest time; the flat region is the run of neighbouring
# fixed grains, around the best, whose intervals overlap the best's (pointwise intervals, a rough
# guide, as for the cutoff).
def best_grain(curve: Curve, points: Sequence[GrainPoint], fork_join: ForkJoinCost | None) -> BestGrain | None:
    fixed = [point for point in points if point.grain is not None]
    if not fixed:
        return None
    best = min(fixed, key=lambda point: point.time_ns)
    flat = contiguous_flat(fixed, best)
    adaptive = next((point for point in points if point.grain is None), None)
    finest = min(fixed, key=lambda point: point.grain or 0)
    return BestGrain(curve, best, flat, adaptive, fork_join, finest)


def contiguous_flat(fixed: Sequence[GrainPoint], best: GrainPoint) -> list[GrainPoint]:
    ordered = sorted(fixed, key=lambda point: point.grain or 0)
    at = ordered.index(best)
    first = last = at
    while first > 0 and ordered[first - 1].interval.low <= best.interval.high:
        first -= 1
    while last + 1 < len(ordered) and ordered[last + 1].interval.low <= best.interval.high:
        last += 1
    return ordered[first : last + 1]


def best_grains(points: Iterable[GrainPoint], costs: Mapping[str, ForkJoinCost]) -> list[BestGrain]:
    found = (best_grain(curve, series, costs.get(curve.environment)) for curve, series in curves(points).items())
    return [best for best in found if best is not None]


def us(ns: float) -> str:
    return f"{ns / NS_PER_US:.1f}"


def point_rows(points: Sequence[GrainPoint]) -> list[dict[str, Any]]:
    fastest = {curve: min(point.time_ns for point in series if point.grain is not None) for curve, series in curves(points).items() if any(p.grain is not None for p in series)}
    return [
        {
            "environment": p.curve.environment,
            "workload": p.curve.workload,
            "k": "" if p.curve.k is None else p.curve.k,
            "side": p.curve.side,
            "grain": p.label,
            "runs": p.runs,
            "time_us": us(p.time_ns),
            "ci_low_us": us(p.interval.low),
            "ci_high_us": us(p.interval.high),
            "relative_to_best": f"{p.time_ns / fastest[p.curve]:.3f}" if p.curve in fastest else "",
        }
        for p in points
    ]


def best_rows(items: Iterable[BestGrain]) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        c = item.curve
        grains = [point.grain for point in item.flat if point.grain is not None]
        rows.append(
            {
                "environment": c.environment,
                "workload": c.workload,
                "k": "" if c.k is None else c.k,
                "side": c.side,
                "grain_unit": c.unit,
                "best_grain": item.best.grain,
                "best_us": us(item.best.time_ns),
                "flat_from": min(grains),
                "flat_to": max(grains),
                "adaptive_us": "" if item.adaptive is None else us(item.adaptive.time_ns),
                "adaptive_over_best": "" if item.adaptive is None else f"{item.adaptive.time_ns / item.best.time_ns:.3f}",
                "fork_join_us": "" if item.fork_join is None else us(item.fork_join.median_ns),
                "grain_100f": "" if item.grain_100f is None else f"{item.grain_100f:.1f}",
                "task_cost_ns": "" if item.task_cost_ns is None else f"{item.task_cost_ns:.0f}",
                "task_cost_low_ns": "" if item.task_cost_interval is None else f"{item.task_cost_interval.low:.0f}",
                "task_cost_high_ns": "" if item.task_cost_interval is None else f"{item.task_cost_interval.high:.0f}",
                "grain_100task": "" if item.grain_100task is None else f"{item.grain_100task:.1f}",
            }
        )
    return rows
