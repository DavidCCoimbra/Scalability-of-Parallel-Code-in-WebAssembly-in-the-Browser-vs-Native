import math
from dataclasses import dataclass

from analysis.configuration import Configuration
from analysis.inference.question import Question
from analysis.stats.bootstrap import Interval


@dataclass(frozen=True)
class Contrast:
    question: Question
    configuration: Configuration
    estimate: float
    interval: Interval
    primary: bool = False
    primary_interval: Interval | None = None
    p: float | None = None
    holm_p: float | None = None
    rejected: bool | None = None

    @property
    def effect(self) -> float:
        return math.exp(self.estimate)

    @property
    def environment(self) -> str:
        return self.configuration.environment

    @property
    def workload(self) -> str:
        return self.configuration.workload

    @property
    def input(self) -> str:
        return self.configuration.input

    @property
    def k(self) -> int | None:
        return self.configuration.k

    @property
    def threads(self) -> int:
        return self.configuration.threads
