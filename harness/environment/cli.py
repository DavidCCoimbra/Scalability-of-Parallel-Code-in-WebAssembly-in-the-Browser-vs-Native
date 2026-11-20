"""Command line of the environment check."""

import argparse
import sys
from pathlib import Path

from harness.environment.check import EnvironmentCheck
from harness.environment.sysinfo import write_sysinfo
from harness.environment.topology import p_core_mask
from harness.paths import BROWSERS_ROOT

MASK = "mask"
CHECK = "check"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m harness.environment")
    parser.add_argument("command", choices=[MASK, CHECK])
    parser.add_argument("--cpus")
    parser.add_argument("--sysinfo", type=Path)
    parser.add_argument("--browsers", type=Path, default=BROWSERS_ROOT)
    args = parser.parse_args(argv)
    if args.command == MASK:
        print(p_core_mask() or "no hybrid CPU topology found")
        return 0
    if not args.cpus:
        parser.error("check needs --cpus")
    return check(args.cpus, args.sysinfo, args.browsers)


def check(cpus: str, sysinfo_path: Path | None, browsers: Path) -> int:
    problems = EnvironmentCheck().problems(cpus)
    if sysinfo_path:
        sysinfo_path.parent.mkdir(parents=True, exist_ok=True)
        write_sysinfo(sysinfo_path, cpus, browsers, problems)
    for problem in problems:
        print(f"problem: {problem}", file=sys.stderr)
    print("environment ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0
