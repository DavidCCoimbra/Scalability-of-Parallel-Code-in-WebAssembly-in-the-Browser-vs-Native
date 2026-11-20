from collections.abc import Sequence
from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter

from analysis.configuration import workload_label
from analysis.figures.pyplot import plt
from analysis.figures.style import (
    BAND_ALPHA,
    COLORS,
    LEGEND_SIZE,
    MARKER_SIZE,
    PANEL_WIDTH,
    REFERENCE_COLOR,
    REFERENCE_STYLE,
    REFERENCE_WIDTH,
    TITLE_SIZE,
)
from analysis.scaling.grain import NS_PER_US, Curve, GrainPoint, curves

GRAIN_LOG_BASE = 2
PANEL_HEIGHT = 2.6
LEGEND_WIDTH = 1.4


# One panel per workload and size: time per pass against the fixed grain (log-log), with the
# adaptive split as a dashed line in the environment's colour. sides: the image sides to draw,
# all by default; the paper draws 8192^2 alone, its panels in one row with the legend inside, so
# that the figure fits one column at a readable height.
def plot(points: list[GrainPoint], path: Path, sides: Sequence[int] | None = None) -> None:
    series = curves(points)
    panels = sorted({(curve.workload, curve.k, curve.side) for curve in series if sides is None or curve.side in sides})
    if not panels:
        raise ValueError(f"no grain panel for sides {sides}")
    one_row = sides is not None
    columns = len(panels) if one_row else len({side for _, _, side in panels})
    rows = 1 if one_row else len({(workload, k) for workload, k, _ in panels})
    size = (PANEL_WIDTH * columns + (0 if one_row else LEGEND_WIDTH), PANEL_HEIGHT * rows)
    figure, axes = plt.subplots(rows, columns, figsize=size, squeeze=False, layout="constrained")
    for axis, panel in zip(axes.flat, panels):
        for curve, curve_points in series.items():
            if (curve.workload, curve.k, curve.side) == panel:
                draw(axis, curve, curve_points)
        workload, k, side = panel
        axis.set_xscale("log", base=GRAIN_LOG_BASE)
        axis.set_yscale("log")
        axis.yaxis.set_major_formatter(ScalarFormatter())
        axis.yaxis.set_minor_formatter(ScalarFormatter())
        axis.set_title(f"{workload_label(workload, k)}, ${side}^2$", fontsize=TITLE_SIZE)
        axis.set_xlabel(f"grain ({unit_of(workload)} per task)")
    figure.supylabel("time per pass (us, log scale)")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    handles.append(Line2D([], [], color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH))
    labels.append("adaptive split")
    if one_row:
        axes.flat[0].legend(handles, labels, fontsize=LEGEND_SIZE)
    else:
        figure.legend(handles, labels, loc="outside right upper", fontsize=LEGEND_SIZE)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)


def unit_of(workload: str) -> str:
    return Curve("", workload, None, 1, 1).unit


def draw(axis: Axes, curve: Curve, points: list[GrainPoint]) -> None:
    fixed = [point for point in points if point.grain is not None]
    color = COLORS[curve.environment]
    grains = [point.grain for point in fixed if point.grain is not None]
    axis.plot(grains, [p.time_ns / NS_PER_US for p in fixed], marker="o", ms=MARKER_SIZE, color=color, label=curve.environment)
    axis.fill_between(grains, [p.interval.low / NS_PER_US for p in fixed], [p.interval.high / NS_PER_US for p in fixed], color=color, alpha=BAND_ALPHA, lw=0)
    for point in points:
        if point.grain is None:
            axis.axhline(point.time_ns / NS_PER_US, color=color, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)
