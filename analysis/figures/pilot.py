from dataclasses import dataclass
from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from analysis.configuration import Environment, Workload
from analysis.figures.panels import plot_lines
from analysis.figures.points import RatioCurves, ScalingCurves, WorkloadKey
from analysis.figures.pyplot import plt
from analysis.figures.style import COLORS, MARKER_SIZE, REFERENCE_STYLE, REFERENCE_WIDTH, REFERENCE_COLOR, THREADS

SPEEDUP = "speedup"
ABSOLUTE = "absolute"
# Row 1 is RQ1 (the filter: speedup, then browser / native time). Rows 2 and 3 are the RQ2 grid of
# the proposal: columns without and with synchronization (local, atomic), rows high and low
# contention (k = 1, k = 256).
PANELS: tuple[tuple[str, WorkloadKey], ...] = (
    (SPEEDUP, (Workload.FILTER, None)),
    (ABSOLUTE, (Workload.FILTER, None)),
    (SPEEDUP, (Workload.HIST_LOCAL, 1)),
    (SPEEDUP, (Workload.HIST_ATOMIC, 1)),
    (SPEEDUP, (Workload.HIST_LOCAL, 256)),
    (SPEEDUP, (Workload.HIST_ATOMIC, 256)),
)
FIGURE_SIZE = (4.2, 4.4)
LARGEST_N = THREADS[-1]
SPEEDUP_LIMITS = (0, 8.5)
SPEEDUP_TICKS = [0, 2, 4, 6, 8]
# The atomic speedups stay between 0.3 and 2: on the 0 to 8 axis they would sit flat at the
# bottom, so their panels get their own axis and a "no gain" line at 1 instead of the diagonal.
ATOMIC_LIMITS = (0, 2.5)
ATOMIC_TICKS = [0, 1, 2]
NO_GAIN = 1
# Native is drawn first; where the browsers match it, a wide pale line keeps it visible.
HALO_WIDTH = 4
HALO_ALPHA = 0.35
SMALL_TEXT = 7
TITLE_TEXT = 8
TITLE_PAD = 2
ROW_PAD = 0.4
# Panel letters, row by row, so the report can point at one panel: "(Fig. 1c)".
PANEL_LETTERS = "abcdef"


@dataclass(frozen=True)
class Labels:
    suffix: str
    workloads: dict[str, str]
    native: str
    ratio: str
    rows: tuple[str, str, str]


PORTUGUESE = Labels(
    "",
    {"filter": "filtro", "hist-local": "sem sync: local", "hist-atomic": "sync: atómico"},
    "nativo",
    "tempo browser / nativo",
    ("RQ1\nfiltro", "RQ2, k = 1\nmuita disputa", "RQ2, k = 256\npouca disputa"),
)
ENGLISH = Labels(
    "-en",
    {"filter": "filter", "hist-local": "no sync: local", "hist-atomic": "sync: atomic"},
    "native",
    "time browser / native",
    ("RQ1\nfilter", "RQ2, k = 1\nhigh contention", "RQ2, k = 256\nlow contention"),
)
# Room on the left of the figure for the row labels, and where they sit.
ROW_LABEL_MARGIN = 0.07
ROW_LABEL_X = 0.012


def title(key: WorkloadKey, labels: Labels, letter: str) -> str:
    workload, k = key
    # The rows already name k, so the title names only the workload.
    return f"({letter}) " + labels.workloads[workload]


def legend(axis: Axes, labels: Labels) -> None:
    names = ((Environment.NATIVE, labels.native), (Environment.CHROME, "Chrome"), (Environment.FIREFOX, "Firefox"))
    handles = [Line2D([], [], color=COLORS[name], marker="o", ms=MARKER_SIZE, label=label) for name, label in names]
    axis.legend(handles=handles, fontsize=SMALL_TEXT, loc="upper left")


def style(axis: Axes, key: WorkloadKey, labels: Labels, letter: str) -> None:
    axis.set_title(title(key, labels, letter), fontsize=TITLE_TEXT, pad=TITLE_PAD)
    axis.set_xticks(THREADS)
    axis.tick_params(labelsize=SMALL_TEXT)


def native_halo(axis: Axes, points: list[tuple[int, float]]) -> None:
    xs, ys = [n for n, _ in points], [y for _, y in points]
    axis.plot(xs, ys, color=COLORS[Environment.NATIVE], lw=HALO_WIDTH, alpha=HALO_ALPHA, zorder=1)


def speedup_panel(axis: Axes, curves: ScalingCurves, key: WorkloadKey, labels: Labels, letter: str) -> None:
    atomic = key[0] == Workload.HIST_ATOMIC
    if atomic:
        axis.axhline(NO_GAIN, color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)
    else:
        axis.plot([1, LARGEST_N], [1, LARGEST_N], color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)
    native = sorted(curves[key].get(Environment.NATIVE, []), key=lambda p: p.threads)
    native_halo(axis, [(p.threads, p.speedup) for p in native])
    plot_lines(axis, curves[key], lambda p: p.speedup, lambda p: p.low, lambda p: p.high)
    axis.set_ylim(*(ATOMIC_LIMITS if atomic else SPEEDUP_LIMITS))
    axis.set_yticks(ATOMIC_TICKS if atomic else SPEEDUP_TICKS)
    axis.set_ylabel("speedup", fontsize=SMALL_TEXT)
    style(axis, key, labels, letter)


def absolute_panel(axis: Axes, ratios: RatioCurves, key: WorkloadKey, labels: Labels, letter: str) -> None:
    axis.axhline(1, color=COLORS[Environment.NATIVE], ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)
    # The dashed line is native's own time (native / native = 1), not a measured curve.
    axis.text(LARGEST_N, 1, f"{labels.native} = 1", color=COLORS[Environment.NATIVE], fontsize=SMALL_TEXT, ha="right", va="bottom")
    plot_lines(axis, ratios[key], lambda p: p.value, lambda p: p.low, lambda p: p.high)
    axis.set_ylabel(labels.ratio, fontsize=SMALL_TEXT)
    style(axis, key, labels, letter)


def pilot_figure(curves: ScalingCurves, ratios: RatioCurves, labels: Labels, output: Path) -> None:
    figure, axes = plt.subplots(3, 2, figsize=FIGURE_SIZE, sharex=True)
    for axis, (kind, key), letter in zip(axes.flat, PANELS, PANEL_LETTERS):
        if kind == SPEEDUP:
            speedup_panel(axis, curves, key, labels, letter)
        else:
            absolute_panel(axis, ratios, key, labels, letter)
    legend(axes[0][0], labels)
    figure.supxlabel("threads N", fontsize=TITLE_TEXT)
    figure.tight_layout(h_pad=ROW_PAD, rect=(ROW_LABEL_MARGIN, 0, 1, 1))
    for row, text in zip(axes, labels.rows):
        box = row[0].get_position()
        figure.text(ROW_LABEL_X, (box.y0 + box.y1) / 2, text, rotation=90, va="center", ha="left", ma="center", fontsize=SMALL_TEXT, fontweight="bold")
    figure.savefig(output / f"pilot-scaling{labels.suffix}.pdf")
    plt.close(figure)
