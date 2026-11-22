"""The code V8 compiled for each kernel, from the dumps of capture_chrome.py.

Usage: python3 -m scripts.chrome_code DUMPS_DIR OUTPUT_DIR
Writes OUTPUT_DIR/<kernel>/chrome-<compiler>.s, the whole function as objdump prints its bytes,
and chrome-<compiler>-loop.s, the loop that kernel_code.py would choose in it.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from analysis.extras.jitdump import CompiledCode, compiled_code
from scripts.kernel_code import KERNELS, SKIPPED, Kernel, native_loop

# The run that holds each kernel, and the compiler V8 names at the end of a function's name.
CELL = {"blur-interior": "filter", "atomic-loop": "hist-atomic", "local-loop": "hist-local", "sequential-histogram": "hist-seq", "sequential-filter": "filter-seq"}
COMPILERS = {"optimizing": "turbofan", "baseline": "liftoff"}
# V8 uses other instructions than LLVM for the two histograms' increments.
MARKERS = {"atomic-loop": "lock", "local-loop": r"(inc|add)\w*\s.*\(|mov\s+%\w+,.*\(", "sequential-histogram": r"(inc|add)\w*\s.*\(|mov\s+%\w+,.*\("}


def function(folder: Path, kernel: Kernel, compiler: str) -> CompiledCode:
    found = [
        code
        for dump in sorted(folder.glob("jit-*.dump"))
        for code in compiled_code(dump.read_bytes())
        if code.name.endswith(f"-{compiler}") and all(word.rstrip(">") in code.name for word in kernel.native) and not any(s in code.name for s in SKIPPED)
    ]
    if not found:
        raise SystemExit(f"no {compiler} code for {kernel.name} in {folder}")
    # A function compiled more than once in a run: the last is the one left running.
    return found[-1]


def disassembly(code: CompiledCode) -> str:
    with tempfile.NamedTemporaryFile(suffix=".bin") as file:
        file.write(code.code)
        file.flush()
        listing = subprocess.run(["objdump", "-D", "-b", "binary", "-m", "i386:x86-64", "--no-show-raw-insn", file.name], capture_output=True, text=True, check=True).stdout
    body = listing.split("<.data>:\n", 1)[1]
    return f"{0:016x} <{code.name}>:\n{body}"


def main(argv: list[str]) -> int:
    dumps, output = Path(argv[0]), Path(argv[1])
    for kernel in KERNELS:
        for tier, compiler in COMPILERS.items():
            code = function(dumps / tier / CELL[kernel.name], kernel, compiler)
            listing = disassembly(code)
            loop = native_loop(listing, MARKERS.get(kernel.name, kernel.native_marker), kernel.native_anchor)
            folder = output / kernel.name
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"chrome-{tier}.s").write_text(listing.rstrip() + "\n")
            (folder / f"chrome-{tier}-loop.s").write_text("\n".join(loop) + "\n")
            print(f"{kernel.name:22} {tier:10} {len(code.code):5d} bytes, loop of {len(loop)} instructions")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
