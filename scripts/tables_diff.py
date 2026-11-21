"""Check that the tables under data/tables are the ones the code regenerates.

Usage: python3 scripts/tables_diff.py [DIR]   (default: data/tables)
Run after the result targets (make tables-check does both). Compares every
file under DIR with the committed one and prints one line per file that
differs or is new. A sidecar's commit and createdAt change on every
regeneration, so lines with those keys are ignored. Exits 1 on any difference.
"""

import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

DEFAULT_DIR = Path("data/tables")
# Keys of analysis/provenance.py, rewritten by every regeneration.
VOLATILE_KEYS = ('"commit":', '"createdAt":')


def stable_lines(text: str) -> list[str]:
    return [line for line in text.splitlines(keepends=True) if not line.lstrip().startswith(VOLATILE_KEYS)]


def git(*arguments: str) -> str:
    return subprocess.run(["git", *arguments], check=True, capture_output=True, text=True).stdout


def committed(path: Path) -> str:
    return git("show", f"HEAD:{path.as_posix()}")


def changed_files(directory: Path) -> Iterator[tuple[str, Path]]:
    # -z: NUL-separated and unquoted, so any file name is read as it is.
    for entry in git("status", "--porcelain", "-z", "--untracked-files=all", "--", directory.as_posix()).split("\0"):
        if entry:
            yield entry[:2].strip(), Path(entry[3:])


def problems(directory: Path) -> Iterator[str]:
    for status, path in changed_files(directory):
        if status == "??":
            yield f"{path}: not committed"
        elif status == "D":
            yield f"{path}: not regenerated"
        elif stable_lines(path.read_text(newline="")) != stable_lines(committed(path)):
            yield f"{path}: differs from the committed table"


def main(argv: list[str]) -> int:
    found = list(problems(Path(argv[0]) if argv else DEFAULT_DIR))
    for problem in found:
        print(problem)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
