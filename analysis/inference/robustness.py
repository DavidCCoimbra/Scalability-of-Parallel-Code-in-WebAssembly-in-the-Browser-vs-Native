import math
import random
import re
import statistics
from collections.abc import Iterable
from dataclasses import dataclass, replace

from analysis.configuration import Configuration
from analysis.inference.cells import rq1_wanted, rq2_wanted
from analysis.inference.contrast import Contrast
from analysis.inference.estimation import DEFAULT_MAX_THREADS, contrasts
from analysis.inference.family import FAMILY_ALPHA
from analysis.inference.groups import Quad
from analysis.inference.question import Question
from analysis.runs import RunSummary
from analysis.stats.bootstrap import BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED
from analysis.stats.cliff import cliffs_delta
from analysis.stats.holm import holm_adjusted
from analysis.stats.mann_whitney import MannWhitney, mann_whitney_u

REPETITION = re.compile(r"-r(\d+)$")
REPAIRINGS = 1_000

LogByRepetition = dict[Configuration, dict[int, float]]


def repetition_of(run: str) -> int:
    match = REPETITION.search(run)
    if match is None:
        raise ValueError(f"run id without a repetition index: {run!r}")
    return int(match.group(1))


def log_by_repetition(runs: Iterable[RunSummary]) -> LogByRepetition:
    values: LogByRepetition = {}
    for run in runs:
        values.setdefault(run.configuration, {})[repetition_of(run.run)] = math.log(run.value)
    return values


# The campaign order is one full shuffle, so repetition r of two configurations shares no
# block or moment: pairing by r only turns two independent groups into one log ratio per run, as a
# fixed pairing chosen before looking at the values. Unmatched repetitions are left out.
def paired_log_ratios(values: LogByRepetition, numerator: Configuration, denominator: Configuration) -> list[float]:
    top, bottom = values.get(numerator, {}), values.get(denominator, {})
    return [top[repetition] - bottom[repetition] for repetition in sorted(top.keys() & bottom.keys())]


@dataclass(frozen=True)
class RobustnessCheck:
    contrast: Contrast
    browser: list[float]
    native: list[float]
    test: MannWhitney
    cliffs_delta: float
    holm_p: float | None = None
    rejected: bool | None = None
    same_decision_share: float | None = None

    @property
    def browser_median(self) -> float:
        return math.exp(statistics.median(self.browser))

    @property
    def native_median(self) -> float:
        return math.exp(statistics.median(self.native))

    # Same decision and, when both reject, the same direction: a browser effect above 1 shows as a
    # positive Cliff's delta here (the browser's per-run ratios dominate).
    @property
    def agrees(self) -> bool:
        if self.rejected != self.contrast.rejected:
            return False
        if not self.rejected:
            return True
        return (self.contrast.estimate > 0) == (self.cliffs_delta > 0)


def wanted(contrast: Contrast) -> Quad[Configuration]:
    if contrast.question is Question.RQ2:
        return rq2_wanted(contrast.configuration)
    if contrast.question is Question.RQ1:
        return rq1_wanted(contrast.configuration)
    raise ValueError(f"no per-run ratio for {contrast.question} contrasts")


# RQ2: log(atomic / local) per run; RQ1: log(T1 / TN), the log speedup, per run.
def check(contrast: Contrast, values: LogByRepetition) -> RobustnessCheck:
    cells = wanted(contrast)
    browser = paired_log_ratios(values, cells.browser_numerator, cells.browser_denominator)
    native = paired_log_ratios(values, cells.native_numerator, cells.native_denominator)
    return RobustnessCheck(contrast, browser, native, mann_whitney_u(native, browser), cliffs_delta(native, browser))


def holm_decisions(p_values: list[float]) -> list[bool]:
    return [p <= FAMILY_ALPHA for p in holm_adjusted(p_values)]


def with_holm(checks: list[RobustnessCheck]) -> list[RobustnessCheck]:
    adjusted = holm_adjusted([check.test.p for check in checks])
    return [replace(check, holm_p=p, rejected=p <= FAMILY_ALPHA) for check, p in zip(checks, adjusted)]


def shuffled_log_ratios(
    values: LogByRepetition, numerator: Configuration, denominator: Configuration, rng: random.Random
) -> list[float]:
    first, second = values.get(numerator, {}), values.get(denominator, {})
    repetitions = sorted(first.keys() & second.keys())
    bottom = [second[repetition] for repetition in repetitions]
    rng.shuffle(bottom)
    return [first[repetition] - b for repetition, b in zip(repetitions, bottom)]


# The fixed pairing by repetition is one of many equally valid ones, so the whole family is redone
# under random pairings: the share of them that reproduce each Holm decision shows whether the
# decision depends on which runs were paired.
def repairing_shares(
    checks: list[RobustnessCheck], values: LogByRepetition, repairings: int, seed: int
) -> list[RobustnessCheck]:
    rng = random.Random(seed)
    same = [0] * len(checks)
    for _ in range(repairings):
        p_values = []
        for item in checks:
            cells = wanted(item.contrast)
            browser = shuffled_log_ratios(values, cells.browser_numerator, cells.browser_denominator, rng)
            native = shuffled_log_ratios(values, cells.native_numerator, cells.native_denominator, rng)
            p_values.append(mann_whitney_u(native, browser).p)
        for index, decision in enumerate(holm_decisions(p_values)):
            same[index] += decision == checks[index].rejected
    return [replace(item, same_decision_share=count / repairings) for item, count in zip(checks, same)]


def robustness_checks(
    runs: list[RunSummary],
    max_threads: int = DEFAULT_MAX_THREADS,
    resamples: int = BOOTSTRAP_RESAMPLES,
    repairings: int = REPAIRINGS,
    seed: int = BOOTSTRAP_SEED,
) -> list[RobustnessCheck]:
    primary = [contrast for contrast in contrasts(runs, max_threads=max_threads, resamples=resamples) if contrast.primary]
    values = log_by_repetition(runs)
    checks = with_holm([check(contrast, values) for contrast in primary])
    return repairing_shares(checks, values, repairings, seed)
