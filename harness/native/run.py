"""One native run, stored with the same files and context as a browser run."""

import json
import resource
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from harness.context import (
    UNAVAILABLE,
    CpuTimeMethod,
    JsonValue,
    RunContext,
    RunEnvironment,
    RunFiles,
    annotate,
    host_fields,
    loadavg,
    parse_cpu_mask,
    grain_of_query,
    passes_of_query,
    refuse_reused_run,
    round_seconds,
    sha256_file,
    utc_now,
)
from harness.native.interface import BUILD_INFO_FLAG, query_to_flags, starts_with_header
from harness.paths import REPOSITORY
from harness.shield import CgroupShield, CpuSplit, RunUsage, check_confinement, confine, stop_scope

DEFAULT_TIMEOUT_SECONDS = 3600.0
BUILD_INFO_TIMEOUT_SECONDS = 60.0


class NativeRunFailed(RuntimeError):
    pass


def children_cpu_seconds() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


@dataclass(frozen=True)
class RunnerOutput:
    completed: "subprocess.CompletedProcess[str] | None"
    timeout: float

    def failure(self) -> str | None:
        if self.completed is None:
            return f"no result after {self.timeout} s"
        if self.completed.returncode != 0:
            return f"exit {self.completed.returncode}: {self.completed.stderr.strip()}"
        if not starts_with_header(self.completed.stdout):
            return "output does not start with the CSV header"
        return None


@dataclass(frozen=True)
class RunStart:
    argv: list[str]
    build: JsonValue
    started_at: str
    loadavg_before: list[float] | str
    monotonic: float
    passes: int
    grain: int | None = None


class NativeRun:
    def __init__(
        self,
        executable: list[str],
        results: Path,
        cpus: str | None,
        order_seed: int | None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        artifact: Path | None = None,
        order_position: int | None = None,
        scope_user: str | None = None,
    ):
        check_confinement(cpus, scope_user)
        self.executable = executable
        self.results = results
        self.cpus = cpus
        self.order_seed = order_seed
        self.timeout = timeout
        self.artifact = artifact or Path(executable[-1])
        self.order_position = order_position
        self.scope_user = scope_user

    def command(self, run_id: str, query: str) -> list[str]:
        return confine([*self.executable, *query_to_flags(query)], run_id, self.cpus, self.scope_user)

    def build_info(self) -> JsonValue:
        try:
            result = subprocess.run(
                [*self.executable, BUILD_INFO_FLAG],
                capture_output=True,
                text=True,
                timeout=min(self.timeout, BUILD_INFO_TIMEOUT_SECONDS),
            )
            return json.loads(result.stdout) if result.returncode == 0 else UNAVAILABLE
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            return UNAVAILABLE

    def run(self, run_id: str, query: str) -> Path:
        refuse_reused_run(self.results, run_id)
        argv = self.command(run_id, query)
        build = self.build_info()
        usage = RunUsage.of_mask(parse_cpu_mask(self.cpus))
        start = RunStart(argv, build, utc_now(), loadavg(), time.monotonic(), passes_of_query(query), grain_of_query(query))
        children_before = children_cpu_seconds()
        usage.start()
        output = self.execute(argv, run_id)
        cpu = usage.cpu.stop(children_cpu_seconds() - children_before)
        cores = usage.cores.stop()
        self.results.mkdir(parents=True, exist_ok=True)
        context = self.context(start, cpu, cores)
        return self.store(RunFiles(self.results, run_id), output, context)

    def execute(self, argv: list[str], run_id: str) -> RunnerOutput:
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            if self.scope_user:
                stop_scope(run_id)
            return RunnerOutput(None, self.timeout)
        return RunnerOutput(completed, self.timeout)

    def store(self, files: RunFiles, output: RunnerOutput, context: RunContext) -> Path:
        failure = output.failure()
        if failure or output.completed is None:
            annotate(files.error, {"error": failure, **context.to_json()})
            raise NativeRunFailed(f"{files.run_id}: {failure}")
        with files.csv.open("x") as file:
            file.write(output.completed.stdout)
        annotate(files.metadata, context.to_json())
        return files.csv

    def context(self, start: RunStart, cpu: CpuSplit, cores: JsonValue) -> RunContext:
        return RunContext(
            **host_fields(REPOSITORY, self.cpus),
            environment=RunEnvironment.NATIVE,
            browser_version=RunEnvironment.NATIVE,
            cpu_mask=self.cpus,
            headless=None,
            launch_flags=start.argv,
            order_seed=self.order_seed,
            order_position=self.order_position,
            started_at=start.started_at,
            finished_at=utc_now(),
            launch_seconds=round_seconds(time.monotonic() - start.monotonic),
            artifact_sha256=sha256_file(self.artifact),
            build=start.build,
            loadavg_before=start.loadavg_before,
            loadavg_after=loadavg(),
            shield=CgroupShield().state(),
            run_cpu_seconds=cpu.run_seconds,
            run_cpu_method=CpuTimeMethod.RUSAGE,
            start_delay_ms=0,
            passes=start.passes,
            grain=start.grain,
            cores=cores,
            leftover_processes=0,
            escaped_processes=0,
            foreign_cpu_seconds=cpu.foreign_seconds,
        )
