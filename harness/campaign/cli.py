"""Command line of a campaign."""

import argparse
import json
import sys
from pathlib import Path

from harness.browsers import Installer, load_specs
from harness.campaign.gate import EnvironmentNotReady
from harness.campaign.runner import Campaign, Summary
from harness.campaign.spec import CampaignSpec
from harness.context import BROWSERS
from harness.paths import BROWSER_VERSIONS, BROWSERS_ROOT
from harness.shield import pin_current_process


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python3 -m harness.campaign")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--results", type=Path, default=Path("data/raw"))
    parser.add_argument("--native", type=Path)
    parser.add_argument("--browsers", type=Path, default=BROWSERS_ROOT)
    parser.add_argument("--chrome", type=Path)
    parser.add_argument("--firefox", type=Path)
    parser.add_argument("--retry-failed", action="store_true")
    return parser.parse_args(argv)


def browser_executables(args: argparse.Namespace, spec: CampaignSpec) -> dict[str, Path]:
    overrides: dict[str, Path | None] = {"chrome": args.chrome, "firefox": args.firefox}
    wanted = [name for name in BROWSERS if name in spec.environments]
    missing = [name for name in wanted if overrides[name] is None]
    installed: dict[str, Path] = {}
    if missing:
        installer = Installer(args.browsers)
        specs = load_specs(BROWSER_VERSIONS)
        installed = {name: installer.install(specs[name]) for name in missing}
    return {name: overrides[name] or installed[name] for name in wanted}


def main(argv: list[str]) -> int:
    args = parse_arguments(argv)
    spec = CampaignSpec.from_json(json.loads(args.spec.read_text()))
    pin_current_process(spec.harness_cpus)
    campaign = Campaign.for_spec(
        spec,
        args.results / spec.name,
        [str(args.native or spec.native_binary)],
        browser_executables(args, spec),
        args.retry_failed,
        args.browsers,
    )
    try:
        summary = campaign.run()
    except EnvironmentNotReady as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print_summary(spec.name, summary)
    return 0 if summary.ok else 1


def print_summary(name: str, summary: Summary) -> None:
    print(
        f"{name}: {summary.done} done, {summary.failed} failed, {summary.skipped} skipped, "
        f"{summary.earlier_failures} failed earlier (rerun with --retry-failed to run them again)"
    )
