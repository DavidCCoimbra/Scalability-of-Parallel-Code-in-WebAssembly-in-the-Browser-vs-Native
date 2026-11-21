import csv
import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from analysis.sensitivity import Analysis, IncompleteCheck, main, sensitivity_rows

HEADER = "question,environment,workload,input,k,threads,effect,low,high,primary,primary_low,primary_high,p,holm_p,rejected"
RQ1 = "RQ1,chrome,filter,noise,,8,{effect},0.96,1.02,yes,0.95,1.03,0.45,{holm},{rejected}"
EXPLORATORY = "RQ1,chrome,filter,noise,,4,0.98,0.97,0.99,exploratory,,,,,"


def table(directory: Path, name: str, effect: str, holm: str, rejected: str) -> Path:
    path = directory / f"{name}.csv"
    path.write_text("\n".join([HEADER, RQ1.format(effect=effect, holm=holm, rejected=rejected), EXPLORATORY]) + "\n")
    return path


class SensitivityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_only_primary_contrasts_are_compared(self) -> None:
        analysis = Analysis.read("primary", table(self.root, "p", "0.99", "0.9", "no"))
        self.assertEqual(list(analysis.contrasts), [("RQ1", "chrome", "filter", "noise", "", "8")])

    def test_a_decision_that_changes_under_a_check_is_not_robust(self) -> None:
        primary = table(self.root, "p", "0.99", "0.9", "no")
        same = table(self.root, "mean", "0.991", "0.75", "no")
        flipped = table(self.root, "median", "0.992", "0.018", "yes")
        output = self.root / "out.csv"
        code = main(["--primary", str(primary), "--check", f"mean={same}", "--check", f"median={flipped}", "--output", str(output)])
        self.assertEqual(code, 0)
        row = next(csv.DictReader(output.open()))
        self.assertEqual((row["primary_rejected"], row["mean_rejected"], row["median_rejected"], row["robust"]), ("no", "no", "yes", "no"))
        self.assertEqual((row["median_effect"], row["median_holm_p"]), ("0.992", "0.018"))

    def test_checks_that_agree_are_robust(self) -> None:
        primary = Analysis.read("primary", table(self.root, "p", "0.99", "0.9", "no"))
        check = Analysis.read("mean", table(self.root, "mean", "0.991", "0.75", "no"))
        self.assertEqual(sensitivity_rows(primary, [check])[0][-1], "yes")

    def test_a_check_without_the_primary_contrasts_is_refused(self) -> None:
        primary = table(self.root, "p", "0.99", "0.9", "no")
        empty = self.root / "empty.csv"
        empty.write_text(HEADER + "\n")
        with self.assertRaises(IncompleteCheck):
            sensitivity_rows(Analysis.read("primary", primary), [Analysis.read("mean", empty)])
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--primary", str(primary), "--check", f"mean={empty}", "--output", str(self.root / "o.csv")]), 1)


if __name__ == "__main__":
    unittest.main()
