"""Run the native runner once and store its CSV and context like a browser run.

Usage: python3 -m harness.native --run ID --query "workload=...&threads=..."
       [--executable bench/target/release/native] [--cpus 0,2,4,6,8,10,12,14]
       [--order-seed S] [--order-position P] [--results data/raw]
       [--scope-user USER] [--harness-cpus 16-31]
"""

from harness.native.interface import BUILD_INFO_FLAG, COLUMNS_SINCE_SCHEMA_3, CSV_HEADER, RESERVED_KEYS, query_to_flags
from harness.native.run import DEFAULT_TIMEOUT_SECONDS, NativeRun, NativeRunFailed, children_cpu_seconds

__all__ = [
    "BUILD_INFO_FLAG",
    "COLUMNS_SINCE_SCHEMA_3",
    "CSV_HEADER",
    "DEFAULT_TIMEOUT_SECONDS",
    "RESERVED_KEYS",
    "NativeRun",
    "NativeRunFailed",
    "children_cpu_seconds",
    "query_to_flags",
]
