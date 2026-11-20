import math
from collections.abc import Iterable
from dataclasses import replace

from analysis.inference.cells import Cells, absolute_cells, log_groups, rq1_cells, rq2_cells
from analysis.inference.contrast import Contrast
from analysis.inference.family import BONFERRONI_CONFIDENCE, FAMILY_ALPHA, primary_flags
from analysis.inference.interaction import LogCenter, interaction, log_center
from analysis.runs import RunSummary
from analysis.stats.bootstrap import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    CONFIDENCE,
    bootstrap_distribution,
    percentile_interval,
    two_sided_p,
)
from analysis.stats.holm import holm_adjusted
from analysis.stats.summary import CONFIGURATION_CENTER, Summary

# The campaign's largest thread count, the 8 P-cores.
DEFAULT_MAX_THREADS = 8


# The estimate and the bootstrap stay in log space, where differences are additive; only the
# interval ends go back to ratios with math.exp, for reporting. The primary contrasts also get
# a Bonferroni interval: 10 contrasts share alpha = 0.05, so each gets 1 - 0.05 / 10 = 99.5 %
# (family.py).
def estimate(cells: Cells, center: LogCenter, resamples: int, seed: int, primary: bool) -> Contrast:
    def statistic(groups: list[list[float]]) -> float:
        return interaction(groups, center)

    distribution = bootstrap_distribution(cells.groups, statistic, resamples, seed)
    contrast = Contrast(
        cells.question,
        cells.configuration,
        interaction(cells.groups, center),
        percentile_interval(distribution, CONFIDENCE).map(math.exp),
    )
    if not primary:
        return contrast
    return replace(
        contrast,
        primary=True,
        primary_interval=percentile_interval(distribution, BONFERRONI_CONFIDENCE).map(math.exp),
        p=two_sided_p(distribution),
    )


# Only the primary contrasts carry a p-value, so they are exactly the family Holm adjusts.
def with_holm(results: list[Contrast]) -> list[Contrast]:
    family = [(index, contrast.p) for index, contrast in enumerate(results) if contrast.p is not None]
    adjusted = holm_adjusted([p for _, p in family])
    corrected = list(results)
    for (index, _), holm_p in zip(family, adjusted):
        corrected[index] = replace(results[index], holm_p=holm_p, rejected=holm_p <= FAMILY_ALPHA)
    return corrected


def contrasts(
    runs: Iterable[RunSummary],
    center: Summary = CONFIGURATION_CENTER,
    max_threads: int = DEFAULT_MAX_THREADS,
    partial: bool = False,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> list[Contrast]:
    groups = log_groups(runs)
    all_cells = rq2_cells(groups) + rq1_cells(groups) + absolute_cells(groups)
    flags = primary_flags(all_cells, max_threads, partial)
    statistic = log_center(center)
    results = [estimate(cells, statistic, resamples, seed, primary) for cells, primary in zip(all_cells, flags)]
    return with_holm(results)
