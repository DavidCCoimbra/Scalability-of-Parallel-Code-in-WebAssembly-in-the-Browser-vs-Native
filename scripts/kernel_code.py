"""The machine code of the study's kernels, from a native binary and a WASM module.

Usage: python3 -m scripts.kernel_code --native BINARY --wasm MODULE.wasm --output DIR
Writes, per kernel, DIR/<kernel>/native.s and DIR/<kernel>/wasm.wat: the whole function that
holds the kernel, as objdump and wasm-objdump print it, with addresses kept. The innermost loop
that contains the kernel's marker instruction is written next to it as native-loop.s and
wasm-loop.wat, and DIR/summary.csv counts the instructions of each loop.
"""

import argparse
import csv
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

NATIVE_FUNCTION = re.compile(r"\n(?=[0-9a-f]{16} <)")
WASM_FUNCTION = re.compile(r"\n(?=[0-9a-f]+ func\[)")
NATIVE_LINE = re.compile(r"^\s*([0-9a-f]+):\s+(.*)$")
JUMP = re.compile(r"^j\w+\s+(?:0x)?([0-9a-f]+)\b")
SKIPPED = ("join", "StackJob", "call_b", "in_worker")


@dataclass(frozen=True)
class Kernel:
    name: str
    # Every word must be in the demangled native name of the function.
    native: tuple[str, ...]
    # Every word must be in the name the WASM name section keeps.
    wasm: tuple[str, ...]
    native_marker: str
    wasm_marker: str
    # What a turn of the kernel's loop also has, so that a loop inside one step of the work (V8's
    # retry of one atomic add) is not taken for the loop over the pixels.
    native_anchor: str = ""
    wasm_anchor: str = ""


KERNELS = (
    Kernel("blur-interior", ("gaussian::blur_interior",), ("gaussian::blur_interior",), "pmaddwd|paddw|pmullw|punpck", "i16x8"),
    Kernel("atomic-loop", ("helper", "atomic::AtomicHistogram"), ("helper", "atomic::AtomicHistogram"), "lock", "i64.atomic.rmw.add", "movzb", "i32.load8_u"),
    Kernel("local-loop", ("helper", "local::local_counts"), ("helper", "local::local_counts"), r"(incq|addq\s+\$0x1,)\s*.*\(", "i64.store", "movzb", "i32.load8_u"),
    Kernel("sequential-histogram", ("SequentialHistogram", "::run>"), ("SequentialHistogram", "::run>"), r"(incq|addq\s+\$0x1,)\s*.*\(", "i64.store", "movzb", "i32.load8_u"),
    Kernel("sequential-filter", ("SequentialBlur", "::run>"), ("SequentialBlur", "::run>"), "call", "call"),
)


def run(*command: str) -> str:
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout


def find(functions: list[str], words: tuple[str, ...]) -> str:
    found = [f for f in functions if all(word in f.split("\n", 1)[0] for word in words) and not any(s in f.split("\n", 1)[0] for s in SKIPPED)]
    if len(found) != 1:
        raise SystemExit(f"{len(found)} functions match {words}")
    return found[0]


# The loop to show: among the loops that hold no other loop with the kernel's marker (the
# innermost ones), the one with the most marker instructions per turn. That is the unrolled main
# loop, not the remainder loop next to it nor the loop over tasks around both.
def chosen(loops: list[tuple[int, int]], lines: list[str], has_marker: Callable[[str], bool], anchor: str = "") -> list[str]:
    marked = [
        (start, end)
        for start, end in loops
        if any(has_marker(line) for line in lines[start : end + 1]) and any(anchor in line for line in lines[start : end + 1])
    ]
    innermost = [(start, end) for start, end in marked if not any((s, e) != (start, end) and start <= s and e <= end for s, e in marked)]
    if not innermost:
        return []
    start, end = max(innermost, key=lambda span: sum(has_marker(line) for line in lines[span[0] : span[1] + 1]))
    return lines[start : end + 1]


# A loop: from a backward jump's target to the jump.
def native_loop(function: str, marker: str, anchor: str = "") -> list[str]:
    parsed = [(int(m.group(1), 16), m.group(2).strip()) for m in map(NATIVE_LINE.match, function.split("\n")[1:]) if m]
    index = {address: position for position, (address, _) in enumerate(parsed)}
    loops = []
    for position, (address, text) in enumerate(parsed):
        jump = JUMP.match(text)
        if jump is not None and int(jump.group(1), 16) in index and int(jump.group(1), 16) <= address:
            loops.append((index[int(jump.group(1), 16)], position))
    return chosen(loops, [text for _, text in parsed], lambda line: re.search(marker, line) is not None, anchor)


# A loop: a `loop` block to its `end`.
def wasm_loop(function: str, marker: str, anchor: str = "") -> list[str]:
    lines = [line.split("|", 1)[1].rstrip() for line in function.split("\n")[1:] if "|" in line]
    stack: list[int] = []
    loops = []
    for position, line in enumerate(lines):
        word = line.split()[0] if line.split() else ""
        if word in ("block", "loop", "if"):
            stack.append(position if word == "loop" else -1)
        elif word == "end" and stack:
            start = stack.pop()
            if start >= 0:
                loops.append((start, position))
    return chosen(loops, lines, lambda line: marker in line, anchor)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--wasm", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    native = NATIVE_FUNCTION.split(run("objdump", "-d", "-C", "--no-show-raw-insn", str(args.native)))
    wasm = WASM_FUNCTION.split(run("wasm-objdump", "-d", str(args.wasm)))
    summary = []
    for kernel in KERNELS:
        folder = args.output / kernel.name
        folder.mkdir(parents=True, exist_ok=True)
        native_function, wasm_function = find(native, kernel.native), find(wasm, kernel.wasm)
        loops = (
            native_loop(native_function, kernel.native_marker, kernel.native_anchor),
            wasm_loop(wasm_function, kernel.wasm_marker, kernel.wasm_anchor),
        )
        (folder / "native.s").write_text(native_function.rstrip() + "\n")
        (folder / "wasm.wat").write_text(wasm_function.rstrip() + "\n")
        (folder / "native-loop.s").write_text("\n".join(loops[0]) + "\n")
        (folder / "wasm-loop.wat").write_text("\n".join(loops[1]) + "\n")
        summary.append([kernel.name, len(native_function.split("\n")) - 1, len(loops[0]), len(wasm_function.split("\n")) - 1, len(loops[1])])
    with (args.output / "summary.csv").open("w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["kernel", "native_function_instructions", "native_loop_instructions", "wasm_function_instructions", "wasm_loop_instructions"])
        writer.writerows(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
