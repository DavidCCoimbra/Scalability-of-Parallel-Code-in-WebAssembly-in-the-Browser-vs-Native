import csv
import math
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from analysis.configuration import parse_k
from analysis.runs import MEASURED

WorkloadKey = tuple[str, int | None]


# Windows of 10 iterations, a 2 % band, a tolerance of 1.5 times the steady-state window
# spread, W = 1.5 times the worst observed W with a floor of 5, and no run whose steady state
# spreads by more than 25 %.
@dataclass(frozen=True)
class WarmupRule:
    window: int = 10
    band: float = 0.02
    spread_factor: float = 1.5
    margin: float = 1.5
    floor: int = 5
    max_spread: float = 0.25

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Series:
    environment: str
    workload: str
    k: int | None
    threads: int
    times: list[float]

    @property
    def workload_key(self) -> WorkloadKey:
        return self.workload, self.k

    @property
    def name(self) -> str:
        return f"{self.environment} {self.workload} k={self.k} N={self.threads}"


class UnsettledRuns(ValueError):
    pass


def window_median(times: list[float], start: int, window: int) -> float:
    return statistics.median(times[start : start + window])


def deviation(times: list[float], start: int, window: int, reference: float) -> float:
    return abs(window_median(times, start, window) / reference - 1)


# The steady state is the second half of the run; its own window-to-window spread sets how far a
# window may sit from it before it counts as still warming up, so noise is not read as warm-up.
def steady_spread(times: list[float], rule: WarmupRule, reference: float) -> float:
    half = len(times) // 2
    starts = range(half, len(times) - rule.window + 1, rule.window)
    return max((deviation(times, start, rule.window, reference) for start in starts), default=0.0)


# Slides the 10-iteration window one iteration at a time through the first half: W is the first
# start whose window median is within the tolerance of the second-half median, so the W
# iterations before it are warm-up.
def first_settled_window(times: list[float], rule: WarmupRule, reference: float, tolerance: float) -> int | None:
    half = len(times) // 2
    return next((start for start in range(half) if deviation(times, start, rule.window, reference) <= tolerance), None)


# A single slow first iteration hides inside a window median, so any iteration of the first window
# slower than every steady-state iteration (and than the band) pushes W past it.
def last_spike(times: list[float], rule: WarmupRule, reference: float) -> int:
    half = len(times) // 2
    ceiling = max(max(times[half:]), reference * (1 + rule.band))
    return max((index + 1 for index in range(rule.window) if times[index] > ceiling), default=0)


def observed_warmup(times: list[float], rule: WarmupRule) -> int | None:
    reference = statistics.median(times[len(times) // 2 :])
    spread = steady_spread(times, rule, reference)
    if spread > rule.max_spread:
        return None
    # "Close" is the larger of the 2 % band and 1.5 times the steady state's own jitter, so a noisy
    # environment is not read as one that never warms up.
    settled = first_settled_window(times, rule, reference, max(rule.band, rule.spread_factor * spread))
    if settled is None:
        return None
    return max(settled, last_spike(times, rule, reference))


def campaign_warmups(series: list[Series], rule: WarmupRule) -> dict[WorkloadKey, int]:
    unsettled = [run for run in series if observed_warmup(run.times, rule) is None]
    if unsettled:
        raise UnsettledRuns(f"runs that never settle: {', '.join(run.name for run in unsettled)}")
    worst: defaultdict[WorkloadKey, int] = defaultdict(int)
    for run in series:
        worst[run.workload_key] = max(worst[run.workload_key], observed_warmup(run.times, rule) or 0)
    return {key: max(rule.floor, math.ceil(rule.margin * value)) for key, value in worst.items()}


def series_of(rows: list[dict[str, str]]) -> Series | None:
    measured = sorted((row for row in rows if row["phase"] == MEASURED), key=lambda row: int(row["iter"]))
    if not measured:
        return None
    first = measured[0]
    times = [float(row["ns"]) for row in measured]
    return Series(first["env"], first["workload"], parse_k(first["k"]), int(first["threads"]), times)


def load_series(directory: Path) -> list[Series]:
    loaded = []
    for path in sorted(directory.glob("*.csv")):
        with path.open(newline="") as handle:
            series = series_of(list(csv.DictReader(handle)))
        if series is not None:
            loaded.append(series)
    return loaded
