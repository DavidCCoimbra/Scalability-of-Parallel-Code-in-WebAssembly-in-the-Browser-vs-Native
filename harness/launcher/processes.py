"""Stop a browser and everything it started, including processes outside its group."""

import os
import signal
import subprocess
from pathlib import Path

from harness.context import UNAVAILABLE

KILL_GRACE_SECONDS = 5.0
PGREP_TIMEOUT_SECONDS = 10


def stop_process_group(process: "subprocess.Popen[bytes]") -> None:
    signal_group(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=KILL_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        pass
    signal_group(process.pid, signal.SIGKILL)
    process.wait()


def signal_group(group: int, sig: signal.Signals) -> None:
    try:
        os.killpg(group, sig)
    except (ProcessLookupError, PermissionError):
        pass


def kill_processes_using(profile: Path) -> int | str:
    # Browsers start helpers in their own sessions; the profile path in their command line finds them.
    try:
        found = subprocess.run(["pgrep", "-f", str(profile)], capture_output=True, text=True, timeout=PGREP_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        return UNAVAILABLE
    pids = [int(pid) for pid in found.stdout.split()]
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    return len(pids)
