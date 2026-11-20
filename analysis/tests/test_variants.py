import unittest

from analysis.configuration import Configuration
from analysis.quality.variants import mixed_configurations


def row(**settings: str) -> dict[str, str]:
    base = {
        "env": "native",
        "workload": "filter",
        "input": "noise",
        "k": "",
        "threads": "8",
        "width": "8192",
        "height": "8192",
        "pitch": "8192",
        "palette": "spread",
        "passes": "1",
    }
    return base | settings


class MixedConfigurationsTest(unittest.TestCase):
    def test_one_setting_per_configuration_is_not_mixed(self) -> None:
        self.assertEqual(mixed_configurations([row(), row()]), [])

    def test_two_pitches_in_one_configuration_are_mixed(self) -> None:
        mixed = mixed_configurations([row(), row(pitch="8256")])
        self.assertEqual(mixed, [Configuration("native", "filter", "noise", None, 8)])

    def test_different_threads_are_different_configurations(self) -> None:
        self.assertEqual(mixed_configurations([row(), row(threads="1", passes="4")]), [])

    def test_grain_may_vary_inside_a_configuration(self) -> None:
        self.assertEqual(mixed_configurations([row(grain="4"), row(grain="8")]), [])


if __name__ == "__main__":
    unittest.main()
