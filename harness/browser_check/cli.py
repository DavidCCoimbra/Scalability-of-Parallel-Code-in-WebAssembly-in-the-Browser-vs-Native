"""Command line of the CI correctness check."""

import argparse
import tempfile
from pathlib import Path

from harness.browser_check.cases import CASES
from harness.browser_check.check import browser_identities, native_identities
from harness.browser_check.identity import Mismatch, compare
from harness.browsers import Installer, load_specs
from harness.launcher import BrowserCommand, ChromeCommand, FirefoxCommand, Launcher
from harness.paths import BROWSER_VERSIONS, BROWSERS_ROOT, NATIVE_BINARY, WWW
from harness.server import BackgroundServer

LAUNCH_TIMEOUT_SECONDS = 120.0


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python3 -m harness.browser_check")
    parser.add_argument("--native", type=Path, default=NATIVE_BINARY)
    parser.add_argument("--browsers", type=Path, default=BROWSERS_ROOT)
    parser.add_argument("--chrome-flag", action="append", default=[])
    parser.add_argument("--trust-on-first-use", action="store_true")
    return parser.parse_args(argv)


def install_browsers(root: Path, trust_on_first_use: bool) -> dict[str, Path]:
    installer = Installer(root, trust_on_first_use=trust_on_first_use)
    executables = {name: installer.install(spec) for name, spec in load_specs(BROWSER_VERSIONS).items()}
    for name, digest in installer.reported.items():
        print(f"{name} installed unverified; pin this sha256 in browsers.json: {digest}")
    return executables


def main(argv: list[str]) -> int:
    args = parse_arguments(argv)
    executables = install_browsers(args.browsers, args.trust_on_first_use)
    commands: dict[str, BrowserCommand] = {"chrome": ChromeCommand(tuple(args.chrome_flag)), "firefox": FirefoxCommand()}
    with tempfile.TemporaryDirectory() as tmp:
        results = Path(tmp)
        server = BackgroundServer(WWW)
        port = server.start(results)
        try:
            native = native_identities(args.native, results)
            browsers = {
                name: browser_identities(
                    Launcher(command, executables[name], results, port=port, headless=True, timeout=LAUNCH_TIMEOUT_SECONDS),
                    results,
                )
                for name, command in commands.items()
            }
        finally:
            server.stop()
    return report(compare(native, browsers), total=len(CASES) * len(browsers))


def report(mismatches: list[Mismatch], total: int) -> int:
    for mismatch in mismatches:
        print(
            f"MISMATCH {mismatch.environment} {mismatch.case} {mismatch.field}: "
            f"native {mismatch.native}, browser {mismatch.browser}"
        )
    failed = len({(mismatch.environment, mismatch.case) for mismatch in mismatches})
    print(f"{total - failed}/{total} browser runs match native input fingerprints and checksums")
    return 1 if mismatches else 0
