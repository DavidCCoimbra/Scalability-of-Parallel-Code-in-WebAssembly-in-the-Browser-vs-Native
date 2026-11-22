"""One diagnostic Chrome run per kernel and tier, with V8 writing the code it compiles.

Usage: python3 -m scripts.capture_chrome OUTPUT_DIR
Chrome is started as in a campaign (taskset, run scope, headless) plus --no-sandbox and V8's
--perf-prof, which make the renderer write jit-<pid>.dump in its working directory. These runs
are not measurements: their flags are never used in a campaign.
"""

import os
import shutil
import sys
from pathlib import Path


from harness.launcher import ChromeCommand, Launcher
from harness.paths import BROWSERS_ROOT, REPOSITORY
from harness.server import BackgroundServer

CPUS = "0,2,4,6,8,10,12,14"
PERF_PROF = ("--perf-prof", "--perf-prof-annotate-wasm")
TIERS = {"optimizing": (), "baseline": ("--liftoff-only",)}
SIZE = "width=4096&height=4096&warmup=8&iters=4&calibration=0"
CELLS = {
    "filter": "workload=filter&input=noise&threads=2",
    "hist-atomic": "workload=hist-atomic&input=few&k=1&threads=2",
    "hist-local": "workload=hist-local&input=few&k=1&threads=2",
    "filter-seq": "workload=filter-seq&input=noise&threads=1",
    "hist-seq": "workload=hist-seq&input=few&k=1&threads=1",
}


def main(argv: list[str]) -> int:
    output = Path(argv[0]).resolve()
    chrome = next(path for path in sorted(Path(BROWSERS_ROOT).glob("chrome-*/chrome-linux64/chrome")))
    server = BackgroundServer(REPOSITORY / "bench/www")
    for tier, flags in TIERS.items():
        for cell, query in CELLS.items():
            folder = output / tier / cell
            shutil.rmtree(folder, ignore_errors=True)
            folder.mkdir(parents=True)
            os.chdir(folder)
            port = server.start(folder)
            launcher = Launcher(
                ChromeCommand(extra_flags=("--no-sandbox",), js_flags=(*PERF_PROF, *flags)),
                chrome.resolve(),
                folder,
                port=port,
                cpus=CPUS,
                headless=True,
                timeout=120,
                scope_user=os.environ["USER"],
            )
            outcome = launcher.run(f"code-{tier}-{cell}", f"{query}&{SIZE}")
            server.stop()
            dumps = sorted(folder.glob("jit-*.dump"))
            print(tier, cell, outcome.status, [f"{dump.name} {dump.stat().st_size}" for dump in dumps], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
