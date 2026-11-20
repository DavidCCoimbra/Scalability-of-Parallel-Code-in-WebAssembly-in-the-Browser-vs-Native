"""Command line of one native run."""

import argparse
import sys
from pathlib import Path

from harness.native.run import NativeRun, NativeRunFailed
from harness.paths import NATIVE_BINARY
from harness.shield import pin_current_process


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python3 -m harness.native")
    parser.add_argument("--run", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--executable", type=Path, default=NATIVE_BINARY)
    parser.add_argument("--cpus")
    parser.add_argument("--order-seed", type=int)
    parser.add_argument("--order-position", type=int)
    parser.add_argument("--results", type=Path, default=Path("data/raw"))
    parser.add_argument("--scope-user")
    parser.add_argument("--harness-cpus")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_arguments(argv)
    pin_current_process(args.harness_cpus)
    native = NativeRun(
        [str(args.executable)],
        args.results,
        args.cpus,
        args.order_seed,
        order_position=args.order_position,
        scope_user=args.scope_user,
    )
    try:
        print(native.run(args.run, args.query))
    except NativeRunFailed as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0
