"""Run every case natively and in each browser, and compare what they produced."""

from pathlib import Path

from harness.browser_check.cases import CASES
from harness.browser_check.identity import Found, RunIdentity, failed_label, read_identity
from harness.context import RunEnvironment, RunFiles
from harness.launcher import Launcher, RunStatus
from harness.native import NativeRun


def native_identities(executable: Path, results: Path) -> dict[str, RunIdentity]:
    native = NativeRun([str(executable)], results, cpus=None, order_seed=None)
    return {case.name: read_identity(native.run(case.run_id(RunEnvironment.NATIVE), case.query)) for case in CASES}


def browser_identities(launcher: Launcher, results: Path) -> dict[str, Found]:
    found: dict[str, Found] = {}
    for case in CASES:
        run_id = case.run_id(launcher.browser.name)
        outcome = launcher.run(run_id, case.query)
        print(f"{run_id}: {outcome.status.value} {outcome.seconds:.1f}s")
        if outcome.status is RunStatus.DONE:
            found[case.name] = read_identity(RunFiles(results, run_id).csv)
        else:
            found[case.name] = failed_label(outcome.status)
    return found
