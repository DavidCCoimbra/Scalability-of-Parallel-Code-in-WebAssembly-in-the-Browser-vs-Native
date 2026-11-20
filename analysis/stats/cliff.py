from collections.abc import Sequence


# Cliff's delta (Cliff 1993): P(treatment > baseline) - P(treatment < baseline) over all pairs.
def cliffs_delta(baseline: Sequence[float], treatment: Sequence[float]) -> float:
    above = sum(t > b for t in treatment for b in baseline)
    below = sum(t < b for t in treatment for b in baseline)
    return (above - below) / (len(baseline) * len(treatment))
