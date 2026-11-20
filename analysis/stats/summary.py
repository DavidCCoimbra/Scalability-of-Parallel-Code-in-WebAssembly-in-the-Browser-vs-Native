import statistics
from collections.abc import Sequence
from enum import Enum


class Summary(Enum):
    MEDIAN = "median"
    MEAN = "mean"
    GEOMETRIC = "geometric"

    def of(self, values: Sequence[float]) -> float:
        if self is Summary.MEDIAN:
            return statistics.median(values)
        if self is Summary.MEAN:
            return statistics.fmean(values)
        return statistics.geometric_mean(values)


# Analysis plan D1 and D2: the median of a run's measured iterations, then the geometric
# mean of the run values of a configuration.
RUN_SUMMARY = Summary.MEDIAN
CONFIGURATION_CENTER = Summary.GEOMETRIC
