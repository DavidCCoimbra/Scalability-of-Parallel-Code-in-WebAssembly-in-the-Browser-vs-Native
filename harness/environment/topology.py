"""The CPU mask of one CPU per physical P-core."""

from pathlib import Path

from harness.context import format_cpus, parse_cpu_mask, read_text
from harness.context.sysfs import ONLINE_CPUS, P_CORE_CPUS, cpu_file


def p_core_mask(root: Path = Path("/")) -> str | None:
    p_cpus = read_text(root / P_CORE_CPUS)
    if p_cpus is None:
        return None
    p_core_cpus = parse_cpu_mask(p_cpus) or []
    online = set(parse_cpu_mask(read_text(root / ONLINE_CPUS)) or p_core_cpus)
    first_threads = {first_thread(root, cpu) for cpu in p_core_cpus if cpu in online}
    return format_cpus(sorted(first_threads))


# With SMT one physical core shows up as two CPUs that share its execution units;
# core_cpus_list lists them (e.g. "0-1"), and keeping the lowest gives one CPU per P-core, so
# no two benchmark threads share a core.
def first_thread(root: Path, cpu: int) -> int:
    core = read_text(root / cpu_file(cpu, "topology/core_cpus_list")) or str(cpu)
    return min(parse_cpu_mask(core) or [cpu])
