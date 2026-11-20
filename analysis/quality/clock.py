from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, TextIO

from analysis.campaign import Context, passes_of, run_context
from analysis.configuration import Configuration
from analysis.runs import RunSummary
from harness.context import DEFAULT_PASSES

# A configuration's median run value must be at least 100 times the coarsest clock
# resolution of its runs (the plan's 1000 is out of reach in Firefox at any usable image size).
CLOCK_FACTOR = 100
RESOLUTION_KEY = "clockResolutionNs"
NO_PASSES: Mapping[str, int] = {}


@dataclass(frozen=True)
class ClockWarning:
    configuration: Configuration
    median_ns: float
    resolution_ns: int
    passes: int = DEFAULT_PASSES

    def as_json(self) -> dict[str, Any]:
        passes = {} if self.passes == DEFAULT_PASSES else {"passes": self.passes}
        return {**self.configuration.as_json(), "medianNs": self.median_ns, "resolutionNs": self.resolution_ns, **passes}

    def message(self) -> str:
        c = self.configuration
        passes = "" if self.passes == DEFAULT_PASSES else f" ({self.passes} passes per timed sample)"
        return (
            f"warning: {c.environment} {c.workload} {c.input} k={c.k} N={c.threads}: median {self.median_ns:.0f} ns{passes} "
            f"is under {CLOCK_FACTOR}x the clock resolution {self.resolution_ns} ns"
        )


@dataclass(frozen=True)
class ClockReport:
    warnings: list[dict[str, Any]]
    unchecked: int


# Browser runs record the resolution in the page metadata; native runs record it in the build block.
def clock_resolution(context: Context) -> int | None:
    if isinstance(context.get(RESOLUTION_KEY), int):
        resolution: int = context[RESOLUTION_KEY]
        return resolution
    build = context.get("build")
    if isinstance(build, dict) and isinstance(build.get(RESOLUTION_KEY), int):
        built: int = build[RESOLUTION_KEY]
        return built
    return None


def run_resolutions(directory: Path, run_ids: Iterable[str]) -> dict[str, int]:
    resolutions = {}
    for run_id in run_ids:
        resolution = clock_resolution(run_context(directory, run_id))
        if resolution is not None:
            resolutions[run_id] = resolution
    return resolutions


def run_passes(directory: Path, run_ids: Iterable[str]) -> dict[str, int]:
    return {run_id: passes_of(run_context(directory, run_id)) for run_id in run_ids}


# A run value is the time per pass, so the clock reads K times that; the check is on the
# timed sample, value x K.
def sample_values(runs: Iterable[RunSummary], passes: Mapping[str, int]) -> dict[Configuration, list[float]]:
    samples: dict[Configuration, list[float]] = {}
    for run in runs:
        samples.setdefault(run.configuration, []).append(run.value * passes.get(run.run, DEFAULT_PASSES))
    return samples


def configuration_passes(runs: Iterable[RunSummary], passes: Mapping[str, int]) -> dict[Configuration, int]:
    fewest: dict[Configuration, int] = {}
    for run in runs:
        count = passes.get(run.run, DEFAULT_PASSES)
        fewest[run.configuration] = min(fewest.get(run.configuration, count), count)
    return fewest


def unchecked_configurations(runs: Iterable[RunSummary], resolutions: dict[str, int]) -> list[Configuration]:
    checked: dict[Configuration, bool] = {}
    for run in runs:
        checked[run.configuration] = checked.get(run.configuration, False) or run.run in resolutions
    return sorted(configuration for configuration, is_checked in checked.items() if not is_checked)


def coarsest_resolutions(runs: Iterable[RunSummary], resolutions: dict[str, int]) -> dict[Configuration, int]:
    coarsest: dict[Configuration, int] = {}
    for run in runs:
        if run.run in resolutions:
            coarsest[run.configuration] = max(coarsest.get(run.configuration, 0), resolutions[run.run])
    return coarsest


def clock_warnings(
    runs: Iterable[RunSummary],
    resolutions: dict[str, int],
    factor: int = CLOCK_FACTOR,
    passes: Mapping[str, int] = NO_PASSES,
) -> list[ClockWarning]:
    runs = list(runs)
    samples = sample_values(runs, passes)
    counts = configuration_passes(runs, passes)
    warnings = []
    for configuration, resolution in sorted(coarsest_resolutions(runs, resolutions).items()):
        median_ns = median(samples[configuration])
        if median_ns < factor * resolution:
            warnings.append(ClockWarning(configuration, median_ns, resolution, counts[configuration]))
    return warnings


def report_clock_warnings(directory: Path, runs: list[RunSummary], stream: TextIO) -> ClockReport:
    run_ids = {run.run for run in runs}
    resolutions = run_resolutions(directory, run_ids)
    warnings = clock_warnings(runs, resolutions, passes=run_passes(directory, run_ids))
    unchecked = unchecked_configurations(runs, resolutions)
    if unchecked:
        print(f"warning: {len(unchecked)} configuration(s) have no recorded clock resolution and were not checked", file=stream)
    for warning in warnings:
        print(warning.message(), file=stream)
    return ClockReport([warning.as_json() for warning in warnings], len(unchecked))
