import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from analysis.configuration import SEQUENTIAL_WORKLOADS
from analysis.inference.exclusion import Exclusions, excluded_runs
from analysis.quality.foreign_cpu import FOREIGN_CPU_THRESHOLD
from analysis.runs import RunSummary, run_summaries
from analysis.stats.summary import RUN_SUMMARY, Summary
from harness.collect import Collection, Row, collect


class InvalidCampaign(ValueError):
    pass


@dataclass(frozen=True)
class ExclusionRule:
    foreign_cpu_threshold: float | None = FOREIGN_CPU_THRESHOLD
    strict: bool = False

    def as_json(self) -> dict[str, Any]:
        return {"foreignCpuThreshold": self.foreign_cpu_threshold, "strict": self.strict}


# The only way a command reads a campaign: every table and figure then sees the same runs, the
# ones left by the analysis plan's predefined exclusions (D7).
@dataclass(frozen=True)
class LoadedCampaign:
    directory: Path
    collection: Collection
    rule: ExclusionRule
    exclusions: Exclusions
    rows: list[Row]
    # The runs of the sequential references, kept apart from the scaling curves in `rows`.
    sequential_rows: list[Row]

    def summaries(self, summary: Summary = RUN_SUMMARY) -> list[RunSummary]:
        return run_summaries(self.rows, summary)

    def sequential_summaries(self, summary: Summary = RUN_SUMMARY) -> list[RunSummary]:
        return run_summaries(self.sequential_rows, summary)

    # Disjoint by construction: a missing run has no file, a failed run has only an error file, and
    # an excluded run has its data and is counted by reason.
    def gaps_json(self) -> dict[str, Any]:
        return {
            **self.rule.as_json(),
            "excluded": self.exclusions.counts(),
            "failed": dict(self.collection.failed),
            "missing": self.collection.missing,
        }

    def report_gaps(self, stream: TextIO = sys.stderr) -> None:
        for reason, count in self.exclusions.counts().items():
            if count:
                print(f"{self.directory}: runs excluded by {reason}: {count}", file=stream)
        for environment, count in sorted(self.collection.failed.items()):
            print(f"{self.directory}: failed runs in {environment}: {count} (excluded)", file=stream)
        for run in self.collection.missing:
            print(f"{self.directory}: planned run without any file: {run}", file=stream)


def conflict_details(conflicts: dict[str, list[str]]) -> str:
    return "; ".join(f"{key}: {', '.join(values)}" for key, values in conflicts.items())


def load_campaign(directory: Path, rule: ExclusionRule = ExclusionRule()) -> LoadedCampaign:
    collection = collect(directory)
    if collection.checksum_conflicts:
        raise InvalidCampaign(f"{directory}: checksums differ, nothing written: {conflict_details(collection.checksum_conflicts)}")
    run_ids = {str(row["run"]) for row in collection.rows}
    exclusions = excluded_runs(directory, run_ids, rule.foreign_cpu_threshold, rule.strict)
    dropped = exclusions.dropped
    kept = [row for row in collection.rows if row["run"] not in dropped]
    return LoadedCampaign(
        directory,
        collection,
        rule,
        exclusions,
        [row for row in kept if row["workload"] not in SEQUENTIAL_WORKLOADS],
        [row for row in kept if row["workload"] in SEQUENTIAL_WORKLOADS],
    )


def add_exclusion_arguments(parser: argparse.ArgumentParser) -> None:
    threshold = parser.add_mutually_exclusive_group()
    threshold.add_argument("--foreign-cpu-threshold", type=float, default=FOREIGN_CPU_THRESHOLD)
    # The plan's sensitivity check "without exclusion 3".
    threshold.add_argument("--no-foreign-cpu-threshold", action="store_true")
    parser.add_argument("--strict", action="store_true")


def exclusion_rule(args: argparse.Namespace) -> ExclusionRule:
    return ExclusionRule(None if args.no_foreign_cpu_threshold else args.foreign_cpu_threshold, args.strict)
