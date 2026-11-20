"""Check that the Gaussian interior loop is vectorized in a built artifact.

Usage: python3 scripts/check_simd.py FILE x86_64|wasm32
FILE is `objdump -d -C` output of the native binary (x86_64), or
`wasm-objdump -d` output of the final .wasm (wasm32).
"""

import re
import sys
from pathlib import Path

FUNCTION = "blur_interior"
# The kernel works in u16 lanes, so packed 16-bit arithmetic proves vectorization;
# a stray vector register use does not.
PACKED_16_BIT = {
    "x86_64": re.compile(r"\b(?:paddw|psubw|pmullw|psllw|psrlw|punpck[lh]bw|packuswb)\b"),
    "wasm32": re.compile(
        r"\b(?:i16x8\.(?:add|sub|mul|shl|shr_u|extend_\w+)|i8x16\.narrow_i16x8_u)\b"
    ),
}
OBJDUMP_HEADER = re.compile(r"^[0-9a-f]+ (?:func\[\d+\] )?<(.+)>:$")
ASM_LABEL = re.compile(r"^([^\s.][^\s]*):\s*$")
ASM_END = "end_function"


def header_name(line: str) -> str | None:
    header = OBJDUMP_HEADER.match(line) or ASM_LABEL.match(line)
    return header.group(1) if header else None


def function_body(lines: list[str]) -> list[str] | None:
    body: list[str] | None = None
    for line in lines:
        name = header_name(line)
        if name is not None:
            if body is not None:
                return body
            if FUNCTION in name:
                body = []
            continue
        if body is not None:
            if line.strip() == ASM_END:
                return body
            body.append(line)
    return body


def packed_count(body: list[str], arch: str) -> int:
    return sum(1 for line in body if PACKED_16_BIT[arch].search(line))


def main(argv: list[str]) -> int:
    path, arch = argv
    body = function_body(Path(path).read_text().splitlines())
    if body is None:
        print(f"{FUNCTION} not found in {path}")
        return 1
    count = packed_count(body, arch)
    print(f"{FUNCTION}: {count} packed 16-bit instructions ({arch})")
    return 0 if count > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
