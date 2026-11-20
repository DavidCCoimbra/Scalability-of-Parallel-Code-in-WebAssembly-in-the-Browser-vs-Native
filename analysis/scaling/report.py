import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from analysis.provenance import provenance
from analysis.quality.clock import CLOCK_FACTOR, report_clock_warnings
from analysis.scaling.output import Scaling
from analysis.scaling.table import ScalingRow, scaling_table
from analysis.runs import run_summaries
from analysis.stats.bootstrap import BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED, CONFIDENCE
from analysis.stats.summary import CONFIGURATION_CENTER, RUN_SUMMARY, Summary
from harness.collect import collect


class InvalidCampaign(ValueError):
    pass


@dataclass(frozen=True)
class ScalingReport:
    rows: list[ScalingRow]
    failed: dict[str, int]
    missing: list[str]
    clock_warnings: list[dict[str, Any]]
    clock_unchecked: int


def conflict_details(conflicts: dict[str, list[str]]) -> str:
    return "; ".join(f"{key}: {', '.join(values)}" for key, values in conflicts.items())


def analyse(directory: Path, summary: Summary = RUN_SUMMARY, center: Summary = CONFIGURATION_CENTER) -> ScalingReport:
    collection = collect(directory)
    if collection.checksum_conflicts:
        raise InvalidCampaign(f"checksums differ, no table written: {conflict_details(collection.checksum_conflicts)}")
    summaries = run_summaries(collection.rows, summary)
    clock = report_clock_warnings(directory, summaries, sys.stderr)
    return ScalingReport(
        scaling_table(summaries, center), dict(collection.failed), collection.missing, clock.warnings, clock.unchecked
    )


@dataclass(frozen=True)
class ScalingOptions:
    directory: Path
    summary: str
    center: str
    scaling: Scaling


# Key order is part of the file: the sidecars are committed, so a reordering would show up as a
# change in every campaign's JSON.
def scaling_sidecar(options: ScalingOptions, report: ScalingReport) -> dict[str, Any]:
    return {
        "campaign": str(options.directory),
        "summary": options.summary,
        "center": options.center,
        "scaling": options.scaling.value,
        "confidence": CONFIDENCE,
        "bootstrapResamples": BOOTSTRAP_RESAMPLES,
        "bootstrapSeed": BOOTSTRAP_SEED,
        **provenance(),
        "clockFactor": CLOCK_FACTOR,
        "clockWarnings": report.clock_warnings,
        "clockUnchecked": report.clock_unchecked,
    }
