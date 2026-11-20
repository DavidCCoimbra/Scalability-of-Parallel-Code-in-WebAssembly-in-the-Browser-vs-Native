"""Browser processes that left the run scope, found from /proc."""

from dataclasses import dataclass
from pathlib import Path

from harness.context import UNAVAILABLE
from harness.shield.cpu_time import stat_fields
from harness.shield.scope import SCOPE_SUFFIX, scope_unit

# Index of the parent pid among the /proc/<pid>/stat fields after the command name.
STAT_PARENT = 1
ARGUMENT_SEPARATOR = b"\0"


@dataclass(frozen=True)
class ProcessEntry:
    parent: int
    arguments: list[bytes]
    cgroup: str


ProcessTable = dict[int, ProcessEntry]


def process_table(root: Path) -> ProcessTable:
    try:
        entries = list((root / "proc").iterdir())
    except OSError:
        return {}
    table = {}
    for entry in entries:
        process = read_process(entry) if entry.name.isdigit() else None
        if process is not None:
            table[int(entry.name)] = process
    return table


def read_process(directory: Path) -> ProcessEntry | None:
    try:
        fields = stat_fields((directory / "stat").read_text())
        if fields is None:
            return None
        parent = int(fields[STAT_PARENT])
        arguments = (directory / "cmdline").read_bytes().split(ARGUMENT_SEPARATOR)
        cgroup = (directory / "cgroup").read_text()
    except (OSError, IndexError, ValueError):
        return None
    return ProcessEntry(parent, arguments, cgroup)


def descendants(table: ProcessTable, ancestor: int) -> set[int]:
    children: dict[int, list[int]] = {}
    for pid, process in table.items():
        children.setdefault(process.parent, []).append(pid)
    found: set[int] = set()
    pending = [ancestor]
    while pending:
        for child in children.get(pending.pop(), []):
            if child not in found:
                found.add(child)
                pending.append(child)
    return found


def escaped_processes(profile: Path, run_id: str, launched: int, root: Path = Path("/")) -> int | str:
    table = process_table(root)
    if not table:
        return UNAVAILABLE
    scope = f"/{scope_unit(run_id)}{SCOPE_SUFFIX}"
    marker = str(profile).encode()
    of_profile = {pid for pid, process in table.items() if any(marker in argument for argument in process.arguments)}
    candidates = (descendants(table, launched) | of_profile) - {launched}
    return sum(1 for pid in candidates if scope not in table[pid].cgroup)
