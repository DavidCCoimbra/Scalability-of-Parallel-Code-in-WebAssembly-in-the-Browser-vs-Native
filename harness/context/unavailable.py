"""The marker for a value the harness could not read."""

UNAVAILABLE = "unavailable"
UNKNOWN_VALUES: tuple[object, ...] = (UNAVAILABLE, None, "")


def is_known(value: object) -> bool:
    return value not in UNKNOWN_VALUES
