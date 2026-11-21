from dataclasses import dataclass
from pathlib import Path
from typing import Any

from analysis.campaign import order_seed_and_build
from analysis.provenance import provenance
from analysis.configuration import Configuration
from analysis.inference.contrast import Contrast
from analysis.inference.exclusion import Exclusions
from analysis.inference.family import FAMILY_ALPHA
from analysis.quality.clock import CLOCK_FACTOR, ClockReport
from analysis.stats.bootstrap import BOOTSTRAP_SEED, CONFIDENCE
from harness.collect import Collection


@dataclass(frozen=True)
class ResultsOptions:
    directory: Path
    contrasts: Path
    shape: Path | None
    foreign_cpu_threshold: float | None
    strict: bool
    summary: str
    center: str
    resamples: int
    max_threads: int
    partial: bool


@dataclass(frozen=True)
class ResultsOutcome:
    collection: Collection
    exclusions: Exclusions
    results: list[Contrast]
    clock: ClockReport
    missing_absolute: list[Configuration]


def options_json(options: ResultsOptions) -> dict[str, Any]:
    return {
        "summary": options.summary,
        "center": options.center,
        "confidence": CONFIDENCE,
        "familyAlpha": FAMILY_ALPHA,
    }


def bootstrap_and_exclusion_json(options: ResultsOptions, outcome: ResultsOutcome) -> dict[str, Any]:
    rows = outcome.collection.rows
    return {
        "primaryContrasts": sum(contrast.primary for contrast in outcome.results),
        "bootstrapResamples": options.resamples,
        "bootstrapSeed": BOOTSTRAP_SEED,
        "foreignCpuThreshold": options.foreign_cpu_threshold,
        "strict": options.strict,
        "maxThreads": options.max_threads,
        "partial": options.partial,
        "excluded": outcome.exclusions.counts(),
        "excludedByEnvironment": outcome.exclusions.by_environment(rows),
        "excludedByConfiguration": outcome.exclusions.by_configuration(rows),
    }


# Key order is part of the file: the sidecars are committed, so a reordering would show up as a
# change in every campaign's JSON.
def results_sidecar(options: ResultsOptions, outcome: ResultsOutcome) -> dict[str, Any]:
    return {
        "campaign": str(options.directory),
        "clockFactor": CLOCK_FACTOR,
        "clockWarnings": outcome.clock.warnings,
        "clockUnchecked": outcome.clock.unchecked,
        "missingAbsolute": [configuration.as_json() for configuration in outcome.missing_absolute],
        **options_json(options),
        **bootstrap_and_exclusion_json(options, outcome),
        **order_seed_and_build(options.directory),
        "failed": dict(outcome.collection.failed),
        "missing": outcome.collection.missing,
        **provenance(),
    }
