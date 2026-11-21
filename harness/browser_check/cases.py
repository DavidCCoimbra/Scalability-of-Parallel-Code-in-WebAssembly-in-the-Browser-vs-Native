"""The cases the CI correctness check runs in every environment."""

from dataclasses import dataclass

from harness.campaign.capabilities import SEQUENTIAL_THREADS

WIDTH = 1024
HEIGHT = 1024
WARMUP = 1
ITERATIONS = 2
SIZE = f"width={WIDTH}&height={HEIGHT}&warmup={WARMUP}&iters={ITERATIONS}"
THREAD_COUNTS = (1, 2, 4)
HISTOGRAM_KS = (1, 4, 16, 256)
NOISE_WORKLOADS = ("filter", "sort", "sort-unstable")
HISTOGRAM_WORKLOADS = ("hist-atomic", "hist-local", "hist-atomic-private", "hist-atomic-packed")
SEQUENTIAL_FILTER = "filter-seq"
SEQUENTIAL_HISTOGRAM = "hist-seq"


@dataclass(frozen=True)
class Case:
    workload: str
    k: int | None
    threads: int

    @property
    def input_label(self) -> str:
        return "noise" if self.k is None else f"k={self.k}"

    @property
    def input_query(self) -> str:
        return "input=noise" if self.k is None else f"input=few&k={self.k}"

    @property
    def name(self) -> str:
        return f"{self.workload} {self.input_label} N={self.threads}"

    @property
    def query(self) -> str:
        return f"workload={self.workload}&{self.input_query}&{SIZE}&threads={self.threads}"

    def run_id(self, environment: str) -> str:
        return f"check-{environment}-{self.name.replace(' ', '-').replace('=', '')}"


CASES = tuple(Case(workload, None, threads) for workload in NOISE_WORKLOADS for threads in THREAD_COUNTS) + tuple(
    Case(workload, k, threads) for workload in HISTOGRAM_WORKLOADS for k in HISTOGRAM_KS for threads in THREAD_COUNTS
)
CASES += (Case(SEQUENTIAL_FILTER, None, SEQUENTIAL_THREADS),) + tuple(Case(SEQUENTIAL_HISTOGRAM, k, SEQUENTIAL_THREADS) for k in HISTOGRAM_KS)
