"""Is the machine prepared to measure?"""

from pathlib import Path

from harness.context import LinuxHost, format_cpus, parse_cpu_mask, topology_problems
from harness.context.validation import REQUIRED_GOVERNOR, REQUIRED_TURBO, SMT_DISABLED
from harness.environment.topology import p_core_mask
from harness.shield import CgroupShield


class EnvironmentCheck:
    def __init__(self, root: Path = Path("/")):
        self.root = root

    def problems(self, mask: str, hybrid: bool = False) -> list[str]:
        host = LinuxHost(self.root, parse_cpu_mask(mask))
        return [
            *frequency_and_smt_problems(host),
            *topology_problems({"cpuMask": mask, "pCpus": host.p_cpus(), "maskSiblings": host.mask_siblings()}, hybrid),
            *self.mask_problems(mask, hybrid),
            *[f"shield: {problem}" for problem in CgroupShield(self.root).problems(mask)],
        ]

    def mask_problems(self, mask: str, hybrid: bool) -> list[str]:
        expected = p_core_mask(self.root)
        if hybrid and expected is None:
            return ["hybrid cpuMask cannot be checked: the P-cores are unknown"]
        if hybrid:
            return hybrid_mask_problems(mask, expected)
        if expected != mask:
            return [f"cpuMask is {mask}, but the physical P-cores are {expected}"]
        return []


def frequency_and_smt_problems(host: LinuxHost) -> list[str]:
    problems = []
    if (turbo := host.turbo()) != REQUIRED_TURBO:
        problems.append(f"turbo is {turbo}, not {REQUIRED_TURBO}")
    if (governor := host.governor()) != REQUIRED_GOVERNOR:
        problems.append(f"governor is {governor}, not {REQUIRED_GOVERNOR}")
    if (smt := host.smt()) not in SMT_DISABLED:
        problems.append(f"smt is {smt}, not off")
    return problems


def hybrid_mask_problems(mask: str, p_cores: str | None) -> list[str]:
    missing = sorted(set(parse_cpu_mask(p_cores) or []) - set(parse_cpu_mask(mask) or []))
    if missing:
        return [f"hybrid cpuMask leaves out P-cores: {format_cpus(missing)}"]
    return []
