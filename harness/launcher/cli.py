"""Command line of one browser launch."""

import argparse
from pathlib import Path

from harness.launcher.commands import COMMANDS
from harness.launcher.launcher import DEFAULT_PORT, DEFAULT_TIMEOUT_SECONDS, Launcher
from harness.launcher.outcome import RunStatus
from harness.shield import pin_current_process


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python3 -m harness.launcher")
    parser.add_argument("--browser", choices=sorted(COMMANDS), required=True)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--cpus")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--results", type=Path, default=Path("data/raw"))
    parser.add_argument("--order-seed", type=int)
    parser.add_argument("--order-position", type=int)
    parser.add_argument("--scope-user")
    parser.add_argument("--harness-cpus")
    parser.add_argument("--start-delay-ms", type=int, default=0)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_arguments(argv)
    pin_current_process(args.harness_cpus)
    launcher = Launcher(
        COMMANDS[args.browser](),
        args.executable,
        args.results,
        port=args.port,
        cpus=args.cpus,
        headless=args.headless,
        timeout=args.timeout,
        order_seed=args.order_seed,
        order_position=args.order_position,
        scope_user=args.scope_user,
        start_delay_ms=args.start_delay_ms,
    )
    outcome = launcher.run(args.run, args.query)
    detail = f" ({outcome.message})" if outcome.message else ""
    print(f"{outcome.run_id} {outcome.status.value} {outcome.seconds:.1f}s{detail}")
    return 0 if outcome.status is RunStatus.DONE else 1
