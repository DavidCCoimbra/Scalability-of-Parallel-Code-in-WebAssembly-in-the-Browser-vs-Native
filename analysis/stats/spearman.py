import statistics
from collections.abc import Sequence


def tie_end(values: Sequence[float], order: list[int], start: int) -> int:
    end = start
    while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
        end += 1
    return end


# Replaces each value by its 1-based rank in sorted order; a run of tied values shares the
# average of the ranks it spans, so [10, 20, 20, 30] gives [1, 2.5, 2.5, 4].
def ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    result = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = tie_end(values, order, start)
        for position in range(start, end + 1):
            result[order[position]] = (start + end) / 2 + 1
        start = end + 1
    return result


# Spearman's rho as the Pearson correlation of the ranks, with tied values sharing their average rank.
def spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    covariance = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    spread = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return covariance / spread if spread else 0.0
