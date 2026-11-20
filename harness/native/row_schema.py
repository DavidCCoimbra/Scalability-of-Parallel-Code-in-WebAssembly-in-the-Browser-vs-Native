"""CSV rows of every schema version, read as rows of the current one.

Schema 1 is every build before v2: the first 13 columns of CSV_HEADER and no
schema column. Schema 2 (v2) appends the probe, memory, buffer address,
pitch, palette, schema, passes and grain columns. A schema 1 row gets the
values those builds implied; what they did not record (memory, addresses)
stays empty.
"""

from collections.abc import Mapping

from harness.context.run_query import DEFAULT_PASSES
from harness.native.interface import CSV_HEADER

LEGACY_SCHEMA = 1
SCHEMA_COLUMN = "schema"
# Schema 1 builds calibrated one probe, the empty broadcast.
LEGACY_PROBE = "broadcast"
CALIBRATION_SAMPLE_PHASES = ("calibration-warm", "calibration-cold")
# Schema 1 builds had one palette, the spread one (i * 256 / k).
LEGACY_PALETTE = "spread"
FEW_COLORS = "few"

Row = dict[str, object]


def schema_of(row: Mapping[str, object]) -> int:
    value = row.get(SCHEMA_COLUMN)
    return int(str(value)) if value else LEGACY_SCHEMA


def upgraded(row: Mapping[str, object], context: Mapping[str, object]) -> Row:
    """`row` with every column of CSV_HEADER; `context` is the run's JSON, which recorded the
    passes and the grain of schema 1 runs."""
    complete: Row = {column: "" for column in CSV_HEADER.split(",")}
    complete.update({key: value for key, value in row.items() if value is not None})
    if schema_of(row) == LEGACY_SCHEMA:
        complete.update(legacy_values(row, context))
    return complete


def legacy_values(row: Mapping[str, object], context: Mapping[str, object]) -> Row:
    grain = context.get("grain")
    return {
        SCHEMA_COLUMN: str(LEGACY_SCHEMA),
        "probe": LEGACY_PROBE if row.get("phase") in CALIBRATION_SAMPLE_PHASES else "",
        "palette": LEGACY_PALETTE if row.get("input") == FEW_COLORS else "",
        "pitch": row.get("width", ""),
        "passes": str(context.get("passes", DEFAULT_PASSES)),
        "grain": "" if grain is None else str(grain),
    }
