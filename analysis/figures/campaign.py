from collections.abc import Sequence
from pathlib import Path

from analysis.configuration import workload_label, workload_order
from analysis.figures.panels import finish, grid, plot_lines, reference_level, reference_line
from analysis.figures.points import RatioCurves, Rq2Curves, ScalingCurves
from analysis.figures.style import PANEL_COLUMNS, TITLE_SIZE


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
