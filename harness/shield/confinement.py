"""Confine a command to the measured CPUs: taskset, optionally inside a run scope."""

import os

from harness.context import parse_cpu_mask
from harness.shield.scope import scope_prefix


def check_confinement(cpus: str | None, scope_user: str | None) -> None:
    parse_cpu_mask(cpus)
    if scope_user and not cpus:
        raise ValueError("a systemd scope needs a CPU mask")


def confine(argv: list[str], run_id: str, cpus: str | None, scope_user: str | None) -> list[str]:
    if not cpus:
        return argv
    pinned = ["taskset", "-c", cpus, *argv]
    if not scope_user:
        return pinned
    return [*scope_prefix(run_id, cpus, scope_user, os.environ), *pinned]


def pin_current_process(cpus: str | None) -> None:
    allowed = parse_cpu_mask(cpus)
    if allowed:
        os.sched_setaffinity(0, allowed)
