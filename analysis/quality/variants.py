"""Configurations whose runs differ in a setting that Configuration does not name.

Configuration is (environment, workload, input, k, threads). The image size, the row
pitch, the palette and the passes per sample are not part of it, so a campaign that
mixed them would pool different experiments into one configuration. The grain is left
out on purpose: the grain sweep varies it inside a configuration, and analysis/grain.py
groups by it.
"""

from collections import defaultdict
from collections.abc import Iterable

from analysis.configuration import Configuration, configuration_of
from harness.collect import Row

UNNAMED_SETTINGS = ("width", "height", "pitch", "palette", "passes")


def setting_values(row: Row) -> tuple[str, ...]:
    return (row["width"], row["height"], row["pitch"], row["palette"], row["passes"])


def mixed_configurations(rows: Iterable[Row]) -> list[Configuration]:
    seen: defaultdict[Configuration, set[tuple[str, ...]]] = defaultdict(set)
    for row in rows:
        seen[configuration_of(row)].add(setting_values(row))
    return sorted(configuration for configuration, values in seen.items() if len(values) > 1)
