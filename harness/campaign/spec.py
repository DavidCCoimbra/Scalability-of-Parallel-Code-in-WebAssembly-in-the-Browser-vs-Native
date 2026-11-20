"""The campaign spec: every parameter of one campaign, read from its JSON file."""

import getpass
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path

from harness.campaign.choices import parse_choice
from harness.campaign.fields import SpecFields
from harness.campaign.planned_run import PlannedRun
from harness.campaign.workload import WorkloadSpec, check_passes
from harness.context import BROWSERS, DEFAULT_PASSES, JsonObject, RunEnvironment, to_camel
from harness.paths import NATIVE_TARGET
from harness.server import MAX_RUN_ID_LENGTH
from harness.shield import UNIT_NAME

CURRENT_USER = "$USER"
MAX_SESSIONS = 99
DEFAULT_TIMEOUT_SECONDS = 300.0
ENVIRONMENT_NAMES = tuple(environment.value for environment in RunEnvironment)
SPEC_KEYS = {
    "name",
    "orderSeed",
    "environments",
    "workloads",
    "threads",
    "repetitions",
    "width",
    "height",
    "heightPerThread",
    "warmup",
    "iterations",
    "calibration",
    "cpus",
    "harnessCpus",
    "hybrid",
    "scopeUser",
    "headless",
    "startDelayMs",
    "timeoutSeconds",
    "discardFirstLaunch",
    "strict",
    "build",
    "passes",
    "comment",
}
# Keys added after the main campaign: left out of the stored spec while unset, so that campaigns
# started before them still resume against an identical spec.
UNSET_LATER_KEYS = {"passes": DEFAULT_PASSES, "comment": None}


class BuildVariant(StrEnum):
    BASELINE = "baseline"
    AVX2 = "avx2"
    SCALAR = "scalar"


BUILD_NAMES = tuple(variant.value for variant in BuildVariant)


