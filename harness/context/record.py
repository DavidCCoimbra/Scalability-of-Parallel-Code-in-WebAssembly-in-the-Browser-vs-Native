"""The context stored with every run, in the field order of the JSON files."""

from dataclasses import asdict, dataclass
from enum import StrEnum

from harness.context.json_value import JsonObject, JsonValue
from harness.context.unavailable import UNAVAILABLE


class CpuTimeMethod(StrEnum):
    SCOPE = "scope"
    SESSION = "session"
    RUSAGE = "rusage"


@dataclass(frozen=True)
class RunContext:
    commit: str
    cpu_model: str
    governor: str
    turbo: str
    kernel: str
    os: str
    environment: str
    browser_version: str
    cpu_mask: str | None
    smt: str
    p_cpus: str
    mask_siblings: list[str] | str
    headless: bool | None
    launch_flags: list[str]
    order_seed: int | None
    order_position: int | None
    started_at: str
    finished_at: str
    launch_seconds: float
    artifact_sha256: str
    build: JsonValue
    loadavg_before: list[float] | str
    loadavg_after: list[float] | str
    shield: dict[str, str] | str
    run_cpu_seconds: float | str
    run_cpu_method: CpuTimeMethod
    foreign_cpu_seconds: float | str
    start_delay_ms: int
    passes: int
    leftover_processes: int | str
    escaped_processes: int | str
    # The fixed task size of a grain sweep run; None is Rayon's adaptive split.
    grain: int | None = None
    # Per measured CPU: busy seconds in the run and the frequency before and after (ADR 0084).
    cores: JsonValue = UNAVAILABLE
    # The engine settings of a browser run in a campaign with engine arms; None is the engine as shipped.
    engine_arm: JsonValue = None

    def to_json(self) -> JsonObject:
        return {to_camel(key): value for key, value in asdict(self).items()}


def to_camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(word.capitalize() for word in rest)
