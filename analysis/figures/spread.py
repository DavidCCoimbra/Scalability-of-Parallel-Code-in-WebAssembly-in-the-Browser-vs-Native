import csv
import statistics
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TextIO

from analysis.configuration import ENVIRONMENTS, Configuration, CsvCell, Input, Workload
from analysis.runs import RunSummary, values_by_configuration
from analysis.scaling.output import CONFIGURATION_COLUMNS

NANOSECONDS_PER_MILLISECOND = 1e6
SPREAD_COLUMNS = (
    *CONFIGURATION_COLUMNS,
    "runs",
    "min_ms",
    "q1_ms",
    "median_ms",
    "q3_ms",
    "max_ms",
    "iqr_over_median",
    "max_over_median",
)


@dataclass(frozen=True)
class DistributionPanel:
    title: str
    workload: str
    input: str
    k: int | None
    threads: int

    def configuration(self, environment: str) -> Configuration:
        return Configuration(environment, self.workload, self.input, self.k, self.threads)


# RQ1's filter at both ends of the thread sweep and RQ2's atomic histogram at the two ends of the
# contention sweep, at the primary N.
CAMPAIGN_PANELS = (
    DistributionPanel("filter N=1", Workload.FILTER, Input.NOISE, None, 1),
    DistributionPanel("filter N=8", Workload.FILTER, Input.NOISE, None, 8),
    DistributionPanel("atomic k=1", Workload.HIST_ATOMIC, Input.FEW_COLORS, 1, 8),
    DistributionPanel("atomic k=256", Workload.HIST_ATOMIC, Input.FEW_COLORS, 256, 8),
)


@dataclass(frozen=True)
class Spread:
    environment: str
    milliseconds: list[float]

    @property
    def quartiles(self) -> tuple[float, float, float]:
        low, median, high = statistics.quantiles(self.milliseconds, n=4, method="inclusive")
        return low, median, high

    def cells(self) -> list[CsvCell]:
        low, median, high = self.quartiles
        largest = self.milliseconds[-1]
        values = (self.milliseconds[0], low, median, high, largest)
        return [
            len(self.milliseconds),
            *(f"{value:.3f}" for value in values),
            f"{(high - low) / median:.4f}",
            f"{largest / median:.4f}",
        ]


def panel_spreads(panel: DistributionPanel, runs: Iterable[RunSummary]) -> list[Spread]:
    groups = values_by_configuration(runs)
    return [
        Spread(environment, sorted(value / NANOSECONDS_PER_MILLISECOND for value in groups[panel.configuration(environment)]))
        for environment in ENVIRONMENTS
        if panel.configuration(environment) in groups
    ]


def write_spreads(panels: Iterable[tuple[DistributionPanel, list[Spread]]], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(SPREAD_COLUMNS)
    for panel, spreads in panels:
        for spread in spreads:
            writer.writerow([*panel.configuration(spread.environment).cells(), *spread.cells()])
