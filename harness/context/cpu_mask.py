"""CPU masks in the kernel list format ("0-3,8"), as taskset and cpuset files use them."""

import re
from collections.abc import Iterable, Mapping

CPU_RANGE = re.compile(r"(\d+)(?:-(\d+))?")
LIST_SEPARATOR = ","


def parse_cpu_mask(mask: str | None) -> list[int] | None:
    if not mask:
        return None
    cpus: list[int] = []
    for part in mask.split(LIST_SEPARATOR):
        cpus.extend(parse_range(part, mask))
    return cpus


def parse_range(part: str, mask: str) -> range:
    match = CPU_RANGE.fullmatch(part)
    if not match:
        raise ValueError(f"malformed CPU mask {mask!r}")
    start, end = int(match.group(1)), int(match.group(2) or match.group(1))
    if end < start:
        raise ValueError(f"malformed CPU mask {mask!r}")
    return range(start, end + 1)


def format_cpus(cpus: Iterable[int]) -> str:
    return LIST_SEPARATOR.join(map(str, cpus))


def shield_overlaps(shield: Mapping[str, str | None], mask: str) -> dict[str, list[int]]:
    try:
        measured = set(parse_cpu_mask(mask) or [])
    except ValueError:
        return {}
    overlaps = {unit: sorted(measured & set(parse_cpu_mask(cpus) or [])) for unit, cpus in shield.items() if cpus}
    return {unit: cpus for unit, cpus in overlaps.items() if cpus}
