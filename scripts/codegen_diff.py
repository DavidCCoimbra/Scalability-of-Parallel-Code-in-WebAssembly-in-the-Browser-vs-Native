"""Compare the machine code of two builds of the bench crate, function by function.

Usage:
  python3 scripts/codegen_diff.py native BASE_BINARY HEAD_BINARY
  python3 scripts/codegen_diff.py wasm BASE_WASM HEAD_WASM

Functions are paired by demangled name after collapsing `bench::` module
paths to the item name, because v0 mangling changes when an item moves to
another module. Native code is compared after dropping addresses, and turning
jump targets into function-relative offsets and RIP-relative data offsets into
a placeholder. WASM code is compared after replacing `i32.const` operands and
load/store offsets that fall between the initial stack pointer (where the
passive data segments start) and the largest constant global (__heap_base)
plus some slack; an `i32.const` that differs only because the function table
was reordered (a function pointer) counts as the same when both indices name
the same function. Exit status 1 means a hot function differs.
"""

import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TypeVar

HOT = [
    re.compile(pattern)
    for pattern in (
        r"bench::blur_interior",
        r"Workload>::run",
        r"Workload>::prepare",
        r"Workload>::checksum",
        r"bench::Histogram>::merge",
        r"bench::Histogram>::checksum",
        r"bench::Checksum>::of_bytes",
        r"bench::measure",
        r"bench::timed_iteration",
        r"bench::calibrate",
        r"bench::pause_for",
        r"bench::execute",
        r"^bench::run$",
        r"^native::run$",
        r"^native::main$",
        r"slice::sort::.*\bu32(?![0-9])",
        r"sort::.*\bu32(?![0-9])",
    )
]
KINDS = ("native", "wasm")
ARGUMENT_COUNT = 4
USAGE_EXIT = 2
CRATE_HASH = re.compile(r"_[0-9a-f]{16}_(?=::)|\[[0-9a-f]{16}\]")
V0_SYMBOL = re.compile(r"([$<])(_R[0-9A-Za-z_]+)")
MODULE_PATH = re.compile(r"(?<![A-Za-z0-9])bench(?:::[a-z_][a-z0-9_]*)*::(?=[A-Za-z_])")
NATIVE_HEADER = re.compile(r"^([0-9a-f]+) <(.+)>:$")
NATIVE_LINE = re.compile(r"^\s*([0-9a-f]+):\s*(.*)$")
NATIVE_TARGET = re.compile(r"\b[0-9a-f]+ <(.+?)(\+0x[0-9a-f]+)?>$")
RIP_OFFSET = re.compile(r"-?0x[0-9a-f]+\(%rip\)")
COMMENT = re.compile(r"\s+# .*$")
BRANCH = re.compile(r"^(j\w+|call|loop\w*)\s+([0-9a-f]+) <")
COPY_SUFFIX = " #"
CACHE_LINE_BYTES = 64
MAX_LISTED_LOOPS = 8
WASM_FUNC = re.compile(r'^\s*\(func \$(\S+)')
WASM_CALL = re.compile(r"call \$(\S+)")
WASM_TOP_LEVEL = "  ("
WASM_STACK = re.compile(r"^\s*\(global \$__stack_pointer \(mut i32\) \(i32\.const (\d+)\)\)")
WASM_GLOBAL_I32 = re.compile(r"^\s*\(global \S+ i32 \(i32\.const (\d+)\)\)")
DATA_SLACK = 64 * 1024
# wasm2wat prints i32.const signed, while data addresses are unsigned.
U32_MASK = 0xFFFF_FFFF
WASM_I32 = re.compile(r"i32\.const (-?\d+)")
WASM_OFFSET = re.compile(r"offset=(\d+)")
WASM_ELEM = re.compile(r"^\s*\(elem \S+ \(i32\.const (\d+)\) func (.*)\)$")
WASM_CONST_LINE = re.compile(r"^i32\.const (\d+)$")
WASM_SIZE = re.compile(r"^ - func\[(\d+)\] size=(\d+)")
WASM_IMPORTED_FUNC = re.compile(r"^\s*\(import .*\(func ")
FILE_LINE = re.compile(r"\s*;;.*$")

FunctionTable = dict[int, str]


@dataclass(frozen=True)
class AddressRange:
    start: int
    end: int

    def __contains__(self, value: int) -> bool:
        return self.start <= value <= self.end


@dataclass(frozen=True)
class Instruction:
    address: int
    text: str


@dataclass
class NativeListing:
    raw_name: str
    start: int
    instructions: list[Instruction]


@dataclass(frozen=True)
class NativeFunction:
    listing: NativeListing
    code: list[str]
    loops: list[int]
    table: FunctionTable | None = None


@dataclass(frozen=True)
class WasmFunction:
    code: list[str]
    size: int | None
    table: FunctionTable


class ComparedFunction(Protocol):
    @property
    def code(self) -> list[str]: ...

    @property
    def table(self) -> FunctionTable | None: ...


