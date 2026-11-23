"""The hot loop of each kernel in the bytes that capture_firefox.py read from a running Firefox.

Usage: python3 -m scripts.firefox_code CAPTURE_DIR OUTPUT_DIR
The bytes are a window of memory, not a function with a known start, so the disassembly is
started at the offset that puts the most samples on the start of an instruction. The listing
written is the span of instructions that holds the sampled addresses, with the samples of each.
"""

import collections
import re
import subprocess
import sys
from pathlib import Path

CODE_MAPPING = "js-executable-memory"
LINE = re.compile(r"^\s*([0-9a-f]+):\s+(.*)$")
TRIED_OFFSETS = 16


def samples(folder: Path) -> collections.Counter[int]:
    script = subprocess.run(["perf", "script", "-i", str(folder / "perf.data"), "-F", "ip,dso"], capture_output=True, text=True, check=True).stdout
    return collections.Counter(int(line.split()[0], 16) for line in script.splitlines() if CODE_MAPPING in line)


def disassembly(dump: Path, address: int, skip: int) -> list[tuple[int, str]]:
    listing = subprocess.run(
        ["objdump", "-D", "-b", "binary", "-m", "i386:x86-64", "--no-show-raw-insn", f"--adjust-vma={address:#x}", f"--start-address={address + skip:#x}", str(dump)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [(int(m.group(1), 16), m.group(2).strip()) for m in map(LINE.match, listing.splitlines()) if m]


JUMP = re.compile(r"^j\w+\s+(?:0x)?([0-9a-f]+)\b")
# The kernel's loop is the shortest loop with the kernel's marker that holds this share of the
# samples: shorter than a loop around it, and sampled far more than a remainder loop. The marker
# keeps out the loop of the checksum, which runs after every iteration and is sampled more than
# the filter itself.
LOOP_SHARE = 0.1
MARKERS = {"blur-interior": "xmm", "atomic-loop": "lock", "local-loop": "movzb"}


def hot_loop(lines: list[tuple[int, str]], hits: collections.Counter[int], marker: str) -> list[tuple[int, str]]:
    index = {address: position for position, (address, _) in enumerate(lines)}
    marked = {address for address, text in lines if marker in text}
    total = sum(hits.values())
    best: tuple[int, int, int] | None = None
    for position, (address, text) in enumerate(lines):
        jump = JUMP.match(text)
        if jump is None or int(jump.group(1), 16) not in index or int(jump.group(1), 16) > address:
            continue
        start = index[int(jump.group(1), 16)]
        body = lines[start : position + 1]
        if not any(a in marked for a, _ in body):
            continue
        inside = sum(hits.get(a, 0) for a, _ in body)
        if inside >= LOOP_SHARE * total and (best is None or position - start < best[1] - best[0]):
            best = (start, position, inside)
    if best is None:
        raise SystemExit(f"no loop with {marker}")
    return lines[best[0] : best[1] + 1]


def main(argv: list[str]) -> int:
    capture, output = Path(argv[0]), Path(argv[1])
    for folder in sorted(path for path in capture.iterdir() if (path / "hot.bin").exists()):
        start = int(re.search(r"bytes from (0x[0-9a-f]+)", (folder / "result.txt").read_text()).group(1), 16)  # type: ignore[union-attr]
        hits = samples(folder)
        low = min(address for address, count in hits.items() if count >= max(hits.values()) // 200)
        best: list[tuple[int, str]] = []
        best_score = -1
        for skip in range(TRIED_OFFSETS):
            lines = disassembly(folder / "hot.bin", start, max(low - start - 256, 0) + skip)
            starts = {address for address, _ in lines}
            score = sum(count for address, count in hits.items() if address in starts)
            if score > best_score:
                best, best_score = lines, score
        span = hot_loop(best, hits, MARKERS[folder.name])
        inside = sum(hits.get(address, 0) for address, _ in span)
        text = [
            f"# {sum(hits.values())} samples in SpiderMonkey's code, {best_score} on an instruction start of the disassembly; "
            f"{inside} in this loop of {len(span)} instructions (columns: offset, samples, instruction)"
        ]
        text += [f"{address - low:+6x}  {hits.get(address, 0):6d}  {instruction}" for address, instruction in span]
        target = output / folder.name
        target.mkdir(parents=True, exist_ok=True)
        (target / "firefox-loop.s").write_text("\n".join(text) + "\n")
        print(f"{folder.name}: {len(span)} instructions, {inside} of {sum(hits.values())} samples in the loop, {best_score} aligned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
