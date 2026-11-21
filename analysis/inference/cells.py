import math
from collections.abc import Iterable
from dataclasses import dataclass

from analysis.configuration import Configuration, Environment, Workload
from analysis.inference.groups import Pair, Quad
from analysis.inference.question import Question
from analysis.runs import RunSummary

LogGroups = dict[Configuration, list[float]]
Wanted = Pair[Configuration] | Quad[Configuration]


@dataclass(frozen=True)
class Cells:
    question: Question
    configuration: Configuration
    groups: Pair[list[float]] | Quad[list[float]]


def log_groups(runs: Iterable[RunSummary]) -> LogGroups:
    groups: LogGroups = {}
    for run in runs:
        groups.setdefault(run.configuration, []).append(math.log(run.value))
    return groups


def cells_if_complete(
    question: Question, configuration: Configuration, wanted: Wanted, groups: LogGroups
) -> Cells | None:
    if not all(cell in groups for cell in wanted):
        return None
    values = [groups[cell] for cell in wanted]
    return Cells(question, configuration, Pair(*values) if isinstance(wanted, Pair) else Quad(*values))


# r = log T(atomic) - log T(local) within one environment, and RQ2 compares r between the
# browser and native at the same input, k and N: interaction() gives r(browser) - r(native) = Δr.
def rq2_wanted(browser_atomic: Configuration) -> Quad[Configuration]:
    native_atomic = browser_atomic.in_environment(Environment.NATIVE)
    return Quad(
        browser_numerator=browser_atomic,
        browser_denominator=browser_atomic.as_workload(Workload.HIST_LOCAL),
        native_numerator=native_atomic,
        native_denominator=native_atomic.as_workload(Workload.HIST_LOCAL),
    )


# The log speedup log T1 - log TN of the browser minus the same of native.
def rq1_wanted(browser: Configuration) -> Quad[Configuration]:
    native = browser.in_environment(Environment.NATIVE)
    return Quad(
        browser_numerator=browser.baseline(),
        browser_denominator=browser,
        native_numerator=native.baseline(),
        native_denominator=native,
    )


# Log T(browser, N) - log T(native, N), never relative to a baseline.
def absolute_wanted(browser: Configuration) -> Pair[Configuration]:
    return Pair(numerator=browser, denominator=browser.in_environment(Environment.NATIVE))


def rq2_cells(groups: LogGroups) -> list[Cells]:
    found = (
        cells_if_complete(Question.RQ2, configuration, rq2_wanted(configuration), groups)
        for configuration in sorted(groups)
        if configuration.is_browser and configuration.workload == Workload.HIST_ATOMIC
    )
    return [cells for cells in found if cells is not None]


def rq1_cells(groups: LogGroups) -> list[Cells]:
    found = (
        cells_if_complete(Question.RQ1, configuration, rq1_wanted(configuration), groups)
        for configuration in sorted(groups)
        if configuration.is_browser and configuration.threads != 1
    )
    return [cells for cells in found if cells is not None]


def absolute_cells(groups: LogGroups) -> list[Cells]:
    found = (
        cells_if_complete(Question.ABSOLUTE, configuration, absolute_wanted(configuration), groups)
        for configuration in sorted(groups)
        if configuration.is_browser
    )
    return [cells for cells in found if cells is not None]


def missing_absolute(runs: Iterable[RunSummary], max_threads: int) -> list[Configuration]:
    present = {run.configuration for run in runs}
    return sorted(
        configuration
        for configuration in present
        if configuration.is_browser
        and configuration.threads in (1, max_threads)
        and configuration.in_environment(Environment.NATIVE) not in present
    )
