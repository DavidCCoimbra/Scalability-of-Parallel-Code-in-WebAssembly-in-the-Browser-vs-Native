"""Context recorded with every result: host state and launch settings."""

from harness.context.cpu_mask import CPU_RANGE, format_cpus, parse_cpu_mask, shield_overlaps
from harness.context.host import HostFields, LinuxHost, MachineFields, host_fields
from harness.context.json_value import JsonObject, JsonValue
from harness.context.provenance import command_output, git_commit, loadavg, sha256_file, utc_now
from harness.context.record import CpuTimeMethod, RunContext, to_camel
from harness.context.run_environment import BROWSERS, RunEnvironment
from harness.context.run_query import DEFAULT_PASSES, grain_of_query, passes_of_query
from harness.context.results import RunFiles, annotate, refuse_reused_run, run_files_exist
from harness.context.sysfs import read_text
from harness.context.unavailable import UNAVAILABLE, is_known
from harness.context.units import round_seconds
from harness.context.validation import (
    BUILD_FIELDS,
    LATER_KEYS,
    REQUIRED_KEYS,
    SMT_DISABLED,
    STRICT_KEYS,
    build_problems,
    strict_problems,
    topology_problems,
    validate,
)

__all__ = [
    "BROWSERS",
    "BUILD_FIELDS",
    "CPU_RANGE",
    "DEFAULT_PASSES",
    "LATER_KEYS",
    "REQUIRED_KEYS",
    "SMT_DISABLED",
    "STRICT_KEYS",
    "UNAVAILABLE",
    "CpuTimeMethod",
    "HostFields",
    "JsonObject",
    "JsonValue",
    "LinuxHost",
    "MachineFields",
    "RunContext",
    "RunEnvironment",
    "RunFiles",
    "annotate",
    "build_problems",
    "command_output",
    "format_cpus",
    "git_commit",
    "host_fields",
    "is_known",
    "loadavg",
    "parse_cpu_mask",
    "grain_of_query",
    "passes_of_query",
    "read_text",
    "refuse_reused_run",
    "round_seconds",
    "run_files_exist",
    "sha256_file",
    "shield_overlaps",
    "strict_problems",
    "to_camel",
    "topology_problems",
    "utc_now",
    "validate",
]
