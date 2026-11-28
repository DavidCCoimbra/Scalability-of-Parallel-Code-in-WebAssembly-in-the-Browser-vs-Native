from collections.abc import Sequence
from pathlib import Path

from matplotlib.ticker import FixedLocator, NullFormatter, ScalarFormatter

from analysis.configuration import BROWSERS, Workload, workload_label, workload_order
from analysis.figures.panels import finish, grid, plot_curve, plot_lines, reference_level, reference_line
from analysis.figures.points import RatioCurves, Rq2Curves, Rq2EffectCurves, ScalingCurves, WorkloadKey
from analysis.figures.pyplot import plt
from analysis.figures.style import (
    COLORS,
    DEFAULT_LINE,
    DEFAULT_MARKER,
    K_LINES,
    K_MARKERS,
    PANEL_COLUMNS,
    PAPER_COLUMN_SIZE,
    PAPER_FONT_SIZE,
    PAPER_LEGEND_SIZE,
    PAPER_ROW_SIZE,
    TITLE_SIZE,
)

# The panels of the paper's RQ1 figure: the workload without synchronization, and the local
# histogram where its efficiency dips at N = 6 and 7 (k = 16) and where it passes 1 (k = 256).
PAPER_EFFICIENCY_PANELS: tuple[tuple[WorkloadKey, str], ...] = (
    ((Workload.FILTER, None), "Gaussian filter"),
    ((Workload.HIST_LOCAL, 16), "Local histogram, k = 16"),
    ((Workload.HIST_LOCAL, 256), "Local histogram, k = 256"),
)
# Ticks of the log axis of the RQ2 effect, which runs from about 0.3 to 2.5.
RQ2_EFFECT_TICKS = (0.4, 0.6, 1.0, 1.5, 2.0)


def speedup_figure(curves: ScalingCurves, diagonal: str, path: Path) -> None:
    keys = sorted(curves, key=workload_order)
    figure, axes = grid(len(keys))
    for axis, key in zip(axes, keys):
        top = max(point.threads for points in curves[key].values() for point in points)
        reference_line(axis, [1, top], [1, top])
        plot_lines(axis, curves[key], lambda p: p.speedup, lambda p: p.low, lambda p: p.high)
        axis.set_title(workload_label(*key), fontsize=TITLE_SIZE)
    finish(figure, axes, f"Relative speedup T1 / TN (dashed: {diagonal})", "speedup", path)


def efficiency_figure(curves: ScalingCurves, path: Path) -> None:
    keys = sorted(curves, key=workload_order)
    figure, axes = grid(len(keys))
    for axis, key in zip(axes, keys):
        reference_level(axis, 1)
        plot_lines(axis, curves[key], lambda p: p.efficiency, lambda p: p.low / p.threads, lambda p: p.high / p.threads)
        axis.set_title(workload_label(*key), fontsize=TITLE_SIZE)
    finish(figure, axes, "Efficiency speedup / N", "efficiency", path)


def absolute_figure(ratios: RatioCurves, path: Path) -> None:
    keys = sorted(ratios, key=workload_order)
    if not keys:
        return
    figure, axes = grid(len(keys))
    for axis, key in zip(axes, keys):
        reference_level(axis, 1)
        plot_lines(axis, ratios[key], lambda p: p.value, lambda p: p.low, lambda p: p.high)
        axis.set_title(workload_label(*key), fontsize=TITLE_SIZE)
    finish(figure, axes, "Absolute time, browser / native", "time ratio", path)


def k_order(k: int | None) -> int:
    return k or 0


# ks: the k panels to draw, every k by default. The paper draws only the two ends of the sweep
# (k = 1 and 256), whose shapes differ; the middle k are in its table.
def rq2_figure(ratios: Rq2Curves, path: Path, ks: Sequence[int | None] | None = None) -> None:
    if not ratios:
        return
    chosen = sorted(ratios, key=k_order) if ks is None else [k for k in sorted(ratios, key=k_order) if k in ks]
    if not chosen:
        return
    figure, axes = grid(len(chosen), columns=len(chosen) if ks is not None else PANEL_COLUMNS)
    for axis, k in zip(axes, chosen):
        reference_level(axis, 1)
        plot_lines(axis, ratios[k], lambda p: p.value, lambda p: p.low, lambda p: p.high)
        axis.set_yscale("log")
        axis.set_title(f"k = {k}", fontsize=TITLE_SIZE)
    finish(figure, axes, "RQ2: T(atomic) / T(local) per environment", "time ratio (log)", path)


# The paper's RQ1 figure: efficiency against N on one scale, drawn at its printed size. On a
# speedup axis from 1 to 8 the differences that RQ1 is about (a few percent) cannot be seen.
def paper_efficiency_figure(curves: ScalingCurves, path: Path) -> None:
    panels = [(key, title) for key, title in PAPER_EFFICIENCY_PANELS if key in curves]
    if not panels:
        return
    with plt.rc_context({"font.size": PAPER_FONT_SIZE}):
        figure, axes = grid(len(panels), columns=len(panels), size=PAPER_ROW_SIZE, share_y=True)
        for axis, (key, title) in zip(axes, panels):
            reference_level(axis, 1)
            plot_lines(axis, curves[key], lambda p: p.efficiency, lambda p: p.low / p.threads, lambda p: p.high / p.threads)
            axis.set_title(title, fontsize=PAPER_FONT_SIZE)
        finish(figure, axes, None, "efficiency S / N", path, PAPER_LEGEND_SIZE)


# The paper's RQ2 figure: exp(Δr) against N, one panel per browser and one line per k. The value
# at N = 1 is there before any thread contends; the slope from it is what the threads add.
def rq2_effect_figure(effects: Rq2EffectCurves, path: Path) -> None:
    browsers = [browser for browser in BROWSERS if browser in effects]
    if not browsers:
        return
    with plt.rc_context({"font.size": PAPER_FONT_SIZE}):
        figure, axes = grid(len(browsers), columns=len(browsers), size=PAPER_COLUMN_SIZE, share_y=True)
        for axis, browser in zip(axes, browsers):
            reference_level(axis, 1)
            for k in sorted(effects[browser], key=k_order):
                plot_curve(
                    axis,
                    effects[browser][k],
                    lambda p: p.value,
                    lambda p: p.low,
                    lambda p: p.high,
                    COLORS[browser],
                    f"k = {k}",
                    K_MARKERS.get(k, DEFAULT_MARKER),
                    K_LINES.get(k, DEFAULT_LINE),
                )
            axis.set_xticks(sorted({point.threads for points in effects[browser].values() for point in points}))
            axis.set_yscale("log")
            axis.yaxis.set_major_locator(FixedLocator(RQ2_EFFECT_TICKS))
            axis.yaxis.set_major_formatter(ScalarFormatter())
            axis.yaxis.set_minor_formatter(NullFormatter())
            axis.set_title(browser.capitalize(), fontsize=PAPER_FONT_SIZE)
        finish(figure, axes, None, "effect (log)", path, PAPER_LEGEND_SIZE, shared_legend_columns=len(K_LINES))
