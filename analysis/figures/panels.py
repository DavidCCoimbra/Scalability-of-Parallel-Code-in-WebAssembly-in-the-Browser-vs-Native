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
    DEFAULT_LINE,
    DEFAULT_MARKER,
    LEGEND_COLUMN_SPACING,
    LEGEND_HANDLE_LENGTH,
    LEGEND_SIZE,
    MARKER_SIZE,
    PANEL_COLUMNS,
    PANEL_HEIGHT,
    PANEL_WIDTH,
    REFERENCE_COLOR,
    REFERENCE_STYLE,
    REFERENCE_WIDTH,
    SHARED_LEGEND_TOP,
)


class HasThreads(Protocol):
    @property
    def threads(self) -> int: ...


Point = TypeVar("Point", bound=HasThreads)


# columns: the grid's width in panels, PANEL_COLUMNS by default so that every figure keeps its
# shape; the paper's two-panel RQ2 figure passes 2, so that scaled to a column it is not squeezed.
# size: the whole figure in inches, for the figures drawn at their printed size; share_y gives
# their panels one scale, so that levels compare across panels.
def grid(
    count: int, columns: int = PANEL_COLUMNS, size: tuple[float, float] | None = None, share_y: bool = False
) -> tuple[Figure, list[Axes]]:
    rows = -(-count // columns)
    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=size or (PANEL_WIDTH * columns, PANEL_HEIGHT * rows),
        sharex=True,
        sharey=share_y,
        squeeze=False,
    )
    panels = list(axes.flat)
    for axis in panels[count:]:
        axis.set_visible(False)
    return figure, panels[:count]


def reference_line(axis: Axes, xs: Sequence[float], ys: Sequence[float]) -> None:
    axis.plot(xs, ys, color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)


def reference_level(axis: Axes, level: float) -> None:
    axis.axhline(level, color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)


# One curve with its band. The marker and the line style tell apart curves that share a colour.
def plot_curve(
    axis: Axes,
    points: Sequence[Point],
    value: Callable[[Point], float],
    low: Callable[[Point], float],
    high: Callable[[Point], float],
    color: str,
    label: str,
    marker: str = DEFAULT_MARKER,
    line: str = DEFAULT_LINE,
) -> None:
    ordered = sorted(points, key=lambda point: point.threads)
    xs = [point.threads for point in ordered]
    axis.plot(xs, [value(point) for point in ordered], marker=marker, ms=MARKER_SIZE, ls=line, color=color, label=label)
    axis.fill_between(xs, [low(point) for point in ordered], [high(point) for point in ordered], color=color, alpha=BAND_ALPHA)


def plot_lines(
    axis: Axes,
    series: Mapping[str, Sequence[Point]],
    value: Callable[[Point], float],
    low: Callable[[Point], float],
    high: Callable[[Point], float],
) -> None:
    for environment in ENVIRONMENTS:
        points = series.get(environment, [])
        if not points:
            continue
        plot_curve(axis, points, value, low, high, COLORS[environment], environment)
        axis.set_xticks(sorted({point.threads for points in series.values() for point in points}))


# title: None for the paper's own figures, whose caption says it. shared_legend_columns: when set,
# one legend above the panels with that many columns, for a figure whose panels have no free
# corner; its line samples are those of the first panel.
def finish(
    figure: Figure,
    axes: list[Axes],
    title: str | None,
    ylabel: str,
    path: Path,
    legend_size: float = LEGEND_SIZE,
    shared_legend_columns: int | None = None,
) -> None:
    figure.supxlabel("threads N")
    figure.supylabel(ylabel)
    if title is not None:
        figure.suptitle(title)
    if shared_legend_columns is None:
        axes[0].legend(fontsize=legend_size)
        figure.tight_layout()
    else:
        handles, labels = axes[0].get_legend_handles_labels()
        figure.legend(
            handles,
            labels,
            loc="upper center",
            ncols=shared_legend_columns,
            fontsize=legend_size,
            frameon=False,
            handlelength=LEGEND_HANDLE_LENGTH,
            columnspacing=LEGEND_COLUMN_SPACING,
        )
        figure.tight_layout(rect=(0, 0, 1, SHARED_LEGEND_TOP))
    figure.savefig(path)
    plt.close(figure)
