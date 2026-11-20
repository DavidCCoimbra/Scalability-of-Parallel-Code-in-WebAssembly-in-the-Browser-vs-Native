"""Run one planned run in its environment: the native runner or a browser launch."""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from harness.campaign.planned_run import PlannedRun
from harness.campaign.spec import CampaignSpec
from harness.context import round_seconds
from harness.launcher import COMMANDS, Launcher, RunStatus
from harness.native import NativeRun, NativeRunFailed


@dataclass(frozen=True)
class ExecutionResult:
    status: RunStatus
    seconds: float
    message: str | None


class Executor(Protocol):
    def execute(self, run: PlannedRun, results: Path) -> ExecutionResult: ...


class ResultServer(Protocol):
    @property
    def port(self) -> int | None: ...

    def start(self, results: Path) -> int: ...

    def stop(self) -> None: ...


class NativeExecutor:
    def __init__(self, spec: CampaignSpec, executable: list[str]):
        self.spec = spec
        self.executable = executable

    def execute(self, run: PlannedRun, results: Path) -> ExecutionResult:
        native = NativeRun(
            self.executable,
            results,
            self.spec.cpus,
            self.spec.order_seed,
            timeout=self.spec.timeout_seconds,
            order_position=run.order_position,
            scope_user=self.spec.resolved_scope_user,
        )
        started = time.monotonic()
        try:
            native.run(run.run_id, self.spec.query(run))
        except NativeRunFailed as error:
            return ExecutionResult(RunStatus.ERROR, round_seconds(time.monotonic() - started), str(error))
        return ExecutionResult(RunStatus.DONE, round_seconds(time.monotonic() - started), None)


class BrowserExecutor:
    def __init__(self, spec: CampaignSpec, browser: str, executable: Path, server: ResultServer):
        self.spec = spec
        self.browser = browser
        self.executable = executable
        self.server = server

    def execute(self, run: PlannedRun, results: Path) -> ExecutionResult:
        if self.server.port is None:
            raise RuntimeError("the results server must be started before a browser run")
        launcher = Launcher(
            COMMANDS[self.browser](),
            self.executable,
            results,
            port=self.server.port,
            cpus=self.spec.cpus,
            headless=self.spec.headless,
            timeout=self.spec.timeout_seconds,
            order_seed=self.spec.order_seed,
            order_position=run.order_position,
            scope_user=self.spec.resolved_scope_user,
            start_delay_ms=self.spec.start_delay_ms,
        )
        outcome = launcher.run(run.run_id, self.spec.query(run))
        return ExecutionResult(outcome.status, round_seconds(outcome.seconds), outcome.message)
