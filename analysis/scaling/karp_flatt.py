import csv
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TextIO

from analysis.configuration import Configuration, CsvCell, parse_k
from analysis.scaling.output import CONFIGURATION_COLUMNS, number

KARP_FLATT_COLUMNS = (*CONFIGURATION_COLUMNS, "speedup", "serial_fraction", "serial_fraction_low", "serial_fraction_high")


# Karp and Flatt 1990 (https://doi.org/10.1145/78607.78614): the experimentally determined serial
# fraction e = (1 / S - 1 / N) / (1 - 1 / N), the Amdahl serial fraction that would give the measured
# speedup S on N threads. A constant e reads as a serial part; an e that grows with N reads as an
# overhead that grows with N. e falls as S rises, so the high end of S gives the low end of e.
def serial_fraction(speedup: float, threads: int) -> float:
    if threads < 2:
        raise ValueError("the serial fraction needs N > 1")
    return (1 / speedup - 1 / threads) / (1 - 1 / threads)


@dataclass(frozen=True)
class KarpFlattRow:
    configuration: Configuration
    speedup: float
    speedup_low: float
    speedup_high: float

    @property
    def serial_fraction(self) -> float:
        return serial_fraction(self.speedup, self.configuration.threads)

    @property
    def interval(self) -> tuple[float, float]:
        threads = self.configuration.threads
        return serial_fraction(self.speedup_high, threads), serial_fraction(self.speedup_low, threads)

    def cells(self) -> list[CsvCell]:
        low, high = self.interval
        return [*self.configuration.cells(), number(self.speedup), number(self.serial_fraction), number(low), number(high)]


def karp_flatt_rows(scaling: Iterable[dict[str, str]]) -> list[KarpFlattRow]:
    return [
        KarpFlattRow(
            Configuration(row["environment"], row["workload"], row["input"], parse_k(row["k"]), int(row["threads"])),
            float(row["speedup"]),
            float(row["speedup_low"]),
            float(row["speedup_high"]),
        )
        for row in scaling
        if int(row["threads"]) > 1
    ]


def write_karp_flatt(rows: list[KarpFlattRow], output: TextIO) -> None:
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(KARP_FLATT_COLUMNS)
    for row in rows:
        writer.writerow(row.cells())
