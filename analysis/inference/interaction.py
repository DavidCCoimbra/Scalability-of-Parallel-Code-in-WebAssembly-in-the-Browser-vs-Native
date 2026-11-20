import statistics
from collections.abc import Callable, Sequence

from analysis.stats.summary import Summary

LogCenter = Callable[[Sequence[float]], float]


# On log run values the mean is the log of the geometric mean (analysis plan D2), and the median of
# the logs is the log of the median.
def log_center(center: Summary) -> LogCenter:
    return statistics.median if center is Summary.MEDIAN else statistics.fmean


def difference(first: Sequence[float], second: Sequence[float], center: LogCenter) -> float:
    return center(first) - center(second)


# Two groups give a log ratio (ABS); four give the interaction (a - b) - (c - d) of the analysis plan, the
# browser contrast minus the same contrast natively (RQ1 and RQ2).
def interaction(groups: Sequence[Sequence[float]], center: LogCenter) -> float:
    if len(groups) == 2:
        return difference(groups[0], groups[1], center)
    # On logs a difference is a ratio, log(a) - log(b) = log(a / b), so each inner difference is
    # "how many times slower is a than b", e.g. atomic over local for RQ2. Their difference, Δr, asks
    # whether that slowdown is bigger in the browser than natively; exp(Δr) is the ratio of ratios
    # (bA / bL) / (nA / nL) of the centres, 1 meaning the same gap.
    return difference(groups[0], groups[1], center) - difference(groups[2], groups[3], center)
