import random
from collections.abc import Callable, Sequence
from typing import NamedTuple

# Percentile bootstrap over runs (Efron and Tibshirani 1993, ch. 13), fixed by the analysis plan D3:
# 95 % intervals, 10 000 resamples, seed 0x5EED (24301).
CONFIDENCE = 0.95
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 0x5EED

Groups = Sequence[Sequence[float]]
Statistic = Callable[[list[list[float]]], float]


class Interval(NamedTuple):
    low: float
    high: float

    def map(self, function: Callable[[float], float]) -> "Interval":
        return Interval(function(self.low), function(self.high))

    def divided_by(self, divisor: float) -> "Interval":
        return Interval(self.low / divisor, self.high / divisor)


# Draws as many runs as the group has, with replacement (`Array.from(group, () =>
# group[randomInt(group.length)])`): a plausible other campaign, built from the runs we have.
def resample(generator: random.Random, groups: Groups) -> list[list[float]]:
    return [generator.choices(group, k=len(group)) for group in groups]


# Each group is resampled on its own: the groups are runs of different configurations, which are
# independent processes, so there is no pairing to keep.
# A seeded Monte Carlo: recompute the statistic on 10 000 resamples and sort the results; their
# spread stands in for the sampling error, and the fixed seed makes every rerun give the same
# interval.
def bootstrap_distribution(groups: Groups, statistic: Statistic, resamples: int, seed: int) -> list[float]:
    generator = random.Random(seed)
    return sorted(statistic(resample(generator, groups)) for _ in range(resamples))


# The percentile interval: cut (1 - confidence) / 2 off each end of the sorted distribution, 2.5 %
# at 95 %, and keep the values at the two cuts.
def percentile_interval(distribution: Sequence[float], confidence: float) -> Interval:
    tail = (1 - confidence) / 2
    last = len(distribution) - 1
    return Interval(distribution[round(tail * last)], distribution[round((1 - tail) * last)])


def bootstrap_interval(
    groups: Groups,
    statistic: Statistic,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> Interval:
    return percentile_interval(bootstrap_distribution(groups, statistic, resamples, seed), CONFIDENCE)


# Two-sided: twice the share of resamples on the smaller side of the null (0, no effect on log
# scale), capped at 1.
# The p-value is floored at one over the resamples: a distribution entirely on one side of the null
# only says that p is below what this many resamples can resolve (analysis plan D8).
def two_sided_p(distribution: Sequence[float], null: float = 0.0) -> float:
    count = len(distribution)
    below = sum(value <= null for value in distribution) / count
    above = sum(value >= null for value in distribution) / count
    return max(min(1.0, 2 * min(below, above)), 1 / count)
