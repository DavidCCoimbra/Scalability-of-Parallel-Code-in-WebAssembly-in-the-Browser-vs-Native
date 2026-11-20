from pathlib import Path

from analysis.configuration import workload_label
from analysis.figures.pyplot import plt
from analysis.figures.style import (
    COLORS,
    LEGEND_SIZE,
    MARKER_SIZE,
    PANEL_WIDTH,
    REFERENCE_COLOR,
    REFERENCE_STYLE,
    REFERENCE_WIDTH,
    TITLE_SIZE,
)
from analysis.scaling.crossing import BREAK_EVEN_SPEEDUP
from analysis.scaling.cutoff import CUTOFF_WORKLOADS, CutoffPoint, curves

THREAD_STYLES = {2: ":", 4: "--", 8: "-"}
SIDE_LOG_BASE = 2
FIGURE_HEIGHT = 3.5
LEGEND_WIDTH = 1.6


def plot(points: list[CutoffPoint], path: Path) -> None:
    size = (PANEL_WIDTH * len(CUTOFF_WORKLOADS) + LEGEND_WIDTH, FIGURE_HEIGHT)
    figure, axes = plt.subplots(1, len(CUTOFF_WORKLOADS), figsize=size, sharey=True, layout="constrained")
    series = curves(points)
    sides = sorted({point.side for point in points})
    for axis, (workload, k) in zip(axes, CUTOFF_WORKLOADS):
        for (environment, curve_workload, _, curve_k, threads), curve in series.items():
            if (curve_workload, curve_k) != (workload, k) or threads not in THREAD_STYLES:
                continue
            axis.plot(
                [point.side for point in curve],
                [point.speedup for point in curve],
                ls=THREAD_STYLES[threads],
                marker="o",
                ms=MARKER_SIZE,
                color=COLORS[environment],
                label=f"{environment} N={threads}",
            )
        axis.axhline(BREAK_EVEN_SPEEDUP, color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)
        axis.set_xscale("log", base=SIDE_LOG_BASE)
        axis.set_xticks(sides, [str(side) for side in sides])
        axis.minorticks_off()
        axis.set_title(workload_label(workload, k), fontsize=TITLE_SIZE)
    figure.supxlabel("image side (pixels, log scale)")
    figure.supylabel("speedup T1 / TN (same size)")
    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside right upper", fontsize=LEGEND_SIZE)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)