Function = TypeVar("Function", NativeFunction, WasmFunction)
Functions = dict[str, Function]
Extra = Callable[[str, Function | None, Function | None], str]


def pairing_name(name: str) -> str:
    return MODULE_PATH.sub("bench::", CRATE_HASH.sub("", name))


def is_hot(name: str) -> bool:
    return any(pattern.search(name) for pattern in HOT)


def run(command: list[str]) -> str:
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def native_listings(binary: Path) -> dict[str, NativeListing]:
    listings: dict[str, NativeListing] = {}
    current = None
    for line in run(["objdump", "-d", "-C", "--no-show-raw-insn", str(binary)]).splitlines():
        header = NATIVE_HEADER.match(line)
        if header:
            current = NativeListing(header.group(2), int(header.group(1), 16), [])
            listings[unique_key(listings, pairing_name(header.group(2)))] = current
            continue
        body = NATIVE_LINE.match(line)
        if current is not None and body:
            current.instructions.append(Instruction(int(body.group(1), 16), body.group(2)))
    return listings


def unique_key(listings: dict[str, NativeListing], name: str) -> str:
    # Distinct symbols can pair to one name once hashes and module paths are dropped;
    # later copies get " #2", " #3", ... in objdump order.
    copies = sum(1 for known in listings if known.split(COPY_SUFFIX)[0] == name)
    return name if not copies else f"{name}{COPY_SUFFIX}{copies + 1}"


def native_functions(binary: Path) -> Functions[NativeFunction]:
    return {name: native_function(listing) for name, listing in native_listings(binary).items()}


def native_function(listing: NativeListing) -> NativeFunction:
    code = [normalize_native(instruction.text, listing) for instruction in listing.instructions]
    return NativeFunction(listing, code, loop_heads(listing))


def normalize_native(text: str, listing: NativeListing) -> str:
    def target(match: re.Match[str]) -> str:
        symbol, offset = match.group(1), match.group(2) or ""
        if symbol == listing.raw_name:
            return f".{offset or '+0x0'}"
        return pairing_name(symbol) + offset

    text = COMMENT.sub("", text)
    text = NATIVE_TARGET.sub(target, text)
    text = RIP_OFFSET.sub("DATA(%rip)", text)
    return " ".join(text.split())


def loop_heads(listing: NativeListing) -> list[int]:
    heads = set()
    for instruction in listing.instructions:
        branch = BRANCH.match(instruction.text)
        if branch and branch.group(1).startswith("j"):
            destination = int(branch.group(2), 16)
            if listing.start <= destination <= instruction.address:
                heads.add(destination)
    return sorted(heads)


def text_size(binary: Path) -> int:
    for line in run(["objdump", "-h", str(binary)]).splitlines():
        fields = line.split()
        if len(fields) > 2 and fields[1] == ".text":
            return int(fields[2], 16)
    return 0


def wasm_listings(wat: list[str]) -> dict[str, list[str]]:
    listings: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in wat:
        start = WASM_FUNC.match(line)
        if start:
            current = []
            listings[pairing_name(start.group(1))] = current
        elif line.startswith(WASM_TOP_LEVEL) and current is not None:
            current = None
        if current is not None:
            current.append(line)
    return listings


def wasm_functions(module: Path) -> Functions[WasmFunction]:
    wat = demangle(run(["wasm2wat", "--enable-threads", str(module)])).splitlines()
    ranges = data_ranges(wat)
    sizes = wasm_sizes(module)
    table = function_table(wat)
    # wasm-objdump numbers functions after the imported ones.
    imported = sum(1 for line in wat if WASM_IMPORTED_FUNC.match(line))
    return {
        name: WasmFunction([normalize_wasm(line, ranges) for line in lines], sizes.get(imported + index), table)
        for index, (name, lines) in enumerate(wasm_listings(wat).items())
    }


def function_table(wat: list[str]) -> FunctionTable:
    table = {}
    for line in wat:
        elem = WASM_ELEM.match(line)
        if elem:
            first = int(elem.group(1))
            for offset, name in enumerate(elem.group(2).split()):
                table[first + offset] = pairing_name(name.lstrip("$"))
    return table


def demangle(text: str) -> str:
    symbols = sorted({symbol for _, symbol in V0_SYMBOL.findall(text)})
    if not symbols:
        return text
    names = subprocess.run(
        ["c++filt"], input="\n".join(symbols), check=True, capture_output=True, text=True
    ).stdout.splitlines()
    readable = {symbol: name.replace(" ", "_") for symbol, name in zip(symbols, names)}
    return V0_SYMBOL.sub(lambda match: match.group(1) + readable[match.group(2)], text)


def data_ranges(wat: list[str]) -> list[AddressRange]:
    starts = [int(match.group(1)) for line in wat if (match := WASM_STACK.match(line))]
    ends = [int(match.group(1)) for line in wat if (match := WASM_GLOBAL_I32.match(line))]
    if not starts or not ends:
        return []
    return [AddressRange(min(starts), max(ends) + DATA_SLACK)]


