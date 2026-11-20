import csv
import json
import tempfile
from datetime import datetime, timezone
import unittest
from pathlib import Path

from analysis.extras.perf_counters import counters_of, main, read_intervals, read_runs

HEADER = "env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum,probe,passes"
START = 1_000_000.0


def iso(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def write_run(raw: Path, run_id: str, started: float, finished: float, timed_iterations: int) -> None:
    rows = ["native,hist-atomic,few,256,10,10,1,8,calibration-warm,0,5,0x1,0x2,broadcast,1"]
    rows += [f"native,hist-atomic,few,256,10,10,1,8,warmup,{i},5,0x1,0x2,,1" for i in range(timed_iterations)]
    (raw / f"{run_id}.csv").write_text(HEADER + "\n" + "\n".join(rows) + "\n")
    (raw / f"{run_id}.json").write_text(json.dumps({"startedAt": iso(started), "finishedAt": iso(finished)}))


def write_segment(counters: Path, rows: list[tuple[float, int]]) -> None:
    counters.mkdir()
    lines = ["# started on a test day", ""]
    for seconds, lock_loads in rows:
        lines.append(f"{seconds:.6f},{lock_loads},,cpu_core/mem_inst_retired.lock_loads/,1,100.00,,")
        lines.append(f"{seconds:.6f},7,,cpu_core/cycles/,1,100.00,,")
    (counters / "seg.csv").write_text("\n".join(lines) + "\n")
    (counters / "seg.start").write_text(f"{START}\n")


class PerfCountersTest(unittest.TestCase):
    def test_intervals_inside_a_run_window_are_divided_by_its_operations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            write_run(raw, "perf-v2-0000-native-hist-atomic-k256-n8-r0", START + 0.05, START + 0.25, 2)
            write_segment(raw / "counters", [(0.1, 100), (0.2, 300), (0.3, 999)])
            [run] = list(read_runs(raw))
            result = counters_of(run, read_intervals(raw / "counters"))
        self.assertEqual(run.operations, 200)
        self.assertEqual(result.intervals, 2)
        self.assertAlmostEqual(result.per_operation["lock_loads"], 2.0)
        self.assertAlmostEqual(result.per_operation["read_hitm"], 0.0)

    def test_a_run_without_intervals_fails_the_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            write_run(raw, "perf-v2-0000-native-hist-atomic-k256-n8-r0", START + 50, START + 60, 1)
            write_segment(raw / "counters", [(0.1, 100)])
            status = main([str(raw), "--runs", str(raw / "runs.csv"), "--summary", str(raw / "summary.csv")])
        self.assertEqual(status, 1)

    def test_summary_has_one_row_per_counter_and_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            write_run(raw, "perf-v2-0000-native-hist-atomic-k256-n8-r0", START + 0.05, START + 0.15, 1)
            write_run(raw, "perf-v2-0001-native-hist-atomic-k256-n8-r1", START + 0.15, START + 0.25, 1)
            write_segment(raw / "counters", [(0.1, 100), (0.2, 300)])
            self.assertEqual(main([str(raw), "--runs", str(raw / "runs.csv"), "--summary", str(raw / "summary.csv")]), 0)
            with (raw / "summary.csv").open(newline="") as file:
                rows = [row for row in csv.DictReader(file) if row["counter"] == "lock_loads"]
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["runs"], rows[0]["mean"]), ("2", "2.0000"))

    def test_retries_are_the_lock_loads_above_one_thread(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            write_run(raw, "perf-v2-0000-chrome-hist-atomic-k1-n1-r0", START + 0.05, START + 0.15, 1)
            write_run(raw, "perf-v2-0001-chrome-hist-atomic-k1-n8-r0", START + 0.15, START + 0.25, 1)
            write_segment(raw / "counters", [(0.1, 100), (0.2, 125)])
            arguments = ["--runs", str(raw / "runs.csv"), "--summary", str(raw / "summary.csv")]
            self.assertEqual(main([str(raw), *arguments, "--retries", str(raw / "retries.csv")]), 0)
            with (raw / "retries.csv").open(newline="") as file:
                [row] = list(csv.DictReader(file))
        self.assertEqual((row["environment"], row["k"], row["threads"]), ("chrome", "1", "8"))
        self.assertEqual(row["excess_lock_loads"], "0.2500")

    def test_a_multiplexed_event_stops_the_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            counters = Path(tmp) / "counters"
            counters.mkdir()
            (counters / "seg.csv").write_text("0.100000,5,,cpu_core/cycles/,1,50.00,,\n")
            (counters / "seg.start").write_text(f"{START}\n")
            with self.assertRaises(ValueError):
                read_intervals(counters)

    def test_a_configuration_short_of_its_planned_runs_fails_the_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            write_run(raw, "perf-v2-0000-native-hist-atomic-k256-n8-r0", START + 0.05, START + 0.15, 1)
            write_segment(raw / "counters", [(0.1, 100)])
            (raw / "campaign.json").write_text(json.dumps({"spec": {"repetitions": 2}}))
            status = main([str(raw), "--runs", str(raw / "runs.csv"), "--summary", str(raw / "summary.csv")])
        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
