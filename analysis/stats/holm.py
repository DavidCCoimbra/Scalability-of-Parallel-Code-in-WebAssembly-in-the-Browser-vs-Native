from collections.abc import Sequence


# Holm 1979 step-down: sort ascending, multiply the i-th smallest by (m - i), cap at 1, and carry the
# running maximum so that the adjusted p-values keep the order of the raw ones.
def holm_adjusted(p_values: Sequence[float]) -> list[float]:
    # Indices sorted by p, like `[...p.keys()].sort((a, b) => p[a] - p[b])`. The smallest p pays
    # the full m-fold penalty and each later one less, since one fewer hypothesis is left to test;
    # it controls the family error like Bonferroni but is never less powerful.
    order = sorted(range(len(p_values)), key=lambda index: p_values[index])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted
