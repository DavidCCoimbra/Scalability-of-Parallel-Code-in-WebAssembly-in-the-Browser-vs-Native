from dataclasses import dataclass

from analysis.configuration import Configuration
from analysis.stats.spearman import spearman

# With 30 runs and no drift, |rho| > 0.5 has a probability of about 0.7 %, so about one
# of the campaign's configurations is expected to be flagged by chance.
# rho is Spearman's correlation of run time with run order: near 0 when the times do not trend,
# towards +1 or -1 when later runs get steadily slower or faster (drift).
DRIFT_LIMIT = 0.5
DRIFT_MINIMUM_RUNS = 10


@dataclass(frozen=True)
class OrderedValue:
    position: int
    value: float


@dataclass(frozen=True)
class OrderDrift:
    configuration: Configuration
    runs: int
    rho: float

    def line(self) -> str:
        return f"{self.configuration.label}: rho = {self.rho:+.2f} over {self.runs} runs"


def order_rho(points: list[OrderedValue]) -> float:
    return spearman([point.position for point in points], [point.value for point in points])


def order_drifts(
    observations: dict[Configuration, list[OrderedValue]],
    limit: float = DRIFT_LIMIT,
    minimum_runs: int = DRIFT_MINIMUM_RUNS,
) -> list[OrderDrift]:
    flagged = []
    for configuration, points in sorted(observations.items()):
        if len(points) < minimum_runs:
            continue
        rho = order_rho(points)
        if abs(rho) > limit:
            flagged.append(OrderDrift(configuration, len(points), rho))
    return flagged
