"""One workload of a campaign: what to run on which input."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from harness.campaign.capabilities import ATOMIC_HISTOGRAM, FILTER, LOCAL_HISTOGRAM, NONE, SEQUENTIAL, Capabilities
from harness.campaign.choices import parse_choice


class Workload(StrEnum):
    FILTER = "filter"
    HIST_ATOMIC = "hist-atomic"
    HIST_LOCAL = "hist-local"
    FILTER_SEQ = "filter-seq"
    HIST_SEQ = "hist-seq"
    HIST_ATOMIC_PRIVATE = "hist-atomic-private"
    HIST_ATOMIC_PACKED = "hist-atomic-packed"
    SORT = "sort"
    SORT_UNSTABLE = "sort-unstable"

    @property
    def capabilities(self) -> Capabilities:
        return CAPABILITIES[self]


class InputKind(StrEnum):
    NOISE = "noise"
    FEW = "few"


# v2: which k grey levels a few-colors input uses; spread (i * 256 / k) is the study's input,
# consecutive (0..k) puts the k counters of the packed histogram on shared cache lines.
class Palette(StrEnum):
    SPREAD = "spread"
    CONSECUTIVE = "consecutive"


CAPABILITIES = {
    Workload.FILTER: FILTER,
    Workload.HIST_ATOMIC: ATOMIC_HISTOGRAM,
    Workload.HIST_LOCAL: LOCAL_HISTOGRAM,
    Workload.FILTER_SEQ: SEQUENTIAL,
    Workload.HIST_SEQ: SEQUENTIAL,
    Workload.HIST_ATOMIC_PRIVATE: NONE,
    Workload.HIST_ATOMIC_PACKED: NONE,
    Workload.SORT: NONE,
    Workload.SORT_UNSTABLE: NONE,
}


def workloads_that(accepts: str) -> str:
    return ", ".join(workload for workload in Workload if getattr(workload.capabilities, accepts))
WORKLOAD_KEYS = {"workload", "input", "k", "warmup", "passes", "grain", "pitch", "palette"}


@dataclass(frozen=True)
class WorkloadSpec:
    workload: Workload
    input: InputKind
    k: int | None = None
    warmup: int | None = None
    passes: int | None = None
    grain: int | None = None
    pitch: int | None = None
    palette: Palette | None = None

    def __post_init__(self) -> None:
        if (self.input == InputKind.FEW) != (self.k is not None):
            raise ValueError(f"k is required for few and only for few: {self}")
        if self.palette is not None and self.input != InputKind.FEW:
            raise ValueError(f"palette is only for few: {self}")
        if self.warmup is not None and self.warmup < 0:
            raise ValueError(f"warmup must be at least 0: {self}")
        if self.passes is not None:
            check_passes(self.workload, self.passes)
        if self.grain is not None:
            check_grain(self.workload, self.grain)
        if self.pitch is not None:
            check_pitch(self.workload, self.pitch)

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "WorkloadSpec":
        unknown = set(data) - WORKLOAD_KEYS
        if unknown:
            raise ValueError(f"unknown workload keys: {', '.join(sorted(unknown))}")
        problem = f"unknown workload or input in {dict(data)}"
        return cls(
            workload=parse_choice(Workload, data.get("workload"), problem),
            input=parse_choice(InputKind, data.get("input"), problem),
            k=optional_int(data.get("k")),
            warmup=optional_int(data.get("warmup")),
            passes=optional_int(data.get("passes")),
            grain=optional_int(data.get("grain")),
            pitch=optional_int(data.get("pitch")),
            palette=None if data.get("palette") is None else parse_choice(Palette, data.get("palette"), problem),
        )

    @property
    def label(self) -> str:
        input_label = InputKind.NOISE.value if self.k is None else f"k{self.k}"
        grain = "" if self.grain is None else f"-g{self.grain}"
        pitch = "" if self.pitch is None else f"-p{self.pitch}"
        palette = "" if self.palette is None else f"-{self.palette}"
        return f"{input_label}{palette}{grain}{pitch}"

    @property
    def query(self) -> str:
        k = f"&k={self.k}" if self.k is not None else ""
        grain = f"&grain={self.grain}" if self.grain is not None else ""
        pitch = f"&pitch={self.pitch}" if self.pitch is not None else ""
        palette = f"&palette={self.palette}" if self.palette is not None else ""
        return f"workload={self.workload}&input={self.input}{k}{palette}{grain}{pitch}"


def check_passes(workload: Workload, passes: int) -> None:
    if passes < 1:
        raise ValueError(f"passes must be at least 1, found {passes} for {workload}")
    if passes > 1 and not workload.capabilities.repeats_identically:
        raise ValueError(f"{workload} cannot take several passes; only {workloads_that('repeats_identically')} can")


def check_grain(workload: Workload, grain: int) -> None:
    if grain < 1:
        raise ValueError(f"grain must be at least 1, found {grain} for {workload}")
    if not workload.capabilities.takes_grain:
        raise ValueError(f"{workload} takes no grain; only {workloads_that('takes_grain')} do")


# The bench also refuses a pitch below the width, which only the campaign knows.
def check_pitch(workload: Workload, pitch: int) -> None:
    if pitch < 1:
        raise ValueError(f"pitch must be at least 1, found {pitch} for {workload}")
    if not workload.capabilities.takes_pitch:
        raise ValueError(f"{workload} takes no pitch; only {workloads_that('takes_pitch')} does")


def optional_int(value: object) -> int | None:
    if value is None or (isinstance(value, int) and not isinstance(value, bool)):
        return value
    raise ValueError(f"expected an integer, found {value!r}")
