"""Launch one browser run: fresh profile, optional taskset mask, no automation.

Usage: python3 -m harness.launcher --browser chrome|firefox --executable PATH
       --run ID --query "workload=...&threads=..." [--cpus 0,2,4,6,8,10,12,14] [--headless]
       [--timeout 300] [--port 8000] [--results data/raw]
       [--scope-user USER] [--harness-cpus 16-31] [--start-delay-ms 0]
The results server (harness/server.py) must be running.
"""

from harness.launcher.commands import (
    CHROME_FLAGS,
    COMMANDS,
    FIREFOX_PREFS,
    BrowserCommand,
    ChromeCommand,
    FirefoxCommand,
    command_for,
)
from harness.launcher.engine_arm import EngineArm
from harness.launcher.launcher import MAX_START_DELAY_MS, Launcher
from harness.launcher.outcome import LaunchRecord, RunOutcome, RunStatus, Teardown
from harness.launcher.processes import KILL_GRACE_SECONDS, kill_processes_using, stop_process_group
from harness.launcher.url import RESERVED_KEYS, run_url

__all__ = [
    "CHROME_FLAGS",
    "COMMANDS",
    "FIREFOX_PREFS",
    "KILL_GRACE_SECONDS",
    "MAX_START_DELAY_MS",
    "RESERVED_KEYS",
    "BrowserCommand",
    "ChromeCommand",
    "EngineArm",
    "FirefoxCommand",
    "LaunchRecord",
    "Launcher",
    "RunOutcome",
    "RunStatus",
    "Teardown",
    "command_for",
    "kill_processes_using",
    "run_url",
    "stop_process_group",
]
