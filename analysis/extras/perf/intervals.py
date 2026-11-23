from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

# The perf events of scripts/perf-counters.sh, by the name used in the tables.
EVENTS = {
    "cpu_core/cycles/": "cycles",
    "cpu_core/instructions/": "instructions",
    "cpu_core/mem_inst_retired.lock_loads/": "lock_loads",
    "cpu_core/ocr.demand_rfo.l3_hit.snoop_hitm/": "rfo_hitm",
    "cpu_core/ocr.demand_data_rd.l3_hit.snoop_hitm/": "read_hitm",
}
COUNTERS = tuple(EVENTS.values())
# Counted since the v3 campaigns only: a table has them when the campaign's intervals do.
LATER_EVENTS = {
    "cpu_core/longest_lat_cache.miss/": "llc_misses",
    "cpu_core/mem_load_retired.l2_miss/": "l2_misses",
}
EVENT_NAMES = {**EVENTS, **LATER_EVENTS}
# perf stat -x, prints the share of the interval the event was counted; below 100 it multiplexed.
FULLY_COUNTED = "100.00"


@dataclass(frozen=True)
class Interval:
    end: float
    counts: dict[str, float]


# One perf stat -I segment: "<seconds since start>,<count>,,<event>,<run time>,<percent>,..." rows
# after comment lines. A row not counted, unsupported or multiplexed would read as a false rate, so
# it stops the analysis instead of becoming 0.
def read_segment(csv_path: Path, start: float) -> list[Interval]:
    by_time: dict[float, dict[str, float]] = defaultdict(dict)
    for line in csv_path.read_text().splitlines():
        fields = line.split(",")
        if line.startswith("#") or len(fields) < 6 or fields[3] not in EVENT_NAMES:
            continue
        if fields[5] != FULLY_COUNTED:
            raise ValueError(f"{csv_path}: {fields[3]} not fully counted at {fields[0]} s: {line}")
        by_time[float(fields[0])][EVENT_NAMES[fields[3]]] = float(fields[1])
    return [Interval(start + seconds, counts) for seconds, counts in sorted(by_time.items())]


def read_intervals(counters_dir: Path) -> list[Interval]:
    intervals: list[Interval] = []
    for csv_path in sorted(counters_dir.glob("*.csv")):
        start = float(csv_path.with_suffix(".start").read_text())
        intervals.extend(read_segment(csv_path, start))
    return sorted(intervals, key=lambda interval: interval.end)


def counters_in(intervals: list[Interval]) -> tuple[str, ...]:
    seen = {name for interval in intervals for name in interval.counts}
    return COUNTERS + tuple(name for name in LATER_EVENTS.values() if name in seen)
