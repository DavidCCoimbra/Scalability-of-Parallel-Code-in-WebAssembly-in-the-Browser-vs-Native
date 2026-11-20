import statistics
from collections import defaultdict
from pathlib import Path

from matplotlib.axes import Axes

from analysis.configuration import workload_label, workload_order
from analysis.figures.pyplot import plt
from analysis.figures.panels import grid
from analysis.figures.style import COLORS, REFERENCE_COLOR, REFERENCE_STYLE, REFERENCE_WIDTH, TITLE_SIZE
from analysis.pilot.warmup import Series, WarmupRule, WorkloadKey, campaign_warmups

LINE_WIDTH = 0.8
LINE_ALPHA = 0.8
SHADE_ALPHA = 0.12
Y_LIMITS = (0.8, 1.6)
BAND = WarmupRule().band


def normalised(times: list[float]) -> list[float]:
    reference = statistics.median(times[len(times) // 2 :])
    return [time / reference for time in times]


def warmup_panel(axis: Axes, runs: list[Series], key: WorkloadKey, warmup: int) -> None:
    for run in runs:
        if run.workload_key == key:
            axis.plot(normalised(run.times), color=COLORS[run.environment], lw=LINE_WIDTH, alpha=LINE_ALPHA, label=run.environment)
    axis.axvline(warmup, color=REFERENCE_COLOR, ls=REFERENCE_STYLE, lw=REFERENCE_WIDTH)
    axis.axhspan(1 - BAND, 1 + BAND, color=REFERENCE_COLOR, alpha=SHADE_ALPHA)
    axis.set_ylim(*Y_LIMITS)
    axis.set_title(f"{workload_label(*key)} (W = {warmup})", fontsize=TITLE_SIZE)


def warmup_figure(threads: int, runs: list[Series], warmups: dict[WorkloadKey, int], output: Path) -> None:
    workloads = sorted(warmups, key=workload_order)
    figure, axes = grid(len(workloads))
    for axis, key in zip(axes, workloads):
        warmup_panel(axis, runs, key, warmups[key])
    handles, labels = axes[0].get_legend_handles_labels()
    # Every run draws its own line, so the figure legend keeps one entry per environment.
    unique = dict(zip(labels, handles))
    figure.legend(list(unique.values()), list(unique.keys()), loc="upper right")
    figure.supxlabel("iteration")
    figure.supylabel("time / median of the second half")
    figure.suptitle(f"N = {threads}: dashed line W, shaded band ±{100 * BAND:.0f} %")
    figure.tight_layout()
    figure.savefig(output / f"warmup-n{threads}.pdf")
    plt.close(figure)


def warmup_figures(series: list[Series], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    warmups = campaign_warmups(series, WarmupRule())
    by_threads: defaultdict[int, list[Series]] = defaultdict(list)
    for run in series:
        by_threads[run.threads].append(run)
    for threads, runs in sorted(by_threads.items()):
        warmup_figure(threads, runs, warmups, output)
