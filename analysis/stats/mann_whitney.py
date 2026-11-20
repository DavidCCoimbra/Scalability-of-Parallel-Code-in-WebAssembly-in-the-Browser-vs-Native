import math
from collections.abc import Sequence
from dataclasses import dataclass

CONTINUITY_CORRECTION = 0.5


@dataclass(frozen=True)
class MannWhitney:
    u: float
    z: float
    p: float


def average_ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
            end += 1
        rank = (start + end) / 2 + 1
        for position in range(start, end + 1):
            ranks[order[position]] = rank
        start = end + 1
    return ranks


def tie_term(values: Sequence[float]) -> int:
    counts: dict[float, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sum(count**3 - count for count in counts.values())


# Mann and Whitney 1947 (https://doi.org/10.1214/aoms/1177730491): U of the treatment is its rank sum
# minus n1 (n1 + 1) / 2, the number of (treatment, baseline) pairs the treatment wins, ties counting
# one half. Under H0, U has mean n1 n2 / 2 and, with ties, variance
# n1 n2 / 12 * ((n + 1) - sum(t^3 - t) / (n (n - 1))). The two-sided p comes from the normal
# approximation with a continuity correction of 0.5, as scipy.stats.mannwhitneyu(method="asymptotic").
def mann_whitney_u(baseline: Sequence[float], treatment: Sequence[float]) -> MannWhitney:
    n1, n2 = len(treatment), len(baseline)
    if n1 == 0 or n2 == 0:
        raise ValueError("both groups need at least one value")
    pooled = [*treatment, *baseline]
    n = n1 + n2
    rank_sum = sum(average_ranks(pooled)[:n1])
    u = rank_sum - n1 * (n1 + 1) / 2
    mean = n1 * n2 / 2
    variance = n1 * n2 / 12 * ((n + 1) - tie_term(pooled) / (n * (n - 1)))
    if variance <= 0:
        return MannWhitney(u, 0.0, 1.0)
    z = max(0.0, abs(u - mean) - CONTINUITY_CORRECTION) / math.sqrt(variance)
    return MannWhitney(u, math.copysign(z, u - mean), min(1.0, math.erfc(z / math.sqrt(2))))
