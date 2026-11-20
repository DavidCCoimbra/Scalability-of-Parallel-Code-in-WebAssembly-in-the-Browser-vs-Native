import math
import random
import statistics
from collections.abc import Sequence
from pathlib import Path

from analysis.inference.cells import Cells, log_groups, rq1_cells, rq2_cells
from analysis.inference.family import BONFERRONI_CONFIDENCE
from analysis.inference.interaction import interaction, log_center
from analysis.runs import run_summaries
from analysis.stats.bootstrap import bootstrap_distribution, percentile_interval
from analysis.stats.summary import CONFIGURATION_CENTER, RUN_SUMMARY
from harness.collect import collect

# Run counts tried on the 30-run pilot, the plan's floor of 10 runs (D3), and
# the c / sqrt(n) fit limited to n <= 20 because larger subsamples overlap almost fully with the
# pilot and understate the width of a new sample.
RUN_SIZES = (5, 10, 15, 20, 25, 30)
RUN_FLOOR = 10
LARGEST_FIT = 20
CENTER = log_center(CONFIGURATION_CENTER)

Widths = dict[int, float]


def statistic(groups: list[list[float]]) -> float:
    return interaction(groups, CENTER)


# Simulates a campaign of `size` runs: draw that many pilot runs without replacement, bootstrap
# the 99.5 % interval, and average its half-width over the subsamples.
def half_width(groups: Sequence[Sequence[float]], size: int, subsamples: int, resamples: int, seed: int) -> float:
    generator = random.Random(seed)
    widths = []
    for index in range(subsamples):
        drawn = [generator.sample(group, min(size, len(group))) for group in groups]
        low, high = percentile_interval(bootstrap_distribution(drawn, statistic, resamples, seed + index), BONFERRONI_CONFIDENCE)
        widths.append((high - low) / 2)
    return statistics.fmean(widths)


def meets_target(widths: dict[str, Widths], size: int, target: float) -> bool:
    return all(by_size.get(size, float("inf")) <= target for by_size in widths.values())


def choose_runs(widths: dict[str, Widths], target: float, floor: int = RUN_FLOOR) -> int | None:
    sizes = sorted({size for by_size in widths.values() for size in by_size if size >= floor})
    return next((size for size in sizes if meets_target(widths, size, target)), None)


# Least squares of width = c / sqrt(n) through the origin: c = sum(w / sqrt(n)) / sum(1 / n).
# An interval narrows like 1 / sqrt(n): four times the runs, half the width. Fitting c, then
# solving c / sqrt(n) = target, gives n = (c / target) ** 2, rounded up.
def extrapolated_runs(widths: Widths, target: float, largest_fit: int = LARGEST_FIT) -> int:
    fitted = {size: width for size, width in widths.items() if size <= largest_fit}
    scale = sum(width / math.sqrt(size) for size, width in fitted.items()) / sum(1 / size for size in fitted)
    return math.ceil((scale / target) ** 2)


def contrast_label(cells: Cells) -> str:
    c = cells.configuration
    return f"{cells.question} {c.environment} {c.workload} k={c.k} N={c.threads}"


def cells_widths(cells: Cells, subsamples: int, resamples: int) -> Widths:
    groups = [list(group) for group in cells.groups]
    available = min(len(group) for group in groups)
    return {
        size: half_width(groups, size, subsamples, resamples, seed=size) for size in RUN_SIZES if size <= available
    }


def contrast_widths(directories: list[Path], subsamples: int, resamples: int) -> dict[str, Widths]:
    rows = [row for directory in directories for row in collect(directory).rows]
    groups = log_groups(run_summaries(rows, RUN_SUMMARY))
    return {contrast_label(cells): cells_widths(cells, subsamples, resamples) for cells in rq2_cells(groups) + rq1_cells(groups)}