# The field order is the key order of the spec in campaign.json; keep it.
@dataclass(frozen=True)
class CampaignSpec:
    name: str
    order_seed: int
    environments: tuple[RunEnvironment, ...]
    workloads: tuple[WorkloadSpec, ...]
    threads: tuple[int, ...]
    repetitions: int
    width: int
    height: int
    warmup: int
    iterations: int
    calibration: int
    cpus: str | None = None
    harness_cpus: str | None = None
    scope_user: str | None = None
    headless: bool = True
    start_delay_ms: int = 0
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    discard_first_launch: bool = False
    strict: bool = False
    height_per_thread: int | None = None
    build: BuildVariant = BuildVariant.BASELINE
    hybrid: bool = False
    passes: int = DEFAULT_PASSES
    comment: str | None = None

    def __post_init__(self) -> None:
        if not UNIT_NAME.fullmatch(self.name):
            raise ValueError(f"campaign name {self.name!r} must be letters, digits, - or _")
        if not self.environments:
            raise ValueError(f"environments must be a non-empty subset of {ENVIRONMENT_NAMES}")
        if not self.workloads or not self.threads or any(threads < 1 for threads in self.threads):
            raise ValueError("workloads and threads must be non-empty, threads at least 1")
        if self.repetitions < 1 or self.iterations < 1 or min(self.width, self.height) < 1:
            raise ValueError("repetitions, iterations, width and height must be at least 1")
        if self.height_per_thread is not None and self.height_per_thread < 1:
            raise ValueError("heightPerThread must be at least 1")
        for workload in self.workloads:
            check_passes(workload.workload, self.passes_of(workload))
        if self.strict and not self.cpus:
            raise ValueError("a strict campaign needs a CPU mask (cpus)")
        self.check_run_id_length()

    def check_run_id_length(self) -> None:
        # Run ids name files, systemd units and the server's run parameter, which caps their length.
        longest = max(len(run.run_id) for run in self.every_run_shape())
        if longest > MAX_RUN_ID_LENGTH:
            raise ValueError(
                f"campaign name {self.name!r} makes run ids of {longest} characters; the limit is {MAX_RUN_ID_LENGTH}"
            )

    def every_run_shape(self) -> list[PlannedRun]:
        last = len(self.environments) * len(self.workloads) * len(self.threads) * self.repetitions - 1
        return [
            PlannedRun(last, environment, workload, threads, self.repetitions - 1, self.name, discarded, MAX_SESSIONS)
            for environment in self.environments
            for workload in self.workloads
            for threads in self.threads
            for discarded in (False, True)
        ]

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "CampaignSpec":
        unknown = set(data) - SPEC_KEYS
        if unknown:
            raise ValueError(f"unknown campaign keys: {', '.join(sorted(unknown))}")
        fields = SpecFields(data)
        return cls(
            name=fields.text("name"),
            order_seed=fields.integer("orderSeed"),
            environments=parse_environments(fields.items("environments")),
            workloads=tuple(WorkloadSpec.from_json(workload) for workload in fields.objects("workloads")),
            threads=fields.integers("threads"),
            repetitions=fields.integer("repetitions"),
            width=fields.integer("width"),
            height=fields.integer("height"),
            warmup=fields.integer("warmup"),
            iterations=fields.integer("iterations"),
            calibration=fields.integer("calibration"),
            cpus=fields.optional_text("cpus"),
            harness_cpus=fields.optional_text("harnessCpus"),
            scope_user=fields.optional_text("scopeUser"),
            headless=fields.flag("headless", True),
            start_delay_ms=fields.integer_or("startDelayMs", 0),
            timeout_seconds=fields.number("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS),
            discard_first_launch=fields.flag("discardFirstLaunch", False),
            strict=fields.flag("strict", False),
            height_per_thread=fields.optional_integer("heightPerThread"),
            build=parse_choice(BuildVariant, fields.raw("build", BuildVariant.BASELINE), f"build must be one of {BUILD_NAMES}"),
            hybrid=fields.flag("hybrid", False),
            passes=fields.integer_or("passes", DEFAULT_PASSES),
            comment=fields.optional_text("comment"),
        )

    def to_json(self) -> JsonObject:
        data = asdict(self)
        data["workloads"] = [{key: value for key, value in asdict(w).items() if value is not None} for w in self.workloads]
        for key, unset in UNSET_LATER_KEYS.items():
            if data[key] == unset:
                del data[key]
        return {to_camel(key): list(value) if isinstance(value, tuple) else value for key, value in data.items()}

    @property
    def resolved_scope_user(self) -> str | None:
        return getpass.getuser() if self.scope_user == CURRENT_USER else self.scope_user

    @property
    def uses_browsers(self) -> bool:
        return any(environment in BROWSERS for environment in self.environments)

    @property
    def native_binary(self) -> Path:
        variant = "" if self.build == BuildVariant.BASELINE else f"{self.build}/"
        return NATIVE_TARGET / f"{variant}release/native"

    def height_of(self, threads: int) -> int:
        return self.height if self.height_per_thread is None else self.height_per_thread * threads

    def warmup_of(self, workload: WorkloadSpec) -> int:
        return self.warmup if workload.warmup is None else workload.warmup

    def passes_of(self, workload: WorkloadSpec) -> int:
        return self.passes if workload.passes is None else workload.passes

    # One pass leaves the query as before passes existed, so the native runner and the page see
    # exactly the arguments of the earlier campaigns.
    def query(self, run: PlannedRun) -> str:
        passes = self.passes_of(run.workload)
        return (
            f"{run.workload.query}&threads={run.threads}&width={self.width}&height={self.height_of(run.threads)}"
            f"&warmup={self.warmup_of(run.workload)}&iters={self.iterations}&calibration={self.calibration}"
            + ("" if passes == DEFAULT_PASSES else f"&passes={passes}")
        )


def parse_environments(names: list[object]) -> tuple[RunEnvironment, ...]:
    problem = f"environments must be a non-empty subset of {ENVIRONMENT_NAMES}"
    return tuple(parse_choice(RunEnvironment, name, problem) for name in names)
