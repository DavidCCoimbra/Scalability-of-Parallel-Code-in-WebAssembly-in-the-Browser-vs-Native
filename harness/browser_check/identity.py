"""What a run must reproduce in every environment: its input fingerprint and checksum."""

import csv
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from harness.launcher import RunStatus

IDENTITY_FIELDS = ("input_fingerprint", "checksum")
WHOLE_RUN = "run"


@dataclass(frozen=True)
class RunIdentity:
    input_fingerprint: str
    checksum: str

    def __str__(self) -> str:
        return f"{self.input_fingerprint}/{self.checksum}"


@dataclass(frozen=True)
class Mismatch:
    environment: str
    case: str
    field: str
    native: str
    browser: str | None


Found = RunIdentity | str


def read_identity(path: Path) -> RunIdentity:
    with path.open() as file:
        rows = list(csv.DictReader(file))
    return RunIdentity(single_value(path, rows, "input_fingerprint"), single_value(path, rows, "checksum"))


def found_identity(path: Path) -> Found:
    """The identity of a finished browser run, or a label when its CSV cannot be read as one."""
    try:
        return read_identity(path)
    except (OSError, ValueError, KeyError) as error:
        return f"<unreadable: {error}>"


def single_value(path: Path, rows: list[dict[str, str]], column: str) -> str:
    values = {row[column] for row in rows}
    if len(values) != 1:
        raise ValueError(f"{path.name}: expected one {column}, found {sorted(values)}")
    return values.pop()


def failed_label(status: RunStatus) -> str:
    return f"<{status.value}>"


def compare(native: Mapping[str, RunIdentity], browsers: Mapping[str, Mapping[str, Found]]) -> list[Mismatch]:
    return [
        mismatch
        for environment, found in browsers.items()
        for case, expected in native.items()
        for mismatch in case_mismatches(environment, case, expected, found.get(case))
    ]


def case_mismatches(environment: str, case: str, expected: RunIdentity, found: Found | None) -> list[Mismatch]:
    if not isinstance(found, RunIdentity):
        return [Mismatch(environment, case, WHOLE_RUN, str(expected), found)]
    return [
        Mismatch(environment, case, field, getattr(expected, field), getattr(found, field))
        for field in IDENTITY_FIELDS
        if getattr(expected, field) != getattr(found, field)
    ]
