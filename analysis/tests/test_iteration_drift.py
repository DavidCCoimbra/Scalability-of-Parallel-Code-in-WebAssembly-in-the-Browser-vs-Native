import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from analysis.quality.iteration_drift import COLUMNS, drifts, write_drifts
from harness.native import CSV_HEADER


def write_run(root: Path, run_id: str, position: int, times: list[int]) -> None:
    rows = ["native,filter,noise,,64,64,24301,2,warmup,0,999,0x01,0xab"]
    rows += [f"native,filter,noise,,64,64,24301,2,measured,{i},{ns},0x01,0xab" for i, ns in enumerate(times)]
    (root / f"{run_id}.csv").write_text(CSV_HEADER + "\n" + "\n".join(rows) + "\n")
    (root / f"{run_id}.json").write_text(json.dumps({"orderPosition": position}))


class IterationDriftTest(unittest.TestCase):
    def test_first_iterations_are_compared_with_the_last_pooled_over_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "c-0000", 0, [120, 120, 100, 100, 100, 100])
            write_run(root, "c-0001", 1, [120, 120, 100, 100, 100, 100])
            output = io.StringIO()
            write_drifts(drifts(root, window=2), output)
        rows = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(list(rows[0]), list(COLUMNS))
        self.assertEqual((rows[0]["runs"], rows[0]["first_over_last"]), ("2", "1.200"))

    def test_warmup_iterations_are_not_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_run(root, "c-0000", 0, [100, 100, 100, 100])
            (drift,) = drifts(root, window=2)
        self.assertEqual(drift.first_over_last, 1.0)


if __name__ == "__main__":
    unittest.main()
