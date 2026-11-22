import unittest

from scripts.kernel_code import native_loop, wasm_loop

NATIVE = """0000000000001000 <kernel>:
    1000:\tmovzbl (%r8),%r10d
    1004:\tlock incq (%rsi,%r10,1)
    1009:\tdec    %r9
    100c:\tjne    1000 <kernel>
    100e:\tmovzbl (%r8),%r9d
    1012:\tlock incq (%rsi,%r9,1)
    1017:\tmovzbl 0x1(%r8),%r9d
    101c:\tlock incq (%rsi,%r9,1)
    1021:\tcmp    %rdx,%r8
    1024:\tjne    100e <kernel+0xe>
    1026:\tjmp    1000 <kernel>
"""

RETRY = """0000000000000000 <kernel>:
   0:\tmovzbl (%rdi,%rsi,1),%r8d
   4:\tmov    (%rdi,%r8,1),%rax
   8:\tlock cmpxchg %rcx,(%rdi,%r8,1)
   e:\tjne    0x4
  10:\tcmp    %rdx,%rsi
  13:\tjne    0x0
"""

WASM = """000100 func[1] <kernel>:
 000101: 03 40 | loop
 000103: 20 00 |   local.get 0
 000105: fe 1e | i64.atomic.rmw.add 3 0
 000107: 0d 00 |   br_if 0
 000109: 0b    | end
 00010a: 03 40 | loop
 00010c: 2d 00 |   i32.load8_u 0 0
 00010e: fe 1e |   i64.atomic.rmw.add 3 0
 000110: 2d 00 |   i32.load8_u 0 1
 000112: fe 1e |   i64.atomic.rmw.add 3 0
 000114: 0d 00 |   br_if 0
 000116: 0b    | end
"""


class KernelCodeTest(unittest.TestCase):
    def test_the_unrolled_loop_is_chosen_over_the_remainder_loop_and_the_loop_around_both(self) -> None:
        loop = native_loop(NATIVE, "lock", "movzb")
        self.assertEqual(len(loop), 6)
        self.assertEqual(sum("lock" in line for line in loop), 2)

    def test_a_retry_loop_that_reads_no_pixel_is_not_the_kernel_loop(self) -> None:
        loop = native_loop(RETRY, "lock", "movzb")
        self.assertEqual(loop[0].split()[0], "movzbl")
        self.assertEqual(len(loop), 6)

    def test_a_function_without_the_marker_has_no_loop(self) -> None:
        self.assertEqual(native_loop(NATIVE, "vpaddw"), [])

    def test_the_wasm_loop_is_the_loop_block_that_reads_pixels(self) -> None:
        loop = wasm_loop(WASM, "i64.atomic.rmw.add", "i32.load8_u")
        self.assertEqual(sum("i64.atomic.rmw.add" in line for line in loop), 2)
        self.assertEqual(loop[0].strip(), "loop")


if __name__ == "__main__":
    unittest.main()
