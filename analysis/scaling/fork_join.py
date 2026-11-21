import math
import statistics
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from analysis.configuration import ENVIRONMENTS
from analysis.runs import Row
from analysis.scaling.cutoff import NS_PER_US, CutoffPoint

# The fork-join cost F at N = 8: per run, the median of its warm calibration calls (empty
# broadcasts back to back); per environment, the median over runs. analysis.calibration writes
# the same statistic for every N, probe and phase of a campaign.
CALIBRATION_PHASE = "calibration-warm"
# Builds before schema 2 had one probe, the broadcast, and no probe column; schema 2 adds the
# empty par_iter probe ("par-iter") and names each calibration row's probe.
BROADCAST_PROBE = "broadcast"
MODEL_THREADS = 8


@dataclass(frozen=True)
class ForkJoinShare:
    percent: int

    @property
    def fraction(self) -> float:
        return self.percent / 100

    @property
    def work_column(self) -> str:
        return f"work_{self.percent}pct_us"

    @property
    def side_column(self) -> str:
        return f"side_{self.percent}pct"


# The common 100:1 rule of thumb for a fork/join threshold: a task's sequential work should
# exceed the fork overhead by more than 100 times.
RULE_OF_THUMB_SHARE = ForkJoinShare(1)
# The cutoff campaign's first prediction, kept as a looser second reading.
LOOSE_SHARE = ForkJoinShare(5)
MODEL_SHARES = (RULE_OF_THUMB_SHARE, LOOSE_SHARE)
MODEL_COLUMNS = (
    "environment",
    "workload",
    "input",
    "k",
    "threads",
    "fork_join_runs",
    "fork_join_us",
    *(column for share in MODEL_SHARES for column in (share.work_column, share.side_column)),
    "model_break_even_us",
    "model_worth_it_us",
)


@dataclass(frozen=True)
class ForkJoinCost:
    runs: int
    median_ns: float


def probe_of(row: Row) -> str:
    probe = row.get("probe")
    return str(probe) if probe else BROADCAST_PROBE


def run_calibration_medians(rows: Iterable[Row], threads: int, probe: str = BROADCAST_PROBE) -> dict[str, tuple[str, float]]:
    samples: dict[str, list[float]] = {}
    environments: dict[str, str] = {}
    for row in rows:
        if row["phase"] == CALIBRATION_PHASE and int(row["threads"]) == threads and probe_of(row) == probe:
            samples.setdefault(row["run"], []).append(float(row["ns"]))
            environments[row["run"]] = row["env"]
    return {run: (environments[run], statistics.median(values)) for run, values in samples.items()}


def fork_join_costs(rows: Iterable[Row], threads: int = MODEL_THREADS, probe: str = BROADCAST_PROBE) -> dict[str, ForkJoinCost]:
    medians: dict[str, list[float]] = {}
    for environment, median in run_calibration_medians(rows, threads, probe).values():
        medians.setdefault(environment, []).append(median)
    return {environment: ForkJoinCost(len(values), statistics.median(values)) for environment, values in medians.items()}


# The model: TN = W / N + F, with W the work of one region (T1 per pass) and F the fork-join cost.
# F is a share s of TN when W = N F (1 / s - 1): 99 N F at 1 % (each thread's W / N is 99 F, the
# 100:1 rule) and 19 N F at 5 %; speedup W / TN is 1 when W = F N / (N - 1) and efficiency is
# 0.5 when W = N F.
@dataclass(frozen=True)
class ModelPrediction:
    reference: CutoffPoint
    fork_join: ForkJoinCost

    @property
    def threads(self) -> int:
        return self.reference.threads

    @property
    def fork_join_ns(self) -> float:
        return self.fork_join.median_ns

    def work_at_share_ns(self, share: ForkJoinShare) -> float:
        return (1 / share.fraction - 1) * self.threads * self.fork_join_ns

    @property
    def break_even_ns(self) -> float:
        return self.fork_join_ns * self.threads / (self.threads - 1)

    @property
    def worth_it_ns(self) -> float:
        return self.threads * self.fork_join_ns

    # The side whose T1 is that work, scaling the reference size's T1 with the pixel count.
    def side_for(self, work_ns: float) -> float:
        return self.reference.side * math.sqrt(work_ns / self.reference.t1_ns)


def largest_side_points(points: Iterable[CutoffPoint], threads: int) -> list[CutoffPoint]:
    largest: dict[tuple[str, str, str, int | None], CutoffPoint] = {}
    for point in points:
        if point.threads != threads:
            continue
        c = point.configuration
        key = (c.environment, c.workload, c.input, c.k)
        if key not in largest or point.side > largest[key].side:
            largest[key] = point
    return sorted(largest.values(), key=lambda point: (ENVIRONMENTS.index(point.configuration.environment), point.curve))


def predictions(
    points: Iterable[CutoffPoint], costs: Mapping[str, ForkJoinCost], threads: int = MODEL_THREADS
) -> list[ModelPrediction]:
    return [
        ModelPrediction(point, costs[point.configuration.environment])
        for point in largest_side_points(points, threads)
        if point.configuration.environment in costs
    ]


def microseconds(ns: float) -> str:
    return f"{ns / NS_PER_US:.1f}"


def share_cells(prediction: ModelPrediction) -> dict[str, str]:
    cells: dict[str, str] = {}
    for share in MODEL_SHARES:
        work_ns = prediction.work_at_share_ns(share)
        cells[share.work_column] = microseconds(work_ns)
        cells[share.side_column] = f"{prediction.side_for(work_ns):.0f}"
    return cells


def model_row(prediction: ModelPrediction) -> dict[str, Any]:
    c = prediction.reference.configuration
    return {
        **dict(zip(("environment", "workload", "input", "k", "threads"), c.cells())),
        "fork_join_runs": prediction.fork_join.runs,
        "fork_join_us": microseconds(prediction.fork_join_ns),
        **share_cells(prediction),
        "model_break_even_us": microseconds(prediction.break_even_ns),
        "model_worth_it_us": microseconds(prediction.worth_it_ns),
    }


def model_rows(items: Iterable[ModelPrediction]) -> list[dict[str, Any]]:
    return [model_row(item) for item in items]
