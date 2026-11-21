"""The names of workloads, inputs, environments and palettes are written three times: in the
bench (Rust), in the harness and in the analysis. A run's CSV carries the bench's names and the
other two match on them as strings, so a renamed or added name on one side would be dropped
silently. This test reads the Rust name tables and compares the three.
"""

import re
import unittest
from pathlib import Path

from analysis import configuration as analysis
from harness.campaign.workload import InputKind, Palette, Workload
from harness.context.run_environment import RunEnvironment

BENCH = Path(__file__).resolve().parents[2] / "bench/src"
NAME_ARM = re.compile(r'Self::\w+(?:\s*\{[^}]*\})?\s*=>\s*"([a-z0-9-]+)"')


def rust_names(relative: str) -> set[str]:
    return set(NAME_ARM.findall((BENCH / relative).read_text()))


class NameParityTest(unittest.TestCase):
    def test_workloads(self) -> None:
        self.assertEqual(rust_names("experiment/workload_kind.rs"), {workload.value for workload in Workload})
        # The analysis names only the workloads the analysis plan refers to.
        self.assertLessEqual({workload.value for workload in analysis.Workload}, {workload.value for workload in Workload})

    def test_environments(self) -> None:
        bench = rust_names("experiment/environment.rs")
        self.assertEqual(bench, {environment.value for environment in RunEnvironment})
        self.assertEqual(bench, {environment.value for environment in analysis.Environment})

    def test_inputs(self) -> None:
        bench = rust_names("experiment/input_kind.rs")
        self.assertEqual(bench, {kind.value for kind in InputKind})
        self.assertEqual(bench, {kind.value for kind in analysis.Input})

    def test_palettes(self) -> None:
        self.assertEqual(rust_names("input/palette.rs"), {palette.value for palette in Palette})


if __name__ == "__main__":
    unittest.main()
