"""A campaign run: check the machine, record the session, run what is still missing, log every run."""

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from harness.browsers import load_specs
from harness.campaign.executors import BrowserExecutor, ExecutionResult, Executor, NativeExecutor, ResultServer
from harness.campaign.gate import EnvironmentGate, EnvironmentNotReady, HostEnvironment
from harness.campaign.identity import build_identity
from harness.campaign.journal import CampaignJournal
from harness.campaign.plan import discarded_runs, plan
from harness.campaign.planned_run import PlannedRun
from harness.campaign.spec import CampaignSpec
from harness.context import BROWSERS, JsonObject, RunEnvironment, RunFiles, run_files_exist
from harness.context.results import ERROR_SUFFIX
from harness.launcher import RunStatus
from harness.paths import BROWSER_VERSIONS, BROWSERS_ROOT, WWW
from harness.server import BackgroundServer

DISCARDED_DIRECTORY = "discarded"
FAILED_DIRECTORY = "failed"
SYSINFO_DIRECTORY = "sysinfo"


@dataclass
class Summary:
    done: int = 0
    failed: int = 0
    skipped: int = 0
    earlier_failures: int = 0

    @property
    def ok(self) -> bool:
        return self.failed == 0 and self.earlier_failures == 0

    def count(self, status: RunStatus) -> None:
        if status == RunStatus.DONE:
            self.done += 1
        else:
            self.failed += 1


def pinned_versions() -> dict[str, str]:
    return {name: browser.version for name, browser in load_specs(BROWSER_VERSIONS).items()}


def executors_for(
    spec: CampaignSpec, native: list[str] | None, browsers: Mapping[str, Path], server: ResultServer | None
) -> dict[str, Executor]:
    executors: dict[str, Executor] = {}
    if RunEnvironment.NATIVE in spec.environments:
        executors[RunEnvironment.NATIVE] = NativeExecutor(spec, native or [str(spec.native_binary)])
    for name in BROWSERS:
        if name in spec.environments and server is not None:
            executors[name] = BrowserExecutor(spec, name, browsers[name], server)
    return executors


@dataclass
class Campaign:
    spec: CampaignSpec
    results: Path
    executors: Mapping[str, Executor]
    server: ResultServer | None = None
    pinned: dict[str, str] = field(default_factory=dict)
    build: JsonObject = field(default_factory=dict)
    retry_failed: bool = False
    environment: EnvironmentGate | None = None
    journal: CampaignJournal = field(init=False)

    def __post_init__(self) -> None:
        self.journal = CampaignJournal(self.spec, self.results, self.build, self.pinned)

    @classmethod
    def for_spec(
        cls,
        spec: CampaignSpec,
        results: Path,
        native: list[str] | None,
        browsers: Mapping[str, Path],
        retry_failed: bool = False,
        browsers_root: Path = BROWSERS_ROOT,
    ) -> "Campaign":
        server = BackgroundServer(WWW) if spec.uses_browsers else None
        environment = HostEnvironment(browsers_root, spec.cpus, spec.hybrid) if spec.strict and spec.cpus else None
        return cls(
            spec,
            results,
            executors_for(spec, native, browsers, server),
            server,
            pinned_versions(),
            build_identity(spec, native, browsers),
            retry_failed,
            environment,
        )

    def run(self) -> Summary:
        self.results.mkdir(parents=True, exist_ok=True)
        runs = plan(self.spec)
        self.require_prepared_machine()
        session = self.journal.start_session(runs)
        summary = Summary()
        self.run_discarded_launches(session)
        with self.serving(self.results):
            for run in runs:
                self.run_planned(run, summary)
        return summary

    def run_planned(self, run: PlannedRun, summary: Summary) -> None:
        files = RunFiles(self.results, run.run_id)
        if files.error.exists() and self.retry_failed:
            keep_failure(files.error, self.results / FAILED_DIRECTORY)
        elif files.error.exists():
            summary.earlier_failures += 1
            return
        elif run_files_exist(self.results, run.run_id):
            summary.skipped += 1
            return
        result = self.execute(run, self.results)
        summary.count(result.status)
        self.journal.log(run, result, self.results)

    def execute(self, run: PlannedRun, results: Path) -> ExecutionResult:
        return self.executors[run.environment].execute(run, results)

    def require_prepared_machine(self) -> None:
        if not self.spec.strict:
            return
        if self.environment is None or self.spec.cpus is None:
            raise EnvironmentNotReady("a strict campaign needs an environment check")
        problems = self.environment.problems(self.spec.cpus)
        self.environment.record(self.results / SYSINFO_DIRECTORY, problems)
        if problems:
            raise EnvironmentNotReady("machine not prepared (run harness/env/setup.sh): " + "; ".join(problems))
        browsers = unpinned_browsers(self.build, self.pinned, [name for name in BROWSERS if name in self.spec.environments])
        if browsers:
            raise EnvironmentNotReady("browser not pinned (reinstall with python3 harness/browsers.py): " + "; ".join(browsers))

    def run_discarded_launches(self, session: int) -> None:
        discard = self.results / DISCARDED_DIRECTORY
        pending = [run for run in discarded_runs(self.spec, session) if not run_files_exist(discard, run.run_id)]
        if not pending:
            return
        discard.mkdir(exist_ok=True)
        with self.serving(discard):
            for run in pending:
                self.journal.log(run, self.execute(run, discard), discard)

    @contextmanager
    def serving(self, results: Path) -> Iterator[None]:
        # Each browser posts to the directory the server writes into, so a discarded launch gets its own.
        if self.server:
            self.server.start(results)
        try:
            yield
        finally:
            if self.server:
                self.server.stop()


def unpinned_browsers(build: JsonObject, pinned: Mapping[str, str], wanted: list[str]) -> list[str]:
    # Checked before the first run: the per-run validation alone let a self-updated Firefox measure a whole campaign.
    measured = build.get("browsers")
    reported = measured if isinstance(measured, dict) else {}
    problems = []
    for name in (name for name in wanted if name in pinned):
        version = str(reported.get(name, "")).split()
        if not version:
            problems.append(f"{name} reported no version")
        elif version[-1] != pinned[name]:
            problems.append(f"{name} is {reported[name]}, not the pinned {pinned[name]}")
    return problems


def keep_failure(error: Path, failed: Path) -> None:
    failed.mkdir(exist_ok=True)
    target = failed / error.name
    attempt = 1
    while target.exists():
        attempt += 1
        target = failed / f"{error.name.removesuffix(ERROR_SUFFIX)}.attempt{attempt}{ERROR_SUFFIX}"
    error.rename(target)
