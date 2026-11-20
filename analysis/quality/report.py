from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from analysis.campaign import Context, is_hybrid, pinned_browser_versions, run_context, strict_problems
from analysis.configuration import Configuration
from analysis.quality.clock import CLOCK_FACTOR, ClockWarning, clock_warnings, run_passes, run_resolutions
from analysis.quality.foreign_cpu import FOREIGN_CPU_THRESHOLD, above_threshold
from analysis.quality.order_drift import DRIFT_LIMIT, DRIFT_MINIMUM_RUNS, OrderDrift, OrderedValue, order_drifts
from analysis.quality.variants import UNNAMED_SETTINGS, mixed_configurations
from analysis.runs import RunSummary, run_summaries
from analysis.stats.summary import RUN_SUMMARY
from harness.collect import Collection, collect

POSITION_KEY = "orderPosition"
# Runs set aside by hand so that the campaign ran the same planned run again; each one keeps
# its reason in the folder's README (a threshold fixed before the data).
EXCLUDED_DIRECTORY = "excluded"
RUN_RECORD = "*.json"


@dataclass
class RunChecks:
    strict_reasons: Counter[str] = field(default_factory=Counter)
    strict_runs: Counter[str] = field(default_factory=Counter)
    foreign: Counter[str] = field(default_factory=Counter)
    observations: defaultdict[Configuration, list[OrderedValue]] = field(default_factory=lambda: defaultdict(list))

    def check(self, run: RunSummary, context: Context, pinned: dict[str, str], hybrid: bool) -> None:
        problems = strict_problems(context, pinned, hybrid)
        if problems:
            self.strict_runs[run.configuration.environment] += 1
            self.strict_reasons.update(problem.split(":")[0] for problem in problems)
        above = above_threshold(context, FOREIGN_CPU_THRESHOLD)
        if above:
            self.foreign[run.configuration.label] += 1
        position = context.get(POSITION_KEY)
        if isinstance(position, int) and not above and not problems:
            self.observations[run.configuration].append(OrderedValue(position, run.value))


@dataclass(frozen=True)
class QualityReport:
    name: str
    collection: Collection
    runs: int
    checks: RunChecks
    clock: list[ClockWarning]
    drifts: list[OrderDrift]
    mixed: list[Configuration]
    replaced: int = 0

    @property
    def blocking(self) -> bool:
        return bool(self.collection.checksum_conflicts or self.collection.missing or self.collection.failed or self.mixed)

    def lines(self) -> list[str]:
        collection, checks = self.collection, self.checks
        return [
            f"# Data quality: {self.name}",
            "",
            f"- Runs done: {self.runs}; missing: {len(collection.missing)}; failed: {sum(collection.failed.values())} {dict(collection.failed)}",
            f"- Runs replaced by a re-run (kept in `{EXCLUDED_DIRECTORY}/`): {self.replaced}",
            f"- Checksum conflicts: {len(collection.checksum_conflicts)}",
            f"- Runs failing strict validation: {sum(checks.strict_runs.values())} {dict(checks.strict_runs)}; reasons: {dict(checks.strict_reasons)}",
            f"- Runs above the foreign CPU threshold ({FOREIGN_CPU_THRESHOLD} s): {sum(checks.foreign.values())} {dict(checks.foreign)}",
            f"- Configurations under {CLOCK_FACTOR} times the clock resolution: {len(self.clock)}"
            + "".join(f"\n  - {warning.configuration.label}" for warning in self.clock),
            f"- Configurations whose valid run values trend with the execution order (|rho| > {DRIFT_LIMIT}, at least {DRIFT_MINIMUM_RUNS} runs): {len(self.drifts)}"
            + "".join(f"\n  - {item.line()}" for item in self.drifts),
            f"- Configurations mixing {', '.join(UNNAMED_SETTINGS)}: {len(self.mixed)}"
            + "".join(f"\n  - {configuration.label}" for configuration in self.mixed),
            f"- Blocking the analysis (checksum conflicts, missing or failed runs, mixed settings): {'yes' if self.blocking else 'no'}",
            "",
        ]

    def text(self) -> str:
        return "\n".join(self.lines())


# Nothing is removed here: the report only counts, and the exclusions are the analysis plan's (D7).
def quality_report(directory: Path) -> QualityReport:
    collection = collect(directory)
    runs = run_summaries(collection.rows, RUN_SUMMARY)
    pinned, hybrid = pinned_browser_versions(), is_hybrid(directory)
    checks = RunChecks()
    for run in runs:
        checks.check(run, run_context(directory, run.run), pinned, hybrid)
    run_ids = {run.run for run in runs}
    clock = clock_warnings(runs, run_resolutions(directory, run_ids), passes=run_passes(directory, run_ids))
    return QualityReport(
        directory.name,
        collection,
        len(runs),
        checks,
        clock,
        order_drifts(checks.observations),
        mixed_configurations(collection.rows),
        replaced_runs(directory),
    )


def replaced_runs(directory: Path) -> int:
    return len(list((directory / EXCLUDED_DIRECTORY).glob(RUN_RECORD)))
