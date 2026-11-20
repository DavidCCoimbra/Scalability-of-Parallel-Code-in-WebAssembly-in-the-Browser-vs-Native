import math
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from analysis.scaling.cutoff import NS_PER_US, CurveKey, CutoffPoint, curves

# The two cutoffs. Break-even is where parallel stops being slower than one thread; "worth
# it" is where half of the N threads' capacity is put to use.
BREAK_EVEN_SPEEDUP = 1.0
WORTH_IT_EFFICIENCY = 0.5
ESTIMATE_COLUMNS = (
    "environment",
    "workload",
    "input",
    "k",
    "threads",
    "criterion",
    "threshold_speedup",
    "placement",
    "side",
    "side_low",
    "side_high",
    "work_us",
)


class Criterion(StrEnum):
    BREAK_EVEN = "break-even"
    WORTH_IT = "worth-it"

    def threshold(self, threads: int) -> float:
        return BREAK_EVEN_SPEEDUP if self is Criterion.BREAK_EVEN else WORTH_IT_EFFICIENCY * threads


class Placement(StrEnum):
    CROSSED = "crossed"
    PAYS_AT_EVERY_SIZE = "below-smallest-size"
    NEVER_PAYS = "above-largest-size"


@dataclass(frozen=True)
class Crossing:
    placement: Placement
    side: float | None = None
    work_us: float | None = None


def log_interpolate(low: float, high: float, fraction: float) -> float:
    return math.exp(math.log(low) + fraction * (math.log(high) - math.log(low)))


# Walks down from the largest size and stops at the first pair of neighbouring sizes where the
# speedup goes from under the threshold to at or above it. Between them the speedup is taken as
# linear in log size; the work T1 per pass, which grows like the pixel count, as linear in log-log.
def crossing(points: Sequence[CutoffPoint], speedup: Callable[[CutoffPoint], float], threshold: float) -> Crossing:
    if speedup(points[-1]) < threshold:
        return Crossing(Placement.NEVER_PAYS)
    for smaller, larger in reversed(list(zip(points, points[1:]))):
        below, above = speedup(smaller), speedup(larger)
        if below < threshold <= above:
            fraction = (threshold - below) / (above - below)
            side = log_interpolate(smaller.side, larger.side, fraction)
            work = log_interpolate(smaller.t1_ns, larger.t1_ns, fraction) / NS_PER_US
            return Crossing(Placement.CROSSED, side, work)
    return Crossing(Placement.PAYS_AT_EVERY_SIZE)


@dataclass(frozen=True)
class CutoffEstimate:
    curve: CurveKey
    criterion: Criterion
    threshold: float
    estimate: Crossing
    smallest: Crossing
    largest: Crossing


# The interval bounds come from the curves of the speedup's interval bounds at each size: the upper
# bounds cross first (smallest side), the lower bounds last. They are pointwise 95 % intervals, not
# a joint band, so the side interval is a rough guide, not a confidence interval.
def estimate(curve: CurveKey, points: Sequence[CutoffPoint], criterion: Criterion) -> CutoffEstimate:
    threshold = criterion.threshold(curve[-1])
    return CutoffEstimate(
        curve,
        criterion,
        threshold,
        crossing(points, lambda point: point.speedup, threshold),
        crossing(points, lambda point: point.speedup_interval.high, threshold),
        crossing(points, lambda point: point.speedup_interval.low, threshold),
    )


def estimates(points: Iterable[CutoffPoint]) -> list[CutoffEstimate]:
    return [
        estimate(curve, series, criterion)
        for curve, series in curves(points).items()
        if curve[-1] > 1
        for criterion in Criterion
    ]


def side_cell(value: float | None) -> str:
    return "" if value is None else f"{value:.0f}"


def estimate_row(item: CutoffEstimate) -> dict[str, Any]:
    environment, workload, input_kind, k, threads = item.curve
    return {
        "environment": environment,
        "workload": workload,
        "input": input_kind,
        "k": "" if k is None else k,
        "threads": threads,
        "criterion": item.criterion,
        "threshold_speedup": f"{item.threshold:.3f}",
        "placement": item.estimate.placement,
        "side": side_cell(item.estimate.side),
        "side_low": side_cell(item.smallest.side),
        "side_high": side_cell(item.largest.side),
        "work_us": "" if item.estimate.work_us is None else f"{item.estimate.work_us:.1f}",
    }


def estimate_rows(items: Iterable[CutoffEstimate]) -> list[dict[str, Any]]:
    return [estimate_row(item) for item in items]