def in_data(value: int, ranges: list[AddressRange]) -> bool:
    return any(value in data for data in ranges)


def normalize_wasm(line: str, ranges: list[AddressRange]) -> str:
    def constant(match: re.Match[str]) -> str:
        return "i32.const DATA" if in_data(int(match.group(1)) & U32_MASK, ranges) else match.group(0)

    def offset(match: re.Match[str]) -> str:
        return "offset=DATA" if in_data(int(match.group(1)), ranges) else match.group(0)

    def paired(prefix: str) -> Callable[[re.Match[str]], str]:
        return lambda match: f"{prefix}${pairing_name(match.group(1))}"

    line = FILE_LINE.sub("", line)
    line = WASM_OFFSET.sub(offset, line)
    line = WASM_FUNC.sub(paired("(func "), line)
    line = WASM_CALL.sub(paired("call "), line)
    return WASM_I32.sub(constant, line).strip()


def wasm_sizes(module: Path) -> dict[int, int]:
    sizes = {}
    for line in run(["wasm-objdump", "-x", str(module)]).splitlines():
        size = WASM_SIZE.match(line)
        if size:
            sizes[int(size.group(1))] = int(size.group(2))
    return sizes


def same_code(base: ComparedFunction, head: ComparedFunction) -> bool:
    if len(base.code) != len(head.code):
        return False
    return all(
        old == new or same_table_entry(old, new, base.table, head.table)
        for old, new in zip(base.code, head.code)
    )


def same_table_entry(old: str, new: str, old_table: FunctionTable | None, new_table: FunctionTable | None) -> bool:
    if old_table is None or new_table is None:
        return False
    old_index, new_index = WASM_CONST_LINE.match(old), WASM_CONST_LINE.match(new)
    if not old_index or not new_index:
        return False
    old_name = old_table.get(int(old_index.group(1)))
    return old_name is not None and old_name == new_table.get(int(new_index.group(1)))


def pair_state(name: str, base: Functions[Function], head: Functions[Function]) -> str:
    if name not in base or name not in head:
        return "only in base" if name in base else "only in head"
    return "identical" if same_code(base[name], head[name]) else "differs"


def report(base: Functions[Function], head: Functions[Function], extra: Extra[Function]) -> int:
    hot_differs = 0
    status: Counter[str] = Counter()
    for name in sorted(set(base) | set(head)):
        state = pair_state(name, base, head)
        status[state] += 1
        if is_hot(name):
            hot_differs += state != "identical"
            print(f"HOT {state:<12} {extra(name, base.get(name), head.get(name))} {name}")
        elif state != "identical":
            print(f"    {state:<12} {name}")
    print("summary: " + ", ".join(f"{state} {count}" for state, count in sorted(status.items())))
    return 1 if hot_differs else 0


@dataclass(frozen=True)
class Alignment:
    start: int
    loops: list[int]

    @classmethod
    def of(cls, function: NativeFunction) -> "Alignment":
        listing = function.listing
        return cls(listing.start % CACHE_LINE_BYTES, [address % CACHE_LINE_BYTES for address in function.loops])

    def listed_loops(self) -> str:
        return str(self.loops) if len(self.loops) <= MAX_LISTED_LOOPS else f"{len(self.loops)} loop heads"


def native_extra(name: str, base: NativeFunction | None, head: NativeFunction | None) -> str:
    if base is None or head is None:
        return "[alignment -]"
    before, after = Alignment.of(base), Alignment.of(head)
    same = "same" if before == after else "DIFFERENT"
    return f"[start%64 {before.start} -> {after.start}, loops%64 {before.listed_loops()}: {same}]"


def wasm_extra(name: str, base: WasmFunction | None, head: WasmFunction | None) -> str:
    def size(function: WasmFunction | None) -> str:
        return "-" if function is None or function.size is None else str(function.size)

    return f"[size {size(base)} -> {size(head)}]"


def compare_native(base_path: Path, head_path: Path) -> int:
    print(f".text size: base {text_size(base_path)} head {text_size(head_path)}")
    return report(native_functions(base_path), native_functions(head_path), native_extra)


def compare_wasm(base_path: Path, head_path: Path) -> int:
    print(f"file size: base {base_path.stat().st_size} head {head_path.stat().st_size}")
    return report(wasm_functions(base_path), wasm_functions(head_path), wasm_extra)


def main(argv: list[str]) -> int:
    if len(argv) != ARGUMENT_COUNT or argv[1] not in KINDS:
        print(__doc__, file=sys.stderr)
        return USAGE_EXIT
    kind, base_path, head_path = argv[1], Path(argv[2]), Path(argv[3])
    if kind == "native":
        return compare_native(base_path, head_path)
    return compare_wasm(base_path, head_path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
