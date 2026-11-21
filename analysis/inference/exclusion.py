from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from analysis.campaign import is_hybrid, pinned_browser_versions
from analysis.configuration import Configuration, configuration_of
from analysis.run_context import run_context
from harness.collect import Row


class Reason(StrEnum):
    FOREIGN_CPU = "foreignCpuSeconds"
    STRICT_VALIDATION = "strictValidation"


# Analysis plan D7: no statistical outlier removal; only these predefined exclusions, all counted.
# A run above the threshold is counted only there, never also as a strict-validation failure.
@dataclass(frozen=True)
class Exclusions:
    runs: dict[Reason, set[str]]

    @property
    def dropped(self) -> set[str]:
        return set().union(*self.runs.values())

    def counts(self) -> dict[Reason, int]:
        return {reason: len(runs) for reason, runs in self.runs.items()}

    def by_environment(self, rows: list[Row]) -> dict[str, dict[str, int]]:
        environment = {row["run"]: row["env"] for row in rows}
        counts: dict[str, Counter[str]] = {}
        for reason, runs in self.runs.items():
            for run in runs:
                counts.setdefault(environment[run], Counter())[reason] += 1
        return {name: dict(counter) for name, counter in sorted(counts.items())}

    def by_configuration(self, rows: list[Row]) -> list[dict[str, Any]]:
        configuration = {row["run"]: configuration_of(row) for row in rows}
        counts: dict[Configuration, Counter[str]] = {}
        for reason, runs in self.runs.items():
            for run in runs:
                counts.setdefault(configuration[run], Counter())[reason] += 1
        return [{**c.as_json(), **counter} for c, counter in sorted(counts.items())]


def excluded_runs(directory: Path, run_ids: set[str], threshold: float | None, strict: bool) -> Exclusions:
    pinned = pinned_browser_versions()
    hybrid = is_hybrid(directory)
    runs: dict[Reason, set[str]] = {Reason.FOREIGN_CPU: set(), Reason.STRICT_VALIDATION: set()}
    for run_id in run_ids:
        context = run_context(directory, run_id)
        if threshold is not None and context.above_foreign_cpu(threshold):
            runs[Reason.FOREIGN_CPU].add(run_id)
        elif strict and context.strict_problems(pinned, hybrid):
            runs[Reason.STRICT_VALIDATION].add(run_id)
    return Exclusions(runs)
