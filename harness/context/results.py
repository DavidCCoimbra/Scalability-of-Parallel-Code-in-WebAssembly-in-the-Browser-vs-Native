"""The files one run leaves in a results directory, and how they are written."""

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from harness.context.json_value import JsonObject

CSV_SUFFIX = ".csv"
METADATA_SUFFIX = ".json"
ERROR_SUFFIX = ".error.json"
BROWSER_LOG_SUFFIX = ".browser.log"
STAGING_PREFIX = ".staging-"
JSON_INDENT = 2


@dataclass(frozen=True)
class RunFiles:
    directory: Path
    run_id: str

    @property
    def csv(self) -> Path:
        return self.directory / f"{self.run_id}{CSV_SUFFIX}"

    @property
    def metadata(self) -> Path:
        return self.directory / f"{self.run_id}{METADATA_SUFFIX}"

    @property
    def error(self) -> Path:
        return self.directory / f"{self.run_id}{ERROR_SUFFIX}"

    @property
    def browser_log(self) -> Path:
        return self.directory / f"{self.run_id}{BROWSER_LOG_SUFFIX}"

    def existing(self) -> list[str]:
        return [path.name for path in (self.csv, self.metadata, self.error) if path.exists()]


def run_files_exist(results: Path, run_id: str) -> list[str]:
    return RunFiles(results, run_id).existing()


def refuse_reused_run(results: Path, run_id: str) -> None:
    existing = run_files_exist(results, run_id)
    if existing:
        raise FileExistsError(f"run {run_id} already has {', '.join(existing)}")


def annotate(path: Path, fields: JsonObject) -> None:
    data: JsonObject = json.loads(path.read_text()) if path.exists() else {}
    data.update(fields)
    # Write a staged file and rename it, so a crash never leaves half a JSON document.
    descriptor, staged = tempfile.mkstemp(dir=path.parent, prefix=STAGING_PREFIX)
    with os.fdopen(descriptor, "w") as file:
        json.dump(data, file, indent=JSON_INDENT)
    os.replace(staged, path)
