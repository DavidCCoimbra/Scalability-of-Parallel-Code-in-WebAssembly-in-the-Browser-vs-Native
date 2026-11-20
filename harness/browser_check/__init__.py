"""Correctness check in CI: every workload's input fingerprint and checksum in
headless Chrome and Firefox (pinned builds) must equal the native ones. Never a
measurement.

Usage: python3 -m harness.browser_check [--native bench/target/release/native]
       [--browsers harness/browsers] [--chrome-flag --no-sandbox]
       [--trust-on-first-use]
"""

from harness.browser_check.cases import CASES, HEIGHT, HISTOGRAM_KS, SIZE, THREAD_COUNTS, WIDTH, Case
from harness.browser_check.check import browser_identities, native_identities
from harness.browser_check.identity import Mismatch, RunIdentity, case_mismatches, compare, failed_label, read_identity

__all__ = [
    "CASES",
    "HEIGHT",
    "HISTOGRAM_KS",
    "SIZE",
    "THREAD_COUNTS",
    "WIDTH",
    "Case",
    "Mismatch",
    "RunIdentity",
    "browser_identities",
    "case_mismatches",
    "compare",
    "failed_label",
    "native_identities",
    "read_identity",
]
