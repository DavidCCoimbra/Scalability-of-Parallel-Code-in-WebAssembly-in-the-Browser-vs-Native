"""Check that every ADR in docs/adr has the required structure.

Usage: python3 scripts/check_adrs.py [DIR]   (default: docs/adr)
Exits 1 and prints one line per problem if any ADR is malformed.
"""

import re
import sys
from collections.abc import Iterator
from pathlib import Path

DEFAULT_DIR = Path("docs/adr")
ADR_GLOB = "[0-9][0-9][0-9][0-9]-*.md"
NUMBER_DIGITS = 4
REQUIRED_HEADINGS = ("## Context", "## Decision", "## Consequences", "## Status")
DATE_PREFIX = "Date: "
ADR_FILE = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")
TITLE = re.compile(r"^# ADR (\d{4}): .+$", re.MULTILINE)


def number_of(path: Path) -> str:
    return path.name[:NUMBER_DIGITS]


def title_problems(text: str, number: str) -> Iterator[str]:
    title = TITLE.search(text)
    if title is None:
        yield "missing title '# ADR NNNN: ...'"
    elif title.group(1) != number:
        yield f"title number {title.group(1)} does not match file number {number}"


def section_problems(lines: list[str]) -> Iterator[str]:
    if not any(line.startswith(DATE_PREFIX) for line in lines):
        yield "missing Date: line"
    for heading in REQUIRED_HEADINGS:
        if heading not in lines:
            yield f"missing {heading}"


def problems_in(path: Path) -> list[str]:
    if ADR_FILE.match(path.name) is None:
        return ["file name must be NNNN-lowercase-words.md"]
    text = path.read_text(encoding="utf-8")
    return [*title_problems(text, number_of(path)), *section_problems(text.splitlines())]


def main(argv: list[str]) -> int:
    adr_dir = Path(argv[0]) if argv else DEFAULT_DIR
    failed = False
    seen: dict[str, str] = {}
    for path in sorted(adr_dir.glob(ADR_GLOB)):
        number = number_of(path)
        if number in seen:
            print(f"{path.name}: duplicate number {number} (also {seen[number]})")
            failed = True
        seen[number] = path.name
        for problem in problems_in(path):
            print(f"{path.name}: {problem}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
