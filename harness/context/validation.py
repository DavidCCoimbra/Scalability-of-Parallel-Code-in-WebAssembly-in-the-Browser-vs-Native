"""Checks of a stored run context: complete (always) and fit to be measured (strict)."""

from collections.abc import Mapping

from harness.context.cpu_mask import format_cpus, parse_cpu_mask, shield_overlaps
from harness.context.provenance import DIRTY_SUFFIX
from harness.context.unavailable import is_known

REQUIRED_KEYS = (
    "commit",
    "cpuModel",
    "governor",
    "turbo",
    "kernel",
    "os",
    "environment",
    "browserVersion",
    "cpuMask",
    "smt",
    "pCpus",
    "maskSiblings",
    "headless",
    "launchFlags",
    "orderSeed",
    "orderPosition",
    "startedAt",
    "finishedAt",
    "launchSeconds",
    "artifactSha256",
    "build",
    "loadavgBefore",
    "loadavgAfter",
    "shield",
    "runCpuSeconds",
    "runCpuMethod",
    "foreignCpuSeconds",
    "startDelayMs",
    "leftoverProcesses",
    "escapedProcesses",
)
# Written since the cutoff campaign and the grain sweep; runs stored before
# them lack them and mean the default.
LATER_KEYS = ("passes", "grain")
BUILD_FIELDS = ("rustc", "wasmBindgen")
STRICT_KEYS = (
    "commit",
    "cpuModel",
    "governor",
    "turbo",
    "kernel",
    "browserVersion",
    "cpuMask",
    "smt",
    "pCpus",
    "maskSiblings",
    "orderSeed",
    "orderPosition",
    "startedAt",
    "finishedAt",
    "artifactSha256",
    "build",
    "shield",
    "foreignCpuSeconds",
    "leftoverProcesses",
    "escapedProcesses",
)
SMT_DISABLED = ("off", "forceoff", "notsupported")
REQUIRED_GOVERNOR = "performance"
REQUIRED_TURBO = "off"

Context = Mapping[str, object]


def validate(data: Context, strict: bool = False, pinned: Mapping[str, str] | None = None, hybrid: bool = False) -> list[str]:
    problems = [f"missing {key}" for key in REQUIRED_KEYS if key not in data]
    if strict:
        problems += strict_problems(data, pinned or {}, hybrid)
    return problems


def strict_problems(data: Context, pinned: Mapping[str, str], hybrid: bool = False) -> list[str]:
    return StrictValidation(data, pinned, hybrid).problems()


class StrictValidation:
    def __init__(self, data: Context, pinned: Mapping[str, str], hybrid: bool):
        self.data = data
        self.pinned = pinned
        self.hybrid = hybrid

    def problems(self) -> list[str]:
        return [
            *self.unavailable_values(),
            *self.build(),
            *self.shield(),
            *self.escaped_processes(),
            *self.commit(),
            *self.machine(),
            *self.topology(),
            *self.browser_version(),
        ]

    def known(self, key: str) -> bool:
        return is_known(self.data.get(key))

    def unavailable_values(self) -> list[str]:
        return [f"{key} unavailable" for key in STRICT_KEYS if key in self.data and not self.known(key)]

    def build(self) -> list[str]:
        build = self.data.get("build")
        return build_problems(build) if self.known("build") and isinstance(build, Mapping) else []

    def shield(self) -> list[str]:
        shield, mask = self.data.get("shield"), self.data.get("cpuMask")
        if not (self.known("shield") and self.known("cpuMask")) or not isinstance(shield, Mapping) or not isinstance(mask, str):
            return []
        return [
            f"shield: {unit} can use measured CPUs {format_cpus(cpus)}"
            for unit, cpus in shield_overlaps(shield, mask).items()
        ]

    def escaped_processes(self) -> list[str]:
        escaped = self.data.get("escapedProcesses")
        if self.known("escapedProcesses") and escaped != 0:
            return [f"escapedProcesses {escaped}: browser processes left the run scope"]
        return []

    def commit(self) -> list[str]:
        if self.known("commit") and str(self.data["commit"]).endswith(DIRTY_SUFFIX):
            return ["commit is dirty"]
        return []

    def machine(self) -> list[str]:
        problems = []
        governor, turbo, smt = self.data.get("governor"), self.data.get("turbo"), self.data.get("smt")
        if self.known("governor") and governor != REQUIRED_GOVERNOR:
            problems.append(f"governor is {governor}, not {REQUIRED_GOVERNOR}")
        if self.known("turbo") and turbo != REQUIRED_TURBO:
            problems.append(f"turbo is {turbo}, not {REQUIRED_TURBO}")
        if self.known("smt") and smt not in SMT_DISABLED:
            problems.append(f"smt is {smt}, not off")
        return problems

    def topology(self) -> list[str]:
        return topology_problems(self.data, self.hybrid) if self.known("cpuMask") else []

    def browser_version(self) -> list[str]:
        expected = self.pinned.get(str(self.data.get("environment", "")))
        version = str(self.data.get("browserVersion"))
        if expected and self.known("browserVersion") and version.split()[-1] != expected:
            return [f"browserVersion {version} is not the pinned {expected}"]
        return []


def build_problems(build: Mapping[str, object]) -> list[str]:
    return [f"build.{field} unavailable" for field in BUILD_FIELDS if not is_known(build.get(field))]


def topology_problems(data: Context, hybrid: bool = False) -> list[str]:
    try:
        mask = parse_mask_value(data["cpuMask"]) or []
        p_cpus_value = data.get("pCpus")
        p_cpus = set(parse_mask_value(p_cpus_value) or []) if is_known(p_cpus_value) else None
    except ValueError:
        return ["cpuMask is malformed"]
    problems = []
    siblings = data.get("maskSiblings")
    if isinstance(siblings, list) and len(set(siblings)) < len(siblings):
        problems.append("cpuMask has two CPUs on one physical core")
    if p_cpus is not None and not hybrid:
        outside = [cpu for cpu in mask if cpu not in p_cpus]
        if outside:
            problems.append(f"cpuMask includes CPUs that are not P-cores: {format_cpus(outside)}")
    return problems


def parse_mask_value(value: object) -> list[int] | None:
    if value is None or isinstance(value, str):
        return parse_cpu_mask(value)
    raise ValueError(f"malformed CPU mask {value!r}")
