import math
import re
import tempfile
import unittest
from pathlib import Path

from harness.browser_check import CASES, HEIGHT, THREAD_COUNTS, WIDTH, Mismatch, RunIdentity, compare, failed_label, read_identity
from harness.browser_check.identity import found_identity
from harness.launcher import ChromeCommand, RunStatus

HEADER = "env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum"


class ReadChecksumTest(unittest.TestCase):
    def write(self, text: str) -> Path:
        path = Path(self.tmp.name) / "r.csv"
        path.write_text(text)
        return path

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_reads_the_single_checksum_of_a_run(self) -> None:
        csv = f"{HEADER}\nnative,filter,noise,,8,8,1,2,measured,0,5,0x01,0xab\nnative,filter,noise,,8,8,1,2,measured,1,6,0x01,0xab\n"
        self.assertEqual(read_identity(self.write(csv)), RunIdentity("0x01", "0xab"))

    def test_inconsistent_checksums_in_one_run_are_an_error(self) -> None:
        csv = f"{HEADER}\nnative,filter,noise,,8,8,1,2,measured,0,5,0x01,0xab\nnative,filter,noise,,8,8,1,2,measured,1,6,0x01,0xcd\n"
        with self.assertRaises(ValueError):
            read_identity(self.write(csv))


    def test_inconsistent_input_fingerprints_in_one_run_are_an_error(self) -> None:
        csv = f"{HEADER}\nchrome,filter,noise,,8,8,1,2,measured,0,5,0x01,0xab\nchrome,filter,noise,,8,8,1,2,measured,1,5,0x02,0xab\n"
        with self.assertRaises(ValueError):
            read_identity(self.write(csv))


class FoundIdentityTest(unittest.TestCase):
    def test_an_unreadable_browser_csv_is_a_label_not_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = found_identity(Path(tmp) / "absent.csv")
            inconsistent = Path(tmp) / "run.csv"
            inconsistent.write_text("input_fingerprint,checksum\n0x01,0xab\n0x01,0xcd\n")
            self.assertTrue(isinstance(missing, str) and missing.startswith("<unreadable"))
            self.assertIn("expected one checksum", str(found_identity(inconsistent)))


class CompareTest(unittest.TestCase):
    def test_equal_runs_have_no_mismatch(self) -> None:
        same = RunIdentity("0x01", "0xab")
        self.assertEqual(compare({"filter noise": same}, {"chrome": {"filter noise": same}}), [])

    def test_input_and_output_mismatches_are_reported_separately(self) -> None:
        native = {"filter noise": RunIdentity("0x01", "0xab"), "hist-local few": RunIdentity("0x02", "0xcd")}
        browsers = {
            "firefox": {
                "filter noise": RunIdentity("0x09", "0xab"),
                "hist-local few": RunIdentity("0x02", "0xee"),
            }
        }
        self.assertEqual(
            compare(native, browsers),
            [
                Mismatch("firefox", "filter noise", "input_fingerprint", "0x01", "0x09"),
                Mismatch("firefox", "hist-local few", "checksum", "0xcd", "0xee"),
            ],
        )

    def test_failed_or_missing_runs_are_mismatches_of_the_whole_run(self) -> None:
        native = {"filter noise": RunIdentity("0x01", "0xab"), "hist-local few": RunIdentity("0x02", "0xcd")}
        browsers = {"chrome": {"filter noise": "<timeout>"}}
        self.assertEqual(
            compare(native, browsers),
            [
                Mismatch("chrome", "filter noise", "run", "0x01/0xab", "<timeout>"),
                Mismatch("chrome", "hist-local few", "run", "0x02/0xcd", None),
            ],
        )


class CasesTest(unittest.TestCase):
    def test_filter_and_sort_on_noise_and_histograms_on_every_k_for_each_thread_count(self) -> None:
        names = {case.name for case in CASES}
        self.assertEqual(len(names), 62)
        self.assertIn("filter-seq noise N=1", names)
        self.assertNotIn("filter-seq noise N=2", names)
        self.assertTrue(all(f"hist-seq k={k} N=1" in names for k in (1, 4, 16, 256)))
        for threads in (1, 2, 4):
            self.assertIn(f"filter noise N={threads}", names)
            self.assertIn(f"sort noise N={threads}", names)
            for workload in ("hist-atomic", "hist-local", "hist-atomic-private", "hist-atomic-packed"):
                for k in (1, 4, 16, 256):
                    self.assertIn(f"{workload} k={k} N={threads}", names)

    def test_cases_exercise_warmup_and_several_iterations(self) -> None:
        self.assertTrue(all("warmup=1" in case.query and "iters=2" in case.query for case in CASES))


class ConcurrencyTest(unittest.TestCase):
    def test_histograms_get_more_chunks_than_the_largest_thread_count(self) -> None:
        rust = (Path(__file__).resolve().parents[2] / "bench/src/workloads/histogram/mod.rs").read_text()
        match = re.search(r"pub const CHUNK_BYTES: usize = ([0-9_ *]+);", rust)
        assert match is not None
        factors = match.group(1)
        chunk_bytes = math.prod(int(factor.replace("_", "")) for factor in factors.split("*"))
        self.assertGreater(WIDTH * HEIGHT // chunk_bytes, max(THREAD_COUNTS))


class OutcomeLabelTest(unittest.TestCase):
    def test_failed_launches_keep_their_status(self) -> None:
        self.assertEqual(failed_label(RunStatus.TIMEOUT), "<timeout>")


class ChromeExtraFlagsTest(unittest.TestCase):
    def test_extra_flags_are_added_before_the_url(self) -> None:
        argv = ChromeCommand(extra_flags=("--no-sandbox",)).argv(Path("c"), Path("p"), "http://u", headless=True)
        self.assertIn("--no-sandbox", argv)
        self.assertEqual(argv[-1], "http://u")


if __name__ == "__main__":
    unittest.main()
