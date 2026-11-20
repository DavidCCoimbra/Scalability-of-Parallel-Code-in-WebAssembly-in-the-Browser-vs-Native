from collections.abc import Sequence
from dataclasses import dataclass
from statistics import geometric_mean

from analysis.stats.bootstrap import BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED, Interval, bootstrap_interval


@dataclass(frozen=True)
class Ratio:
    value: float
    interval: Interval


def treatment_over_baseline(groups: list[list[float]]) -> float:
    treatment, baseline = groups
    return geometric_mean(treatment) / geometric_mean(baseline)


def ratio_of_geometric_means(
    baseline: Sequence[float],
    treatment: Sequence[float],
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> Ratio:
    # The treatment is resampled first; swapping the groups would change every published interval.
    interval = bootstrap_interval([treatment, baseline], treatment_over_baseline, resamples, seed)
    return Ratio(geometric_mean(treatment) / geometric_mean(baseline), interval)
