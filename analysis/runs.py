from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from analysis.configuration import Configuration, configuration_of
from analysis.stats.summary import Summary

MEASURED = "measured"
Row = dict[str, Any]


@dataclass(frozen=True)
class RunSummary:
    run: str
    configuration: Configuration
    value: float


def measured_times(rows: Iterable[Row]) -> tuple[dict[str, list[float]], dict[str, Configuration]]:
    times: dict[str, list[float]] = {}
    configurations: dict[str, Configuration] = {}
    for row in rows:
        if row["phase"] == MEASURED:
            times.setdefault(row["run"], []).append(float(row["ns"]))
            configurations[row["run"]] = configuration_of(row)
    return times, configurations


# One value per run, never per iteration: the run is the unit of analysis (Georges et al. 2007,
# https://doi.org/10.1145/1297027.1297033).
def run_summaries(rows: Iterable[Row], summary: Summary) -> list[RunSummary]:
    times, configurations = measured_times(rows)
    return [RunSummary(run, configurations[run], summary.of(values)) for run, values in times.items()]


def values_by_configuration(runs: Iterable[RunSummary]) -> dict[Configuration, list[float]]:
    groups: dict[Configuration, list[float]] = {}
    for run in runs:
        groups.setdefault(run.configuration, []).append(run.value)
    return groups
