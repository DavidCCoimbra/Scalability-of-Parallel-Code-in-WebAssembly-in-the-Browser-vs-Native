"""Command line of the shield check."""

import argparse
import sys

from harness.shield.cgroup import CgroupShield


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m harness.shield")
    parser.add_argument("command", choices=["check"])
    parser.add_argument("--cpus", required=True)
    args = parser.parse_args(argv)
    shield = CgroupShield()
    print(shield.state())
    problems = shield.problems(args.cpus)
    for problem in problems:
        print(f"problem: {problem}", file=sys.stderr)
    return 1 if problems else 0
