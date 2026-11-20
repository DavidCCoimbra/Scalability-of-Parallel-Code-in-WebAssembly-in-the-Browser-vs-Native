# Extra, not part of RQ1 or RQ2: the SIMD build variants (scalar, AVX2) of the filter.

from pathlib import Path

from analysis.configuration import ENVIRONMENTS
from analysis.figures.pyplot import plt
from analysis.figures.style import COLORS, LEGEND_SIZE, MARKER_SIZE, THREADS, TITLE_SIZE
from analysis.scaling.build_variants import VariantPoint

STYLES = {"baseline": "-", "scalar": ":", "avx2": "--"}
FIGURE_SIZE = (12, 3.2)
VARIANT_BAND_ALPHA = 0.15


def build_series(points: list[VariantPoint], build: str, environment: str) -> list[VariantPoint]:
    return sorted((p for p in points if p.build == build and p.environment == environment), key=lambda p: p.threads)


def plot(points: list[VariantPoint], path: Path) -> None:
    figure, axes = plt.subplots(1, len(ENVIRONMENTS), figsize=FIGURE_SIZE, sharey=True)
    for axis, environment in zip(axes, ENVIRONMENTS):
        color = COLORS[environment]
        for build, style in STYLES.items():
            series = build_series(points, build, environment)
            if not series:
                continue
            xs = [p.threads for p in series]
            axis.plot(xs, [p.efficiency for p in series], ls=style, marker="o", ms=MARKER_SIZE, color=color, label=build)
            lows = [p.efficiency_interval.low for p in series]
            highs = [p.efficiency_interval.high for p in series]
            axis.fill_between(xs, lows, highs, color=color, alpha=VARIANT_BAND_ALPHA)
        axis.set_title(environment, fontsize=TITLE_SIZE)
        axis.set_xticks(THREADS)
        axis.legend(fontsize=LEGEND_SIZE)
    figure.supxlabel("threads N")
    figure.supylabel("efficiency")
    figure.suptitle("Filter efficiency per build")
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)
