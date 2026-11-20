"""Short human-readable durations for the status report."""

from datetime import timedelta

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR


def format_duration(duration: timedelta) -> str:
    total = max(0, round(duration.total_seconds()))
    days, rest = divmod(total, SECONDS_PER_DAY)
    hours, rest = divmod(rest, SECONDS_PER_HOUR)
    minutes, seconds = divmod(rest, SECONDS_PER_MINUTE)
    if days:
        return f"{days}d {hours:02d}h"
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {seconds:02d}s"
    return f"{seconds}s"
