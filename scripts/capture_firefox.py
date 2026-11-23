"""One long Firefox run per kernel, sampled with perf, and the bytes of the hottest code read back.

Usage: python3 -m scripts.capture_firefox OUTPUT_DIR
Firefox's release build writes no dump of its compiled code. This reads it from the running
process instead: perf samples the content process for a few seconds, the page with most samples
in memory that is no file is taken for the kernel's loop, and its bytes are read from
/proc/<pid>/mem by a root unit (the kernel lets a process read only its descendants' memory).
A diagnostic run, never a measurement.
"""

import collections
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from harness.launcher import FirefoxCommand, Launcher
from harness.paths import BROWSERS_ROOT, REPOSITORY
from harness.server import BackgroundServer

CPUS = "0,2,4,6,8,10,12,14"
# Long enough for perf to sample the steady loop: about 20 s of measured iterations.
CELLS = {
    "blur-interior": "workload=filter&input=noise&threads=1&width=8192&height=8192&warmup=20&iters=600&calibration=0",
    "atomic-loop": "workload=hist-atomic&input=few&k=256&threads=1&width=8192&height=8192&warmup=5&iters=50&calibration=0",
    "local-loop": "workload=hist-local&input=few&k=256&threads=1&width=8192&height=8192&warmup=20&iters=600&calibration=0",
}
SETTLE_SECONDS = 8
SAMPLE_SECONDS = 5
PAGE = 4096
WINDOW_PAGES = 2


def busiest_firefox() -> int:
    listing = subprocess.run(["ps", "-eo", "pid,pcpu,comm", "--sort=-pcpu"], capture_output=True, text=True, check=True).stdout
    for line in listing.splitlines()[1:]:
        pid, _cpu, command = line.split(None, 2)
        if "firefox" in command or "Isolated Web" in command or "Web Content" in command:
            return int(pid)
    raise SystemExit("no Firefox process found")


def sample(pid: int, folder: Path) -> None:
    data = folder / "perf.data"
    subprocess.run(["perf", "record", "-q", "-e", "cycles:u", "-p", str(pid), "-o", str(data), "--", "sleep", str(SAMPLE_SECONDS)], check=False, capture_output=True)
    script = subprocess.run(["perf", "script", "-i", str(data), "-F", "ip,dso"], capture_output=True, text=True, check=False).stdout
    pages: collections.Counter[int] = collections.Counter()
    total = 0
    for line in script.splitlines():
        fields = line.split()
        if len(fields) < 2:
            continue
        total += 1
        # SpiderMonkey names the mapping of its compiled code.
        if "js-executable-memory" in fields[1]:
            pages[int(fields[0], 16) // PAGE] += 1
    if not pages:
        (folder / "result.txt").write_text(f"{total} samples, none in anonymous memory\n")
        return
    page, hits = pages.most_common(1)[0]
    start, length = (page - 1) * PAGE, (WINDOW_PAGES + 1) * PAGE
    dump = folder / "hot.bin"
    command = f"dd if=/proc/{pid}/mem of={dump} bs=1 skip={start} count={length} status=none"
    done = subprocess.run(["sudo", "-n", "systemd-run", "--quiet", "--wait", "--collect", "--", "sh", "-c", command], capture_output=True, text=True, check=False)
    (folder / "result.txt").write_text(
        f"pid {pid}: {total} samples, {sum(pages.values())} in anonymous memory, {hits} in the page at {page * PAGE:#x}\n"
        f"read {length} bytes from {start:#x}: exit {done.returncode} {done.stderr.strip()}\n"
        f"top pages: {[(hex(p * PAGE), n) for p, n in pages.most_common(5)]}\n"
    )


def main(argv: list[str]) -> int:
    output = Path(argv[0]).resolve()
    firefox = next(path for path in sorted(Path(BROWSERS_ROOT).glob("firefox-*/firefox/firefox")))
    server = BackgroundServer(REPOSITORY / "bench/www")
    for cell, query in CELLS.items():
        folder = output / cell
        folder.mkdir(parents=True, exist_ok=True)
        port = server.start(folder)
        launcher = Launcher(FirefoxCommand(), firefox.resolve(), folder, port=port, cpus=CPUS, headless=True, timeout=180, scope_user=os.environ["USER"])
        run = threading.Thread(target=launcher.run, args=(f"code-firefox-{cell}-{int(time.time())}", query))
        run.start()
        time.sleep(SETTLE_SECONDS)
        sample(busiest_firefox(), folder)
        run.join()
        server.stop()
        print(cell, (folder / "result.txt").read_text().strip(), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
