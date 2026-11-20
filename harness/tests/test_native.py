import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from harness.context import sha256_file, validate
from harness.shield import scope_prefix
from harness.native import CSV_HEADER, NativeRun, NativeRunFailed, query_to_flags

BUILD = {"features": [], "rustc": "rustc x", "rustflags": "", "clockResolutionNs": 40}

FAKE_RUNNER = f"""
import json, sys
args = sys.argv[1:]
if args == ["--build-info"]:
    print(json.dumps({BUILD!r}))
    sys.exit(0)
print({CSV_HEADER!r})
print("native," + args[args.index("--workload") + 1] + "," + args[args.index("--threads") + 1])
"""


class QueryToFlagsTest(unittest.TestCase):
    def test_query_becomes_runner_flags(self) -> None:
        self.assertEqual(query_to_flags("workload=filter&threads=2"), ["--workload", "filter", "--threads", "2"])

    def test_passes_become_a_runner_flag(self) -> None:
        self.assertEqual(query_to_flags("workload=filter&passes=4"), ["--workload", "filter", "--passes", "4"])

    def test_query_cannot_set_run_or_environment(self) -> None:
        for query in ("env=chrome&threads=2", "run=x&threads=2"):
            with self.assertRaises(ValueError):
                query_to_flags(query)


class NativeRunTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.results = root / "results"
        self.runner = root / "runner.py"
        self.runner.write_text(FAKE_RUNNER)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def native(self, script: Path) -> NativeRun:
        return NativeRun([sys.executable, str(script)], self.results, cpus=None, order_seed=3, artifact=script, order_position=9)

    def test_writes_csv_and_context(self) -> None:
        self.native(self.runner).run("n1", "workload=filter&threads=2")
        self.assertEqual((self.results / "n1.csv").read_text(), f"{CSV_HEADER}\nnative,filter,2\n")
        meta = json.loads((self.results / "n1.json").read_text())
        self.assertEqual(validate(meta), [])
        self.assertEqual((meta["environment"], meta["browserVersion"], meta["orderSeed"]), ("native", "native", 3))
        self.assertIn("--workload", meta["launchFlags"])
        self.assertEqual(meta["build"], BUILD)
        self.assertEqual(meta["artifactSha256"], sha256_file(self.runner))
        self.assertEqual(meta["orderPosition"], 9)
        self.assertEqual(meta["passes"], 1)

    def test_context_records_the_passes_and_the_runner_gets_the_flag(self) -> None:
        self.native(self.runner).run("n7", "workload=filter&threads=2&passes=16")
        meta = json.loads((self.results / "n7.json").read_text())
        self.assertEqual(meta["passes"], 16)
        flags = meta["launchFlags"]
        self.assertEqual(flags[flags.index("--passes") + 1], "16")

    def test_context_records_the_grain_and_the_runner_gets_the_flag(self) -> None:
        self.native(self.runner).run("n8", "workload=filter&threads=2&grain=8")
        meta = json.loads((self.results / "n8.json").read_text())
        self.assertEqual(meta["grain"], 8)
        flags = meta["launchFlags"]
        self.assertEqual(flags[flags.index("--grain") + 1], "8")

    def test_failing_runner_records_the_error_with_context(self) -> None:
        failing = Path(self.tmp.name) / "failing.py"
        failing.write_text(
            "import json, sys\n"
            f"if sys.argv[1:] == ['--build-info']: print(json.dumps({BUILD!r})); sys.exit(0)\n"
            "sys.stderr.write('boom'); sys.exit(2)\n"
        )
        with self.assertRaises(NativeRunFailed) as error:
            self.native(failing).run("n2", "workload=filter&threads=2")
        self.assertIn("boom", str(error.exception))
        self.assertFalse((self.results / "n2.csv").exists())
        stored = json.loads((self.results / "n2.error.json").read_text())
        self.assertIn("boom", stored["error"])
        self.assertEqual(stored["environment"], "native")

    def test_output_that_is_not_the_csv_schema_is_rejected(self) -> None:
        chatty = Path(self.tmp.name) / "chatty.py"
        chatty.write_text("print('starting...'); print('env,workload')")
        with self.assertRaises(NativeRunFailed):
            self.native(chatty).run("n3", "workload=filter&threads=2")
        self.assertFalse((self.results / "n3.csv").exists())

    def test_hung_runner_times_out(self) -> None:
        hung = Path(self.tmp.name) / "hung.py"
        hung.write_text("import time; time.sleep(60)")
        native = NativeRun([sys.executable, str(hung)], self.results, cpus=None, order_seed=3, timeout=0.5)
        with self.assertRaises(NativeRunFailed):
            native.run("n4", "workload=filter&threads=2")

    def test_scope_wraps_taskset_in_a_systemd_scope_on_the_mask(self) -> None:
        native = NativeRun([sys.executable, str(self.runner)], self.results, cpus="0,2", order_seed=3, scope_user="david")
        argv = native.command("n1", "threads=1")
        prefix = scope_prefix("n1", "0,2", "david", os.environ)
        self.assertEqual(argv[: len(prefix)], prefix)
        self.assertEqual(argv[len(prefix) : len(prefix) + 3], ["taskset", "-c", "0,2"])

    def test_scope_without_a_mask_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            NativeRun([sys.executable, str(self.runner)], self.results, cpus=None, order_seed=3, scope_user="david")

    def test_context_records_the_runner_cpu_time(self) -> None:
        busy = Path(self.tmp.name) / "busy.py"
        busy.write_text(
            "import json, sys, time\n"
            f"if sys.argv[1:] == ['--build-info']: print(json.dumps({BUILD!r})); sys.exit(0)\n"
            "end = time.process_time() + 0.3\n"
            "while time.process_time() < end: pass\n"
            f"print({CSV_HEADER!r})\n"
        )
        self.native(busy).run("n5", "workload=filter&threads=2")
        meta = json.loads((self.results / "n5.json").read_text())
        self.assertGreaterEqual(meta["runCpuSeconds"], 0.25)
        self.assertEqual(meta["runCpuMethod"], "rusage")
        self.assertEqual(meta["startDelayMs"], 0)
        self.assertIn("shield", meta)

    def test_reused_run_id_is_refused_before_running(self) -> None:
        self.results.mkdir(parents=True, exist_ok=True)
        for leftover in ("n6.csv", "n6.json", "n6.error.json"):
            (self.results / leftover).write_text("old")
            with self.assertRaises(FileExistsError, msg=leftover):
                self.native(self.runner).run("n6", "workload=filter&threads=2")
            self.assertEqual((self.results / leftover).read_text(), "old")
            (self.results / leftover).unlink()

    def test_malformed_cpu_mask_is_rejected_up_front(self) -> None:
        with self.assertRaises(ValueError):
            NativeRun([sys.executable, str(self.runner)], self.results, cpus="0-7:2", order_seed=3)


class SchemaTest(unittest.TestCase):
    def test_header_matches_the_rust_schema(self) -> None:
        rust = (Path(__file__).resolve().parents[2] / "bench/src/results.rs").read_text()
        self.assertIn(f'"{CSV_HEADER}"', rust)


if __name__ == "__main__":
    unittest.main()
