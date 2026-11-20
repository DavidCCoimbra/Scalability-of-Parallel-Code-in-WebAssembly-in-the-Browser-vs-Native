"""The cgroup cpuset shield that keeps the rest of the system off the measured CPUs."""

from pathlib import Path

from harness.context import UNAVAILABLE, format_cpus, read_text, shield_overlaps
from harness.context.sysfs import CGROUP_ROOT

SHIELDED_UNITS = ("system.slice", "user.slice", "init.scope")
EFFECTIVE_CPUS = "cpuset.cpus.effective"


class CgroupShield:
    def __init__(self, root: Path = Path("/")):
        self.root = root

    def effective(self, unit: str) -> str | None:
        return read_text(self.root / CGROUP_ROOT / unit / EFFECTIVE_CPUS)

    def units(self) -> dict[str, str | None]:
        return {unit: self.effective(unit) for unit in SHIELDED_UNITS}

    def state(self) -> dict[str, str] | str:
        cpus = self.units()
        known = {unit: value for unit, value in cpus.items() if value is not None}
        return UNAVAILABLE if len(known) < len(cpus) else known

    def problems(self, mask: str) -> list[str]:
        cpus = self.units()
        missing = [f"{unit} cpuset unavailable" for unit, value in cpus.items() if value is None]
        overlapping = [
            f"{unit} can use measured CPUs {format_cpus(overlap)}" for unit, overlap in shield_overlaps(cpus, mask).items()
        ]
        return missing + overlapping
