"""One browser run: fresh profile, confined to the measured CPUs, no automation."""

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from harness.context import (
    UNAVAILABLE,
    CpuTimeMethod,
    JsonObject,
    RunContext,
    RunFiles,
    annotate,
    command_output,
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
from harness.launcher.commands import BrowserCommand
from harness.launcher.engine_arm import EngineArm
from harness.launcher.outcome import LaunchRecord, RunOutcome, RunStatus, Teardown
from harness.launcher.processes import kill_processes_using, stop_process_group
from harness.launcher.url import run_url
from harness.paths import REPOSITORY, WASM_ARTIFACT
from harness.shield import (
    CgroupShield,
    RunUsage,
    check_confinement,
    confine,
    escaped_processes,
    process_session_seconds,
    scope_cpu_seconds,
    stop_scope,
)

DEFAULT_PORT = 8000
DEFAULT_TIMEOUT_SECONDS = 300.0
DEFAULT_POLL_SECONDS = 0.2
# The page waits with setTimeout, whose delay is a signed 32-bit number of milliseconds.
# https://developer.mozilla.org/en-US/docs/Web/API/Window/setTimeout#maximum_delay_value
MAX_START_DELAY_MS = 2**31 - 1
PROFILE_PREFIX = "bench-"

PageVerdict = tuple[RunStatus, str | None]


class Launcher:
    def __init__(
        self,
        browser: BrowserCommand,
        executable: Path,
        results: Path,
        port: int = DEFAULT_PORT,
        cpus: str | None = None,
        headless: bool = False,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        poll: float = DEFAULT_POLL_SECONDS,
        order_seed: int | None = None,
        order_position: int | None = None,
        artifact: Path = WASM_ARTIFACT,
        scope_user: str | None = None,
        start_delay_ms: int = 0,
        engine_arm: EngineArm | None = None,
    ):
        check_confinement(cpus, scope_user)
        if not 0 <= start_delay_ms <= MAX_START_DELAY_MS:
            raise ValueError(f"start delay must be between 0 and {MAX_START_DELAY_MS} ms")
        self.browser = browser
        self.executable = executable
        self.results = results
        self.port = port
        self.cpus = cpus
        self.headless = headless
        self.timeout = timeout
        self.poll = poll
        self.order_seed = order_seed
        self.order_position = order_position
        self.artifact = artifact
        self.scope_user = scope_user
        self.start_delay_ms = start_delay_ms
        self.engine_arm = engine_arm

    def command(self, profile: Path, run_id: str, query: str) -> list[str]:
        url = run_url(self.port, run_id, self.browser.name, query, self.start_delay_ms)
        argv = self.browser.argv(self.executable, profile, url, self.headless)
        return confine(argv, run_id, self.cpus, self.scope_user)

    def run(self, run_id: str, query: str) -> RunOutcome:
        refuse_reused_run(self.results, run_id)
        self.results.mkdir(parents=True, exist_ok=True)
        profile = Path(tempfile.mkdtemp(prefix=f"{PROFILE_PREFIX}{self.browser.name}-"))
        try:
            return self.run_on_profile(profile, run_id, query)
        finally:
            shutil.rmtree(profile, ignore_errors=True)

    def run_on_profile(self, profile: Path, run_id: str, query: str) -> RunOutcome:
        files = RunFiles(self.results, run_id)
        usage = RunUsage.of_mask(parse_cpu_mask(self.cpus))
        started_at, load_before, started = utc_now(), loadavg(), time.monotonic()
        self.browser.prepare_profile(profile)
        usage.start()
        with files.browser_log.open("w") as output:
            argv = self.command(profile, run_id, query)
            process = subprocess.Popen(argv, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                status, message = self.wait_for_result(process, files, started)
            finally:
                teardown = self.tear_down(process, profile, run_id, usage)
        seconds = time.monotonic() - started
        exit_code = process.returncode if status is RunStatus.EXITED else None
        record = LaunchRecord(argv, started_at, seconds, load_before, teardown, passes_of_query(query), grain_of_query(query))
        self.record_outcome(files, status, message, exit_code, record)
        if status is RunStatus.DONE:
            files.browser_log.unlink(missing_ok=True)
        return RunOutcome(run_id, status, seconds, exit_code, message)

    def wait_for_result(self, process: "subprocess.Popen[bytes]", files: RunFiles, started: float) -> PageVerdict:
        while time.monotonic() - started < self.timeout:
            if files.csv.exists():
                return RunStatus.DONE, None
            if files.error.exists():
                return RunStatus.ERROR, json.loads(files.error.read_text()).get("error")
            if process.poll() is not None:
                return (RunStatus.DONE, None) if files.csv.exists() else (RunStatus.EXITED, None)
            time.sleep(self.poll)
        return RunStatus.TIMEOUT, None

    def tear_down(self, process: "subprocess.Popen[bytes]", profile: Path, run_id: str, usage: RunUsage) -> Teardown:
        # Read the CPU time and the escaped processes while the browser still runs:
        # stopping the scope or the group first would empty what they count.
        cpu_seconds = usage.cpu.stop(self.run_cpu_seconds(process, run_id))
        cores = usage.cores.stop()
        escaped = escaped_processes(profile, run_id, process.pid) if self.scope_user else UNAVAILABLE
        if self.scope_user:
            stop_scope(run_id)
        stop_process_group(process)
        leftovers = kill_processes_using(profile)
        return Teardown(cpu_seconds, leftovers, escaped, cores)

    def run_cpu_seconds(self, process: "subprocess.Popen[bytes]", run_id: str) -> float | str:
        return scope_cpu_seconds(run_id) if self.scope_user else process_session_seconds(process.pid)

    def record_outcome(
        self, files: RunFiles, status: RunStatus, message: str | None, exit_code: int | None, record: LaunchRecord
    ) -> None:
        if status is RunStatus.DONE:
            target = files.metadata
        else:
            target = files.error
            if status is not RunStatus.ERROR:
                annotate(target, {"error": f"{status.value}: {failure_reason(status, exit_code)}"})
        annotate(target, self.context(target, record).to_json())

    def context(self, target: Path, record: LaunchRecord) -> RunContext:
        page_meta: JsonObject = json.loads(target.read_text()) if target.exists() else {}
        return RunContext(
            **host_fields(REPOSITORY, self.cpus),
            environment=self.browser.name,
            browser_version=command_output(self.browser.version_command(self.executable)),
            cpu_mask=self.cpus,
            headless=self.headless,
            launch_flags=record.argv,
            order_seed=self.order_seed,
            order_position=self.order_position,
            started_at=record.started_at,
            finished_at=utc_now(),
            launch_seconds=round_seconds(record.seconds),
            artifact_sha256=sha256_file(self.artifact),
            build=page_meta.get("build", UNAVAILABLE),
            loadavg_before=record.loadavg_before,
            loadavg_after=loadavg(),
            shield=CgroupShield().state(),
            run_cpu_seconds=record.teardown.cpu_seconds.run_seconds,
            run_cpu_method=CpuTimeMethod.SCOPE if self.scope_user else CpuTimeMethod.SESSION,
            start_delay_ms=self.start_delay_ms,
            passes=record.passes,
            grain=record.grain,
            cores=record.teardown.cores,
            engine_arm=self.engine_arm.to_json() if self.engine_arm else None,
            leftover_processes=record.teardown.leftover_processes,
            escaped_processes=record.teardown.escaped_processes,
            foreign_cpu_seconds=record.teardown.cpu_seconds.foreign_seconds,
        )


def failure_reason(status: RunStatus, exit_code: int | None) -> str:
    return "no result before the timeout" if status is RunStatus.TIMEOUT else f"browser exited with {exit_code}"
