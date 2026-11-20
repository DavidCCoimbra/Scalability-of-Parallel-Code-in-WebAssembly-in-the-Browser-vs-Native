import math
from collections.abc import Iterable
from dataclasses import dataclass

from analysis.configuration import Configuration, CsvCell
from analysis.runs import RunSummary, values_by_configuration
from analysis.stats.skewness import skewness


@dataclass(frozen=True)
class ShapeRow:
    configuration: Configuration
    runs: int
    skewness: float
    log_skewness: float

    def cells(self) -> list[CsvCell]:
        return self.configuration.cells() + [self.runs, f"{self.skewness:.3f}", f"{self.log_skewness:.3f}"]


# The skewness of the logs next to that of the raw values shows whether the log scale of the
# contrasts makes the run distributions more symmetric.
def shape_row(configuration: Configuration, values: list[float]) -> ShapeRow:
    return ShapeRow(configuration, len(values), skewness(values), skewness([math.log(value) for value in values]))


def shape_table(runs: Iterable[RunSummary]) -> list[ShapeRow]:
    return [shape_row(configuration, values) for configuration, values in sorted(values_by_configuration(runs).items())]
