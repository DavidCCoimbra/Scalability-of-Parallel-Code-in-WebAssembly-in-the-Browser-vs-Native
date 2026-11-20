import csv
from typing import TextIO

from analysis.configuration import CsvCell
from analysis.inference.contrast import Contrast
from analysis.inference.robustness import RobustnessCheck
from analysis.inference.shape import ShapeRow
from analysis.scaling.output import CONFIGURATION_COLUMNS
from analysis.stats.bootstrap import Interval

CONTRAST_COLUMNS = (
    "question",
    *CONFIGURATION_COLUMNS,
    "effect",
    "low",
    "high",
    "primary",
    "primary_low",
    "primary_high",
    "p",
    "holm_p",
    "rejected",
)
ROBUSTNESS_COLUMNS = (
    "question",
    *CONFIGURATION_COLUMNS,
    "browser_runs",
    "native_runs",
    "browser_median_ratio",
    "native_median_ratio",
    "cliffs_delta",
    "u",
    "z",
    "p",
    "holm_p",
    "rejected",
    "same_decision_share",
    "bootstrap_effect",
    "bootstrap_holm_p",
    "bootstrap_rejected",
    "agree",
)
SHAPE_COLUMNS = (*CONFIGURATION_COLUMNS, "runs", "skewness", "log_skewness")
SIGNIFICANT_DIGITS = 4
NO_INTERVAL = (None, None)


def optional(value: float | None) -> str:
    return "" if value is None else f"{value:.{SIGNIFICANT_DIGITS}g}"


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def contrast_cells(contrast: Contrast) -> list[CsvCell]:
    primary_low, primary_high = contrast.primary_interval or NO_INTERVAL
    interval: Interval = contrast.interval
    return [
        contrast.question,
        *contrast.configuration.cells(),
        optional(contrast.effect),
        optional(interval.low),
        optional(interval.high),
        "yes" if contrast.primary else "exploratory",
        optional(primary_low),
        optional(primary_high),
        optional(contrast.p),
        optional(contrast.holm_p),
        "" if contrast.rejected is None else yes_no(contrast.rejected),
    ]


def write_contrasts(results: list[Contrast], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(CONTRAST_COLUMNS)
    for contrast in results:
        writer.writerow(contrast_cells(contrast))


def write_shape(rows: list[ShapeRow], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(SHAPE_COLUMNS)
    for row in rows:
        writer.writerow(row.cells())


def robustness_cells(check: RobustnessCheck) -> list[CsvCell]:
    contrast = check.contrast
    return [
        contrast.question,
        *contrast.configuration.cells(),
        len(check.browser),
        len(check.native),
        optional(check.browser_median),
        optional(check.native_median),
        optional(check.cliffs_delta),
        optional(check.test.u),
        optional(check.test.z),
        optional(check.test.p),
        optional(check.holm_p),
        "" if check.rejected is None else yes_no(check.rejected),
        optional(check.same_decision_share),
        optional(contrast.effect),
        optional(contrast.holm_p),
        "" if contrast.rejected is None else yes_no(contrast.rejected),
        yes_no(check.agrees),
    ]


def write_robustness(checks: list[RobustnessCheck], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(ROBUSTNESS_COLUMNS)
    for check in checks:
        writer.writerow(robustness_cells(check))
