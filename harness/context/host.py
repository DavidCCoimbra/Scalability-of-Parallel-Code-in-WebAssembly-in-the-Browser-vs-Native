"""State of the measuring host: CPU model, frequency policy, SMT and topology."""

import os
import platform
from pathlib import Path
from typing import TypedDict

from harness.context.cpu_mask import parse_cpu_mask
from harness.context.provenance import command_output, git_commit
from harness.context.sysfs import (
    CPUFREQ_BOOST,
    CPUINFO,
    INTEL_NO_TURBO,
    KERNEL_RELEASE,
    OS_RELEASE,
    P_CORE_CPUS,
    SMT_CONTROL,
    cpu_file,
    read_text,
)
from harness.context.unavailable import UNAVAILABLE

LINUX = "Linux"
TURBO_ON = "on"
TURBO_OFF = "off"
SYSFS_TRUE = "1"
MIXED_PREFIX = "mixed:"
PRETTY_NAME_KEY = "PRETTY_NAME"
MACOS_CPU_MODEL_COMMAND = ["sysctl", "-n", "machdep.cpu.brand_string"]


class MachineFields(TypedDict):
    cpu_model: str
    governor: str
    turbo: str
    kernel: str
    smt: str
    p_cpus: str
    mask_siblings: list[str] | str


class HostFields(MachineFields):
    commit: str
    os: str


class LinuxHost:
    def __init__(self, root: Path = Path("/"), cpus: list[int] | None = None):
        self.root = root
        self.masked = cpus is not None
        self.cpus = cpus if cpus is not None else list(range(os.cpu_count() or 1))

    def cpu_model(self) -> str:
        return self.cpuinfo_field("model name")

    def microcode(self) -> str:
        return self.cpuinfo_field("microcode")

    def cpuinfo_field(self, name: str) -> str:
        for line in self.read_lines(CPUINFO):
            key, _, value = line.partition(":")
            if key.strip() == name:
                return value.strip()
        return UNAVAILABLE

    def distro(self) -> str:
        for line in self.read_lines(OS_RELEASE):
            key, _, value = line.partition("=")
            if key == PRETTY_NAME_KEY:
                return value.strip('"')
        return UNAVAILABLE

    def governor(self) -> str:
        found = {self.read(cpu_file(cpu, "cpufreq/scaling_governor")) for cpu in self.cpus}
        if None in found or not found:
            return UNAVAILABLE
        governors = {governor for governor in found if governor is not None}
        return governors.pop() if len(governors) == 1 else MIXED_PREFIX + ",".join(sorted(governors))

    def turbo(self) -> str:
        # intel_pstate's no_turbo is inverted: 1 means turbo is off.
        # https://docs.kernel.org/admin-guide/pm/intel_pstate.html
        no_turbo = self.read(INTEL_NO_TURBO)
        if no_turbo is not None:
            return TURBO_OFF if no_turbo == SYSFS_TRUE else TURBO_ON
        boost = self.read(CPUFREQ_BOOST)
        if boost is not None:
            return TURBO_ON if boost == SYSFS_TRUE else TURBO_OFF
        return UNAVAILABLE

    def smt(self) -> str:
        return self.read(SMT_CONTROL) or UNAVAILABLE

    def p_cpus(self) -> str:
        return self.read(P_CORE_CPUS) or UNAVAILABLE

    def mask_siblings(self) -> list[str] | str:
        if not self.masked:
            return UNAVAILABLE
        siblings = [self.read(cpu_file(cpu, "topology/thread_siblings_list")) for cpu in self.cpus]
        known = [sibling for sibling in siblings if sibling is not None]
        return UNAVAILABLE if len(known) < len(siblings) else known

    def kernel(self) -> str:
        return self.read(KERNEL_RELEASE) or platform.release()

    def machine_fields(self) -> MachineFields:
        return MachineFields(
            cpu_model=self.cpu_model(),
            governor=self.governor(),
            turbo=self.turbo(),
            kernel=self.kernel(),
            smt=self.smt(),
            p_cpus=self.p_cpus(),
            mask_siblings=self.mask_siblings(),
        )

    def read(self, relative: str) -> str | None:
        return read_text(self.root / relative)

    def read_lines(self, relative: str) -> list[str]:
        return (self.read(relative) or "").splitlines()


def other_machine_fields() -> MachineFields:
    return MachineFields(
        cpu_model=command_output(MACOS_CPU_MODEL_COMMAND),
        governor=UNAVAILABLE,
        turbo=UNAVAILABLE,
        kernel=platform.release(),
        smt=UNAVAILABLE,
        p_cpus=UNAVAILABLE,
        mask_siblings=UNAVAILABLE,
    )


def host_fields(repository: Path, cpu_mask: str | None) -> HostFields:
    if platform.system() == LINUX:
        machine = LinuxHost(cpus=parse_cpu_mask(cpu_mask)).machine_fields()
    else:
        machine = other_machine_fields()
    return HostFields(commit=git_commit(repository), os=platform.system(), **machine)
