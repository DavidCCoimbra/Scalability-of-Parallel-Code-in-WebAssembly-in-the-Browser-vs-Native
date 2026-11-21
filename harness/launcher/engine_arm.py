"""A named set of engine settings for a browser run: V8 flags for Chrome, preferences for Firefox."""

import re
from collections.abc import Mapping
from dataclasses import dataclass

from harness.context.json_value import JsonObject

ARM_KEYS = {"name", "chromeJsFlags", "firefoxPrefs"}
# The name goes into run ids, so it is as plain as a workload label.
ARM_NAME = re.compile(r"[a-z0-9]+")

PrefValue = str | bool | int


# An arm with no flags and no preferences is the engine as every other campaign runs it.
@dataclass(frozen=True)
class EngineArm:
    name: str
    chrome_js_flags: tuple[str, ...] = ()
    firefox_prefs: tuple[tuple[str, PrefValue], ...] = ()

    def __post_init__(self) -> None:
        if not ARM_NAME.fullmatch(self.name):
            raise ValueError(f"engine arm name {self.name!r} must be lowercase letters and digits")

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "EngineArm":
        unknown = set(data) - ARM_KEYS
        if unknown:
            raise ValueError(f"unknown engine arm keys: {', '.join(sorted(unknown))}")
        flags, prefs = data.get("chromeJsFlags", []), data.get("firefoxPrefs", {})
        if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
            raise ValueError(f"chromeJsFlags must be a list of strings, found {flags!r}")
        if not isinstance(prefs, dict) or not all(isinstance(value, str | bool | int) for value in prefs.values()):
            raise ValueError(f"firefoxPrefs must map preference names to strings, booleans or integers, found {prefs!r}")
        return cls(str(data.get("name", "")), tuple(flags), tuple(prefs.items()))

    def to_json(self) -> JsonObject:
        data: JsonObject = {"name": self.name}
        if self.chrome_js_flags:
            data["chromeJsFlags"] = list(self.chrome_js_flags)
        if self.firefox_prefs:
            data["firefoxPrefs"] = dict(self.firefox_prefs)
        return data
