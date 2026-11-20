"""Where a result came from: commit, artifact digest, tool output, time and load."""

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from harness.context.unavailable import UNAVAILABLE

DIRTY_SUFFIX = "-dirty"
COMMAND_TIMEOUT_SECONDS = 30
LOADAVG_DIGITS = 2


def git_commit(repository: Path) -> str:
    try:
        commit = run_git(repository, "rev-parse", "HEAD")
        changes = run_git(repository, "status", "--porcelain", "--untracked-files=no")
    except (OSError, subprocess.CalledProcessError):
        return UNAVAILABLE
    return f"{commit}{DIRTY_SUFFIX}" if changes else commit


def run_git(repository: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(repository), *args], capture_output=True, text=True, check=True)
    return completed.stdout.strip()


def command_output(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        return UNAVAILABLE
    output = result.stdout.strip()
    return output if result.returncode == 0 and output else UNAVAILABLE


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return UNAVAILABLE


def loadavg() -> list[float] | str:
    try:
        return [round(value, LOADAVG_DIGITS) for value in os.getloadavg()]
    except OSError:
        return UNAVAILABLE


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
