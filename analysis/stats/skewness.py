import statistics
from collections.abc import Sequence


# Moment coefficient of skewness g1 = m3 / m2^1.5, with population (not sample-corrected) moments.
def skewness(values: Sequence[float]) -> float:
    mean = statistics.fmean(values)
    second = statistics.fmean((value - mean) ** 2 for value in values)
    if second == 0:
        return 0.0
    third = statistics.fmean((value - mean) ** 3 for value in values)
    scale: float = second**1.5
    return third / scale
