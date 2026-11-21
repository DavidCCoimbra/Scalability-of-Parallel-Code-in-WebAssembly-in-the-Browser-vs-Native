"""The gate before a build's campaigns: whether a few runs at the real size are fit to start from."""

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

from analysis.configuration import Workload
from analysis.inference.exclusion import Reason
from analysis.loading import ExclusionRule, InvalidCampaign, load_campaign
from analysis.quality.clock import CLOCK_FACTOR
from analysis.quality.iteration_drift import DEFAULT_WINDOW, drift_of, measured_series
from analysis.run_context import run_context
from analysis.runs import MEASURED
from harness.collect import Row

# How far the median of the first measured iterations may be from the median of the last ones.
DRIFT_TOLERANCE = 0.05
# The workloads that must give one output for one input: each sequential reference and the
# parallel workloads it stands for.
SAME_OUTPUT = (
    (Workload.FILTER_SEQ, Workload.FILTER),
    (Workload.HIST_SEQ, Workload.HIST_LOCAL, Workload.HIST_ATOMIC),
)


# The strict rule is the one of the campaigns the gate stands before.
STRICT = ExclusionRule(strict=True)


def gate_problems(directory: Path, rule: ExclusionRule = STRICT) -> list[str]:
    try:
        campaign = load_campaign(directory, rule)
    except InvalidCampaign as error:
        return [str(error)]
    rows = campaign.rows + campaign.sequential_rows
    return [
        *run_problems(campaign.collection.failed, campaign.collection.missing, campaign.exclusions.counts()),
        *reference_problems(rows),
        *clock_problems(directory, rows),
        *drift_problems(rows),
    ]


def run_problems(failed: Mapping[str, int], missing: list[str], excluded: Mapping[Reason, int]) -> list[str]:
    problems = [f"{count} failed run(s) in {environment}" for environment, count in sorted(failed.items())]
    problems += [f"planned run without any file: {run}" for run in missing]
    problems += [f"{count} run(s) excluded by {reason}" for reason, count in excluded.items() if count]
    return problems


# The loader already refuses two checksums for one workload and input. This adds the comparison
# across workloads, which it does not make.
def reference_problems(rows: list[Row]) -> list[str]:
    checksums: defaultdict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        checksums[(row["workload"], row["input"], row["k"])].add(row["checksum"])
    problems = []
    for group in SAME_OUTPUT:
        inputs = sorted({(input_, k) for workload, input_, k in checksums if workload in group})
        for input_, k in inputs:
            found = {workload: checksums[(workload, input_, k)] for workload in group if (workload, input_, k) in checksums}
            if len(set().union(*found.values())) > 1:
                detail = ", ".join(f"{workload} {sorted(values)}" for workload, values in found.items())
                problems.append(f"{input_} k={k or '-'}: outputs differ between workloads: {detail}")
    return problems


# Every timed sample, not the median: the gate has few runs, and one short sample is the sign
# of a size or a pass count that does not fit the clock.
def clock_problems(directory: Path, rows: list[Row]) -> list[str]:
    shortest: dict[str, int] = {}
    for row in rows:
        if row["phase"] == MEASURED:
            shortest[row["run"]] = min(shortest.get(row["run"], int(row["ns"])), int(row["ns"]))
    problems = []
    for run, per_pass_ns in sorted(shortest.items()):
        context = run_context(directory, run)
        resolution = context.clock_resolution_ns
        if resolution is None:
            problems.append(f"{run}: no clock resolution recorded")
        elif per_pass_ns * context.passes < CLOCK_FACTOR * resolution:
            problems.append(f"{run}: a sample of {per_pass_ns * context.passes} ns is under {CLOCK_FACTOR}x the clock resolution {resolution} ns")
    return problems


def drift_problems(rows: list[Row], window: int = DEFAULT_WINDOW, tolerance: float = DRIFT_TOLERANCE) -> list[str]:
    problems = []
    for configuration, runs in sorted(measured_series(rows).items()):
        ratio = drift_of(configuration, runs, window).first_over_last
        if abs(ratio - 1) > tolerance:
            c = configuration
            problems.append(
                f"{c.environment} {c.workload} {c.input} k={c.k} N={c.threads}: the first {window} measured iterations "
                f"are {ratio:.3f} times the last {window}, outside {tolerance:.0%}"
            )
    return problems

