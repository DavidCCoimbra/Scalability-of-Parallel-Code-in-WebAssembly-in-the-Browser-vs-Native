from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any

from harness.collect import Row


class Environment(StrEnum):
    NATIVE = "native"
    CHROME = "chrome"
    FIREFOX = "firefox"


ENVIRONMENTS = (Environment.NATIVE, Environment.CHROME, Environment.FIREFOX)
BROWSERS = (Environment.CHROME, Environment.FIREFOX)


# Workload names stay plain strings in Configuration: the extras campaigns add workloads (sort,
# packed and private atomics) that the analysis handles without naming them, so this enum only names
# the workloads the analysis plan refers to.
class Workload(StrEnum):
    FILTER = "filter"
    HIST_ATOMIC = "hist-atomic"
    HIST_LOCAL = "hist-local"
    FILTER_SEQ = "filter-seq"
    HIST_SEQ = "hist-seq"


# The references without Rayon. They have one thread count, so they are no scaling curve: the
# scaling commands leave them out and the sequential table reads them.
SEQUENTIAL_WORKLOADS = frozenset({Workload.FILTER_SEQ, Workload.HIST_SEQ})


class Input(StrEnum):
    NOISE = "noise"
    FEW_COLORS = "few"


CsvCell = str | int


@dataclass(frozen=True, order=True)
class Configuration:
    environment: str
    workload: str
    input: str
    k: int | None
    threads: int

    def baseline(self) -> "Configuration":
        return self.at_threads(1)

    def at_threads(self, threads: int) -> "Configuration":
        return replace(self, threads=threads)

    def in_environment(self, environment: str) -> "Configuration":
        return replace(self, environment=environment)

    def as_workload(self, workload: str) -> "Configuration":
        return replace(self, workload=workload)

    @property
    def is_browser(self) -> bool:
        return self.environment in BROWSERS

    @property
    def label(self) -> str:
        return f"{self.environment} {workload_label(self.workload, self.k)} N={self.threads}"

    def cells(self) -> list[CsvCell]:
        return [self.environment, self.workload, self.input, "" if self.k is None else self.k, self.threads]

    def as_json(self) -> dict[str, Any]:
        return {
            "environment": self.environment,
            "workload": self.workload,
            "input": self.input,
            "k": self.k,
            "threads": self.threads,
        }


def workload_label(workload: str, k: int | None) -> str:
    return workload if k is None else f"{workload} k{k}"


def workload_order(key: tuple[str, int | None]) -> tuple[str, int]:
    workload, k = key
    return workload, k or 0


def parse_k(text: str) -> int | None:
    return int(text) if text else None


def configuration_of(row: Row) -> Configuration:
    return Configuration(row["env"], row["workload"], row["input"], parse_k(row["k"]), int(row["threads"]))
