"""Rounding of the durations stored in results."""

MILLISECOND_DIGITS = 3


def round_seconds(seconds: float) -> float:
    return round(seconds, MILLISECOND_DIGITS)
