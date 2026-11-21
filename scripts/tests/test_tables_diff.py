import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import tables_diff

SIDECAR = '{\n  "seed": 7,\n  "commit": "%s",\n  "createdAt": "%s"\n}\n'


class TablesDiffTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.previous = Path.cwd()
        os.chdir(self.tmp.name)
        self.tables = Path("data/tables")
        self.tables.mkdir(parents=True)
        (self.tables / "a.csv").write_text("x,y\n1,2\n")
        (self.tables / "a.json").write_text(SIDECAR % ("abc", "t0"))
        for command in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "tables"]):
            subprocess.run(["git", *command], check=True)

    def tearDown(self) -> None:
        os.chdir(self.previous)
        self.tmp.cleanup()

    def problems(self) -> list[str]:
        return list(tables_diff.problems(self.tables))

    def test_unchanged_tables_pass(self) -> None:
        self.assertEqual(self.problems(), [])

    def test_a_new_commit_and_time_stamp_in_a_sidecar_are_ignored(self) -> None:
        (self.tables / "a.json").write_text(SIDECAR % ("def", "t1"))
        self.assertEqual(self.problems(), [])

    def test_another_value_in_a_sidecar_is_a_difference(self) -> None:
        (self.tables / "a.json").write_text((SIDECAR % ("abc", "t0")).replace('"seed": 7', '"seed": 8'))
        self.assertEqual(self.problems(), ["data/tables/a.json: differs from the committed table"])

    def test_a_changed_number_in_a_table_is_a_difference(self) -> None:
        (self.tables / "a.csv").write_text("x,y\n1,3\n")
        self.assertEqual(self.problems(), ["data/tables/a.csv: differs from the committed table"])

    def test_another_line_ending_is_a_difference(self) -> None:
        (self.tables / "a.csv").write_bytes(b"x,y\r\n1,2\r\n")
        self.assertEqual(self.problems(), ["data/tables/a.csv: differs from the committed table"])

    def test_a_table_that_is_new_or_was_not_regenerated_is_reported(self) -> None:
        (self.tables / "b.csv").write_text("z\n")
        (self.tables / "a.csv").unlink()
        self.assertEqual(sorted(self.problems()), ["data/tables/a.csv: not regenerated", "data/tables/b.csv: not committed"])


if __name__ == "__main__":
    unittest.main()
