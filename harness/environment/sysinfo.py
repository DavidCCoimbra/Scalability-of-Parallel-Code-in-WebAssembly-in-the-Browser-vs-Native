"""The system state recorded next to a campaign: CPU, frequencies, shield, quiet mode, versions."""

import json
import os
from pathlib import Path
from typing import TypedDict

from harness.browsers import load_specs
from harness.context import LinuxHost, command_output, git_commit, loadavg, parse_cpu_mask, read_text, utc_now
from harness.context.sysfs import cpu_file
from harness.environment.host_state import HostState, host_state
from harness.environment.topology import p_core_mask
from harness.paths import BROWSER_VERSIONS, REPOSITORY
from harness.shield import CgroupShield

QUIET_STATE_FILE = "ppc-quiet.state"
FALLBACK_RUNTIME_DIRECTORY = "/tmp"
JSON_INDENT = 2
# Recorded because setup.sh lowers it for the perf diagnostics.
PERF_EVENT_PARANOID = Path("proc/sys/kernel/perf_event_paranoid")


class Frequency(TypedDict):
    min: int | None
    max: int | None
    current: int | None


class QuietMode(TypedDict):
    on: bool
    stopped: list[str]


class Sysinfo(TypedDict):
    cpuModel: str
    kernel: str
    distro: str
    microcode: str
    governor: str
    turbo: str
    smt: str
    pCoreMask: str | None
    frequenciesKHz: dict[str, Frequency]
    shield: dict[str, str] | str
    quietMode: QuietMode
    perfEventParanoid: int | None
    hostState: HostState
    commit: str
    versions: dict[str, str]
    loadavg: list[float] | str
    collectedAt: str


def frequencies(root: Path, mask: str) -> dict[str, Frequency]:
    def khz(cpu: int, name: str) -> int | None:
        value = read_text(root / cpu_file(cpu, f"cpufreq/{name}"))
        return int(value) if value else None

    return {
        str(cpu): Frequency(
            min=khz(cpu, "cpuinfo_min_freq"),
            max=khz(cpu, "cpuinfo_max_freq"),
            current=khz(cpu, "scaling_cur_freq"),
        )
        for cpu in parse_cpu_mask(mask) or []
    }


def perf_event_paranoid(root: Path) -> int | None:
    value = read_text(root / PERF_EVENT_PARANOID)
    return int(value) if value else None


def default_quiet_state() -> Path:
    return Path(os.environ.get("XDG_RUNTIME_DIR", FALLBACK_RUNTIME_DIRECTORY)) / QUIET_STATE_FILE


UNIT_KINDS = ("system", "user")


def quiet_mode(state: Path) -> QuietMode:
    # harness/env/quiet.sh writes one "<system|user> <unit>" line per unit it stopped, and one
    # "claude <pid>" line per Claude Code process it paused, which is not a unit.
    lines = read_text(state)
    if lines is None:
        return QuietMode(on=False, stopped=[])
    entries = [line.split() for line in lines.splitlines()]
    return QuietMode(on=True, stopped=[entry[1] for entry in entries if len(entry) == 2 and entry[0] in UNIT_KINDS])


def sysinfo(root: Path, mask: str, versions: dict[str, str], quiet_state: Path | None = None) -> Sysinfo:
    host = LinuxHost(root, parse_cpu_mask(mask))
    return Sysinfo(
        cpuModel=host.cpu_model(),
        kernel=host.kernel(),
        distro=host.distro(),
        microcode=host.microcode(),
        governor=host.governor(),
        turbo=host.turbo(),
        smt=host.smt(),
        pCoreMask=p_core_mask(root),
        frequenciesKHz=frequencies(root, mask),
        shield=CgroupShield(root).state(),
        quietMode=quiet_mode(quiet_state or default_quiet_state()),
        perfEventParanoid=perf_event_paranoid(root),
        hostState=host_state(root, parse_cpu_mask(mask) or []),
        commit=git_commit(REPOSITORY),
        versions=versions,
        loadavg=loadavg(),
        collectedAt=utc_now(),
    )


def tool_versions(browsers: Path) -> dict[str, str]:
    # rustup picks the toolchain from the directory: bench/rust-toolchain.toml pins the nightly.
    versions = {"rustc": command_output(["rustc", "-V"], cwd=REPOSITORY / "bench")}
    for name, spec in load_specs(BROWSER_VERSIONS).items():
        executable = browsers / spec.directory_name / spec.executable
        versions[name] = command_output([str(executable), "--version"])
    return versions


def write_sysinfo(path: Path, mask: str, browsers: Path, problems: list[str]) -> None:
    info = sysinfo(Path("/"), mask, tool_versions(browsers))
    path.write_text(json.dumps({**info, "problems": problems}, indent=JSON_INDENT) + "\n")
