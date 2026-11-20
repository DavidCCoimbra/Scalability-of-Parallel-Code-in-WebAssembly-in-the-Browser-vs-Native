"""The environment check a strict campaign passes on every start."""

from pathlib import Path
from typing import Protocol

from harness.context import utc_now
from harness.environment import EnvironmentCheck, write_sysinfo


class EnvironmentNotReady(RuntimeError):
    pass


class EnvironmentGate(Protocol):
    def problems(self, mask: str) -> list[str]: ...

    def record(self, directory: Path, problems: list[str]) -> Path: ...


class HostEnvironment:
    def __init__(self, browsers: Path, mask: str, hybrid: bool = False):
        self.browsers = browsers
        self.mask = mask
        self.hybrid = hybrid

    def problems(self, mask: str) -> list[str]:
        return EnvironmentCheck().problems(mask, self.hybrid)

    def record(self, directory: Path, problems: list[str]) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{utc_now().replace(':', '')}.json"
        write_sysinfo(path, self.mask, self.browsers, problems)
        return path
