from collections.abc import Sequence
from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.colors import to_rgba

from analysis.figures.pyplot import plt
from analysis.figures.spread import DistributionPanel, Spread
from analysis.figures.style import COLORS

FIGURE_SIZE = (3.4, 1.75)
FONT_SIZE = 6
VIOLIN_ALPHA = 0.35
VIOLIN_WIDTH = 0.8
BOX_WIDTH = 3.5
MEDIAN_SIZE = 9
POINT_SIZE = 1.5
POINT_OFFSET = 0.3
POINT_COLOR = "black"
MEDIAN_COLOR = "white"
LABELS = {"native": "nat", "chrome": "Chr", "firefox": "FF"}
TICK_SIZE = 5.5


def draw_spread(axis: Axes, position: int, spread: Spread) -> None:
    color = COLORS[spread.environment]
    fill = to_rgba(color, VIOLIN_ALPHA)
    axis.violinplot([spread.milliseconds], [position], widths=VIOLIN_WIDTH, showextrema=False, facecolor=fill, linecolor=color)
    low, median, high = spread.quartiles
    axis.vlines(position, low, high, color=color, lw=BOX_WIDTH)
    axis.scatter([position], [median], s=MEDIAN_SIZE, color=MEDIAN_COLOR, edgecolors=color, zorder=3)
    xs = [position + POINT_OFFSET] * len(spread.milliseconds)
    axis.scatter(xs, spread.milliseconds, s=POINT_SIZE, color=POINT_COLOR, linewidths=0, zorder=3)


def draw_panel(axis: Axes, title: str, spreads: Sequence[Spread]) -> None:
    for position, spread in enumerate(spreads):
        draw_spread(axis, position, spread)
    axis.set_xticks(range(len(spreads)), [LABELS.get(s.environment, s.environment) for s in spreads])
    axis.set_title(title, fontsize=FONT_SIZE)
    axis.tick_params(axis="y", labelsize=FONT_SIZE, pad=1)
    axis.tick_params(axis="x", labelsize=TICK_SIZE, pad=1, length=0)


def distributions_figure(panels: Sequence[tuple[DistributionPanel, list[Spread]]], path: Path) -> None:
    figure, axes = plt.subplots(1, len(panels), figsize=FIGURE_SIZE)
    for axis, (panel, spreads) in zip(axes.flat, panels):
        draw_panel(axis, panel.title, spreads)
    figure.supylabel("run value (ms)", fontsize=FONT_SIZE)
    figure.tight_layout(pad=0.2, w_pad=0.3)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)
