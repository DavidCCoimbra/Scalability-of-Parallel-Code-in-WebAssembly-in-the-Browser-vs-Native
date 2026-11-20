"""Keep the rest of the system off the measured CPUs and measure what still lands there.

Usage: python3 -m harness.shield check --cpus 0,2,4,6,8,10,12,14
"""

from harness.shield.cgroup import SHIELDED_UNITS, CgroupShield
from harness.shield.confinement import check_confinement, confine, pin_current_process
from harness.shield.cpu_time import BUSY_FIELDS, CpuSplit, CpuTimes, CpuUsage, process_session_seconds
from harness.shield.processes import descendants, escaped_processes, process_table
from harness.shield.scope import (
    BENCH_SLICE,
    SESSION_VARIABLES,
    UNIT_NAME,
    scope_cpu_seconds,
    scope_prefix,
    scope_stop_command,
    scope_unit,
    slice_cgroup,
    stop_scope,
)

__all__ = [
    "BENCH_SLICE",
    "BUSY_FIELDS",
    "SESSION_VARIABLES",
    "SHIELDED_UNITS",
    "UNIT_NAME",
    "CgroupShield",
    "CpuSplit",
    "CpuTimes",
    "CpuUsage",
    "check_confinement",
    "confine",
    "descendants",
    "escaped_processes",
    "pin_current_process",
    "process_session_seconds",
    "process_table",
    "scope_cpu_seconds",
    "scope_prefix",
    "scope_stop_command",
    "scope_unit",
    "slice_cgroup",
    "stop_scope",
]
