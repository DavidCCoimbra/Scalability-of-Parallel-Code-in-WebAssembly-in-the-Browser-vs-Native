import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts import check_simd

OBJDUMP_VECTOR = """
0000000000012300 <bench::workloads::gaussian::blur_interior>:
   12300:\tpush   %rbp
   12301:\tmovdqu (%rdi,%rax,1),%xmm0
   12306:\tpaddw  %xmm1,%xmm0
   1230a:\tret

0000000000012310 <other>:
   12310:\tmovdqu (%rdi),%xmm0
"""

OBJDUMP_SCALAR = """
0000000000012300 <bench::workloads::gaussian::blur_interior>:
   12300:\tpxor   %xmm0,%xmm0
   12304:\tmovzbl (%rax),%r9d
   12308:\tret

0000000000012310 <other>:
   12310:\tmovdqu (%rdi),%xmm0
"""

WASM_VECTOR = """_ZN5bench9workloads8gaussian13blur_interior17h0E:
\t.functype\t_ZN5bench9workloads8gaussian13blur_interior17h0E (i32, i32) -> ()
\tv128.load\t0:p2align=0
\ti16x8.extend_low_i8x16_u
\ti16x8.add
\tend_function
other:
\tv128.load\t0
"""

WASM_OBJDUMP_VECTOR = """
000abc func[12] <_RNvNtNtCs1_5bench9workloads8gaussian13blur_interior>:
 000abd: 01 7f                      | local[0] type=i32
 000ac1: fd 00 00 00                | v128.load 0 0
 000ac5: fd 8e 01                   | i16x8.add
 000ac8: 0b                         | end
000ad0 func[13] <other>:
 000ad1: fd 8e 01                   | i16x8.add
"""


def run(text: str, arch: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, "code.txt")
        path.write_text(text)
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_simd.main([str(path), arch])
        return code, out.getvalue()


class CheckSimdTest(unittest.TestCase):
    def test_vectorized_x86_function_passes(self) -> None:
        code, out = run(OBJDUMP_VECTOR, "x86_64")
        self.assertEqual(code, 0)
        self.assertIn("blur_interior: 1 packed 16-bit instructions", out)

    def test_scalar_x86_function_fails(self) -> None:
        code, out = run(OBJDUMP_SCALAR, "x86_64")
        self.assertEqual(code, 1)
        self.assertIn("blur_interior: 0 packed 16-bit instructions", out)

    def test_vectorized_wasm_function_passes(self) -> None:
        code, out = run(WASM_VECTOR, "wasm32")
        self.assertEqual(code, 0)
        self.assertIn("blur_interior: 2 packed 16-bit instructions", out)

    def test_vectorized_wasm_objdump_function_passes(self) -> None:
        code, out = run(WASM_OBJDUMP_VECTOR, "wasm32")
        self.assertEqual(code, 0)
        self.assertIn("blur_interior: 1 packed 16-bit instructions", out)

    def test_lone_v128_load_is_not_enough(self) -> None:
        code, _ = run(WASM_VECTOR.replace("\ti16x8.extend_low_i8x16_u\n\ti16x8.add\n", ""), "wasm32")
        self.assertEqual(code, 1)

    def test_missing_function_fails(self) -> None:
        code, out = run("other:\n\tv128.load 0\n", "wasm32")
        self.assertEqual(code, 1)
        self.assertIn("blur_interior not found", out)


if __name__ == "__main__":
    unittest.main()
