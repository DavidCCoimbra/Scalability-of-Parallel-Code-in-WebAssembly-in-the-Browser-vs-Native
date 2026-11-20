"""The environments a run can measure in."""

from enum import StrEnum


class RunEnvironment(StrEnum):
    NATIVE = "native"
    CHROME = "chrome"
    FIREFOX = "firefox"

    @property
    def is_browser(self) -> bool:
        return self in BROWSERS


BROWSERS = (RunEnvironment.CHROME, RunEnvironment.FIREFOX)
