import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts import check_adrs

VALID = """# ADR {num}: Example decision

Date: 2026-10-17

## Context

Why.

## Decision

What.

## Consequences

So what.

## Status

Accepted
"""


def run(files: dict[str, str]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        for name, text in files.items():
            Path(tmp, name).write_text(text)
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_adrs.main([tmp])
        return code, out.getvalue()


class CheckAdrsTest(unittest.TestCase):
    def test_valid_adr_passes(self) -> None:
        code, _ = run({"0001-example.md": VALID.format(num="0001")})
        self.assertEqual(code, 0)

    def test_missing_consequences_fails(self) -> None:
        text = VALID.format(num="0001").replace("## Consequences\n\nSo what.\n\n", "")
        code, out = run({"0001-example.md": text})
        self.assertEqual(code, 1)
        self.assertIn("missing ## Consequences", out)

    def test_number_mismatch_fails(self) -> None:
        code, out = run({"0002-example.md": VALID.format(num="0003")})
        self.assertEqual(code, 1)
        self.assertIn("0002-example.md", out)

    def test_duplicate_number_fails(self) -> None:
        code, out = run({
            "0011-first.md": VALID.format(num="0011"),
            "0011-second.md": VALID.format(num="0011"),
        })
        self.assertEqual(code, 1)
        self.assertIn("duplicate number 0011", out)


if __name__ == "__main__":
    unittest.main()
