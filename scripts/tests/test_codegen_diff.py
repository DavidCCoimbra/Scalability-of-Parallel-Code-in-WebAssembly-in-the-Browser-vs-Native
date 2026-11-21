import io
import unittest
from contextlib import redirect_stdout

from scripts.codegen_diff import (
    Instruction,
    NativeListing,
    WasmFunction,
    is_hot,
    normalize_native,
    pairing_name,
    report,
    unmatched_patterns,
    wasm_extra,
)

RUN = "<bench::AtomicHistogram as bench::Workload>::run"


def wasm(*code: str) -> WasmFunction:
    return WasmFunction(list(code), None, {})


def compare(base: dict[str, WasmFunction], head: dict[str, WasmFunction]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output):
        code = report(base, head, wasm_extra)
    return code, output.getvalue()


class NamesTest(unittest.TestCase):
    def test_a_moved_item_keeps_its_pairing_name(self) -> None:
        moved = "<bench::workloads::histogram::extras::private::PrivateAtomicHistogram as bench::workloads::workload::Workload>::run"
        self.assertEqual(pairing_name(moved), "<bench::PrivateAtomicHistogram as bench::Workload>::run")

    def test_the_crate_hash_is_dropped(self) -> None:
        self.assertEqual(pairing_name("bench[0123456789abcdef]::run"), "bench::run")

    def test_kernels_and_the_run_entry_are_hot_and_helpers_are_not(self) -> None:
        for name in (RUN, "bench::blur_interior", "bench::local_counts", "bench::run", "native::run"):
            self.assertTrue(is_hot(name), name)
        for name in ("<bench::Options>::input", "core::fmt::write", "bench::run_config"):
            self.assertFalse(is_hot(name), name)

    def test_a_pattern_that_names_no_function_is_listed(self) -> None:
        unmatched = unmatched_patterns([RUN, "bench::blur_interior"])
        self.assertIn(r"bench::measure", unmatched)
        self.assertNotIn(r"Workload>::run", unmatched)


class NativeNormalizationTest(unittest.TestCase):
    def test_addresses_and_data_offsets_do_not_count_as_differences(self) -> None:
        listing = NativeListing("f", 0x1000, [Instruction(0x1000, "nop")])
        self.assertEqual(normalize_native("jne    1040 <f+0x40>", listing), "jne .+0x40")
        self.assertEqual(normalize_native("mov    0x2f1(%rip),%rax        # 3000 <x>", listing), "mov DATA(%rip),%rax")
        self.assertEqual(normalize_native("call   9000 <bench::input::noise>", listing), "call bench::noise")


class ReportTest(unittest.TestCase):
    def test_identical_hot_functions_pass(self) -> None:
        code, output = compare({RUN: wasm("i32.add")}, {RUN: wasm("i32.add")})
        self.assertEqual(code, 0)
        self.assertIn("HOT identical", output)

    def test_a_hot_function_that_differs_fails(self) -> None:
        code, output = compare({RUN: wasm("i32.add")}, {RUN: wasm("i32.sub")})
        self.assertEqual(code, 1)
        self.assertIn("HOT differs", output)

    def test_a_hot_function_missing_on_one_side_fails(self) -> None:
        self.assertEqual(compare({RUN: wasm("i32.add")}, {})[0], 1)

    def test_a_cold_function_that_differs_is_listed_and_passes(self) -> None:
        both = {RUN: wasm("i32.add")}
        code, output = compare({**both, "core::fmt::write": wasm("a")}, {**both, "core::fmt::write": wasm("b")})
        self.assertEqual(code, 0)
        self.assertIn("differs      core::fmt::write", output)

    def test_the_fold_of_the_local_histogram_is_hot(self) -> None:
        name = "bench::local_counts::<rayon::iter::len::MaxLen<rayon::slice::chunks::Chunks<u8>>>::{closure#0}"
        self.assertEqual(compare({name: wasm("i64.add")}, {name: wasm("i64.sub")})[0], 1)

    def test_inlined_hot_items_are_reported_per_side(self) -> None:
        code, output = compare({RUN: wasm("i32.add")}, {RUN: wasm("i32.add")})
        self.assertEqual(code, 0)
        self.assertIn("hot pattern without a function in base (inlined or renamed): bench::measure", output)
        self.assertIn("hot pattern without a function in head (inlined or renamed): bench::measure", output)


if __name__ == "__main__":
    unittest.main()
