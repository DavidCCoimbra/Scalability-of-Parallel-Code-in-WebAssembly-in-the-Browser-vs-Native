import csv
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TextIO

from analysis.configuration import Configuration, CsvCell, Environment
from analysis.runs import RunSummary, values_by_configuration
from analysis.scaling.output import CONFIGURATION_COLUMNS
from analysis.scaling.table import SINGLE_THREAD_INTERVAL, Speedup, speedup_of
from analysis.stats.summary import CONFIGURATION_CENTER, Summary

COLUMNS = (
    *CONFIGURATION_COLUMNS,
    "runs",
    "pixels",
    "ns_per_pixel",
    "megapixels_per_second",
    "absolute_speedup",
    "absolute_speedup_low",
    "absolute_speedup_high",
)
NANOSECONDS_PER_SECOND = 1e9
PIXELS_PER_MEGAPIXEL = 1e6
SIGNIFICANT_DIGITS = 4


# Time per pixel and pixels per second of one pass over the image (one byte per pixel, so
# megapixels per second is also MB of input per second), and the absolute speedup: the native
# one-thread time over this configuration's time. The relative speedup of the scaling table
# divides by the same environment's T1 and so hides how fast that T1 is; this one does not.
@dataclass(frozen=True)
class ThroughputRow:
    configuration: Configuration
    runs: int
    pixels: int
    center_ns: float
    absolute: Speedup | None

    @property
    def ns_per_pixel(self) -> float:
        return self.center_ns / self.pixels

    @property
    def megapixels_per_second(self) -> float:
        return self.pixels / PIXELS_PER_MEGAPIXEL / (self.center_ns / NANOSECONDS_PER_SECOND)

    def cells(self) -> list[CsvCell]:
        absolute = self.absolute
        speedup = ["", "", ""] if absolute is None else [number(absolute.value), number(absolute.interval.low), number(absolute.interval.high)]
        return [
            *self.configuration.cells(),
            self.runs,
            self.pixels,
            number(self.ns_per_pixel),
            f"{self.megapixels_per_second:.1f}",
            *speedup,
        ]


def number(value: float) -> str:
    return f"{value:.{SIGNIFICANT_DIGITS}g}"


def native_baseline(configuration: Configuration) -> Configuration:
    return configuration.in_environment(Environment.NATIVE).baseline()


def absolute_speedup(
    configuration: Configuration, values: Sequence[float], baseline: Sequence[float] | None, center: Summary
) -> Speedup | None:
    if baseline is None:
        return None
    if configuration == native_baseline(configuration):
        return Speedup(1.0, SINGLE_THREAD_INTERVAL)
    return speedup_of(baseline, values, center)


def throughput_table(
    runs: Iterable[RunSummary], pixels: dict[Configuration, int], center: Summary = CONFIGURATION_CENTER
) -> list[ThroughputRow]:
    groups = values_by_configuration(runs)
    return [
        ThroughputRow(
            configuration,
            len(values),
            pixels[configuration],
            center.of(values),
            absolute_speedup(configuration, values, groups.get(native_baseline(configuration)), center),
        )
        for configuration, values in sorted(groups.items())
    ]


def write_throughput(rows: list[ThroughputRow], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(COLUMNS)
    for row in rows:
        writer.writerow(row.cells())
