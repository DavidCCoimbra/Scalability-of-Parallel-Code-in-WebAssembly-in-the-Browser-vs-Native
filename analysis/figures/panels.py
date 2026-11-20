from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Protocol, TypeVar

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from analysis.configuration import ENVIRONMENTS
from analysis.figures.pyplot import plt
from analysis.figures.style import (
    BAND_ALPHA,
    COLORS,
    LEGEND_SIZE,
    MARKER_SIZE,
    PANEL_COLUMNS,
    PANEL_HEIGHT,
    PANEL_WIDTH,
    REFERENCE_COLOR,
    REFERENCE_STYLE,
    REFERENCE_WIDTH,
)


class HasThreads(Protocol):
    @property
    def threads(self) -> int: ...


Point = TypeVar("Point", bound=HasThreads)


# columns: the grid's width in panels, PANEL_COLUMNS by default so that every figure keeps its
# shape; the paper's two-panel RQ2 figure passes 2, so that scaled to a column it is not squeezed.
def grid(count: int, columns: int = PANEL_COLUMNS) -> tuple[Figure, list[Axes]]:
    rows = -(-count // columns)
    figure, axes = plt.subplots(
        rows, columns, figsize=(PANEL_WIDTH * columns, PANEL_HEIGHT * rows), sharex=True, squeeze=False
    )
    panels = list(axes.flat)
    for axis in panels[count:]:
        axis.set_visible(False)
    return figure, panels[:count]


def reference_line(axis: Axes, xs: Sequence[float], ys: Sequence[float]) -> None:
    axis.plot(xs, ys, color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)


def reference_level(axis: Axes, level: float) -> None:
    axis.axhline(level, color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)


def plot_lines(
    axis: Axes,
    series: Mapping[str, Sequence[Point]],
    value: Callable[[Point], float],
    low: Callable[[Point], float],
    high: Callable[[Point], float],
) -> None:
    for environment in ENVIRONMENTS:
        points = sorted(series.get(environment, []), key=lambda point: point.threads)
        if not points:
            continue
        xs = [point.threads for point in points]
        color = COLORS[environment]
        axis.plot(xs, [value(point) for point in points], marker="o", ms=MARKER_SIZE, color=color, label=environment)
        axis.fill_between(xs, [low(point) for point in points], [high(point) for point in points], color=color, alpha=BAND_ALPHA)
        axis.set_xticks(sorted({point.threads for points in series.values() for point in points}))


def finish(figure: Figure, axes: list[Axes], title: str, ylabel: str, path: Path) -> None:
    axes[0].legend(fontsize=LEGEND_SIZE)
    figure.supxlabel("threads N")
    figure.supylabel(ylabel)
    figure.suptitle(title)
    figure.tight_layout()
    figure.savefig(path)
    plt.close(figure)
