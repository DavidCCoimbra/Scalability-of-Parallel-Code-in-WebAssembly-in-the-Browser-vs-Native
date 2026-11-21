import functools
from dataclasses import dataclass
from pathlib import Path

from analysis.campaign import Context, read_json
from harness.context import DEFAULT_PASSES, validate

CLOCK_RESOLUTION_KEY = "clockResolutionNs"


def integer(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


# The context JSON of one run, read in one place: each field has one name, one type and one
# default here, whatever command asks for it.
@dataclass(frozen=True)
class RunContext:
    raw: Context

    # The runs record their passes K; the runs stored before passes existed ran one.
    @property
    def passes(self) -> int:
        passes = integer(self.raw.get("passes"))
        return DEFAULT_PASSES if passes is None else passes

    # Rows per task for the filter, KB for the local histogram; none is Rayon's adaptive split.
    @property
    def grain(self) -> int | None:
        return integer(self.raw.get("grain"))

    @property
    def order_position(self) -> int | None:
        return integer(self.raw.get("orderPosition"))

    @property
    def foreign_cpu_seconds(self) -> float | None:
        value = self.raw.get("foreignCpuSeconds")
        return value if isinstance(value, (int, float)) else None

    # Browser runs record the resolution in the page metadata; native runs record it in the build block.
    @property
    def clock_resolution_ns(self) -> int | None:
        resolution = self.raw.get(CLOCK_RESOLUTION_KEY)
        if isinstance(resolution, int):
            return resolution
        build = self.raw.get("build")
        if isinstance(build, dict) and isinstance(build.get(CLOCK_RESOLUTION_KEY), int):
            built: int = build[CLOCK_RESOLUTION_KEY]
            return built
        return None

    def above_foreign_cpu(self, threshold: float) -> bool:
        seconds = self.foreign_cpu_seconds
        return seconds is not None and seconds > threshold

    def strict_problems(self, pinned: dict[str, str], hybrid: bool = False) -> list[str]:
        problems: list[str] = validate(self.raw, strict=True, pinned=pinned, hybrid=hybrid)
        return problems


# Several checks of one command ask for the same run; the files of a stored campaign do not change.
@functools.lru_cache(maxsize=None)
def run_context(directory: Path, run_id: str) -> RunContext:
    return RunContext(read_json(directory / f"{run_id}.json"))
