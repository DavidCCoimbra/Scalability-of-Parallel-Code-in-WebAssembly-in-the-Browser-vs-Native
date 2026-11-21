import subprocess
import tempfile
import unittest
from pathlib import Path

from harness.context import git_commit

GENERATED = ("data/tables",)


def git(repository: Path, *arguments: str) -> None:
    identity = ["-c", "user.name=test", "-c", "user.email=test@example.org", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "-C", str(repository), *identity, *arguments], check=True, capture_output=True)


class GeneratedFilesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "data/tables").mkdir(parents=True)
        (self.root / "data/tables/table.csv").write_text("a\n")
        (self.root / "code.py").write_text("x = 1\n")
        git(self.root, "init", "-q")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "initial")

    def test_a_regenerated_table_does_not_make_the_commit_dirty(self) -> None:
        (self.root / "data/tables/table.csv").write_text("b\n")
        self.assertFalse(git_commit(self.root, GENERATED).endswith("-dirty"))
        self.assertTrue(git_commit(self.root).endswith("-dirty"))

    def test_changed_code_still_makes_the_commit_dirty(self) -> None:
        (self.root / "code.py").write_text("x = 2\n")
        self.assertTrue(git_commit(self.root, GENERATED).endswith("-dirty"))


if __name__ == "__main__":
    unittest.main()
