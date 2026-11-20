"""Code of one function from a V8 jitdump.

Usage: python3 -m analysis.extras.jitdump JIT_DUMP... --name SUFFIX --output FILE.bin
Chrome writes jit-<pid>.dump in its working directory when started with
--no-sandbox --js-flags="--perf-prof --perf-prof-annotate-wasm"; the dump
holds the bytes of every compiled function; a last record cut short by
a killed process is skipped, never returned short. The first function whose name
ends with SUFFIX is written to FILE.bin, for
objdump -D -b binary -m i386:x86-64 -M intel FILE.bin.
"""

import argparse
import struct
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

# Layouts from the Linux perf jitdump specification
# (tools/perf/Documentation/jitdump-specification.txt): the file header, the record header and the
# JIT_CODE_LOAD body; the magic is "JiTD" read as a little-endian 32-bit word.
HEADER = struct.Struct("<IIIIIIQQ")
RECORD = struct.Struct("<IIQ")
CODE_LOAD = struct.Struct("<IIQQQQ")
CODE_LOAD_RECORD = 0
MAGIC = 0x4A695444


class TruncatedDump(ValueError):
    pass


@dataclass(frozen=True)
class CompiledCode:
    name: str
    address: int
    code: bytes


def code_load(dump: bytes, offset: int, size: int) -> CompiledCode:
    _pid, _tid, _vma, address, code_size, _index = CODE_LOAD.unpack_from(dump, offset + RECORD.size)
    name_start = offset + RECORD.size + CODE_LOAD.size
    name_end = dump.find(b"\0", name_start, offset + size)
    if name_end < 0 or name_end + 1 + code_size > offset + size:
        raise TruncatedDump(f"code record at byte {offset} is malformed")
    code_start = name_end + 1
    return CompiledCode(dump[name_start:name_end].decode("utf-8", "replace"), address, dump[code_start : code_start + code_size])


# A record that runs past the end of the file was cut short by a killed process and ends the walk;
# a record whose own fields disagree with its size is a malformed dump and is an error.
def compiled_code(dump: bytes) -> Iterator[CompiledCode]:
    magic, _version, header_size, *_ = HEADER.unpack_from(dump, 0)
    if magic != MAGIC:
        raise ValueError("not a jitdump file")
    offset = header_size
    while offset + RECORD.size <= len(dump):
        kind, size, _timestamp = RECORD.unpack_from(dump, offset)
        if size == 0 or offset + size > len(dump):
            break
        if kind == CODE_LOAD_RECORD:
            yield code_load(dump, offset, size)
        offset += size


def find(dumps: list[Path], suffix: str) -> CompiledCode | None:
    for dump in dumps:
        for code in compiled_code(dump.read_bytes()):
            if code.name.endswith(suffix):
                return code
    return None


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("dumps", type=Path, nargs="+")
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    code = find(args.dumps, args.name)
    if code is None:
        print(f"no function ends with {args.name!r}", file=sys.stderr)
        return 1
    args.output.write_bytes(code.code)
    print(f"{code.name} at {code.address:#x}: {len(code.code)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
