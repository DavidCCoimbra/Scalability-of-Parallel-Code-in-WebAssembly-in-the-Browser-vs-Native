from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from matplotlib.axes import Axes

from analysis.campaign import image_side
from analysis.configuration import ENVIRONMENTS, workload_label
from analysis.figures.pyplot import plt
from analysis.figures.style import BAND_ALPHA, COLORS, LEGEND_SIZE, MARKER_SIZE, PANEL_HEIGHT, PANEL_WIDTH, TITLE_SIZE
from analysis.runs import run_summaries
from analysis.scaling.table import scaling_table
from analysis.stats.summary import CONFIGURATION_CENTER, RUN_SUMMARY
from harness.collect import collect

# The size sweep is read at the campaign's largest N.
SWEEP_THREADS = 8


@dataclass(frozen=True)
class SizePoint:
    side: int
    speedup: float
    low: float
    high: float


SizeCurves = dict[str, dict[str, list[SizePoint]]]


def size_points(directories: list[Path]) -> SizeCurves:
    points: SizeCurves = defaultdict(lambda: defaultdict(list))
    for directory in directories:
        side = image_side(directory)
        for row in scaling_table(run_summaries(collect(directory).rows, RUN_SUMMARY), CONFIGURATION_CENTER):
            c = row.configuration
            if c.threads != SWEEP_THREADS or row.speedup is None or row.speedup_interval is None:
                continue
            low, high = row.speedup_interval
            points[workload_label(c.workload, c.k)][c.environment].append(SizePoint(side, row.speedup, low, high))
    return points


def size_panel(axis: Axes, workload: str, series: dict[str, list[SizePoint]], sides: list[int]) -> None:
    for environment in ENVIRONMENTS:
        data = sorted(series.get(environment, []), key=lambda point: point.side)
        if not data:
            continue
        xs = [point.side for point in data]
        color = COLORS[environment]
        axis.plot(xs, [point.speedup for point in data], marker="o", ms=MARKER_SIZE, color=color, label=environment)
        axis.fill_between(xs, [point.low for point in data], [point.high for point in data], color=color, alpha=BAND_ALPHA)
    axis.set_xticks(sides, [str(side) for side in sides])
    axis.set_title(workload, fontsize=TITLE_SIZE)


def sizes_figure(points: SizeCurves, output: Path) -> None:
    sides = sorted({point.side for series in points.values() for runs in series.values() for point in runs})
    figure, axes = plt.subplots(1, len(points), figsize=(PANEL_WIDTH * len(points), PANEL_HEIGHT), squeeze=False)
    for axis, (workload, series) in zip(axes.flat, sorted(points.items())):
        size_panel(axis, workload, series, sides)
    axes.flat[0].legend(fontsize=LEGEND_SIZE)
    figure.supxlabel("image side (pixels)")
    figure.supylabel(f"speedup at N = {SWEEP_THREADS}")
    figure.tight_layout()
    output.mkdir(parents=True, exist_ok=True)
    figure.savefig(output / "pilot-sizes.pdf")
