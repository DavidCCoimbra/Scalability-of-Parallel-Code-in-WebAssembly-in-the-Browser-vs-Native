"""The gate before a build's campaigns: exits 1 unless a gate campaign is fit to start from.

Usage: python3 -m analysis.gate data/raw/gate-<build>
It passes when no run failed, was excluded or is missing, the checksums agree across
environments, thread counts and each sequential reference and its parallel workloads, every
timed sample is at least 100 times the clock resolution, and the first three measured
iterations of every configuration are within 5 % of the last three.
"""

import argparse
import sys
from pathlib import Path

from analysis.quality.gate import gate_problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    problems = gate_problems(args.directory)
    for problem in problems:
        print(f"gate: {problem}")
    print(f"gate: {len(problems)} problem(s)" if problems else "gate: passed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
