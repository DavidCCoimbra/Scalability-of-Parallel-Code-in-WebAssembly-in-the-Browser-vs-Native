"""The build a campaign measures: commit, binaries and browser versions, fixed for every resume."""

import tomllib
from collections.abc import Mapping
from pathlib import Path

from harness.campaign.spec import CampaignSpec
from harness.context import JsonObject, RunEnvironment, command_output, git_commit, sha256_file
from harness.launcher import COMMANDS, FIREFOX_PREFS
from harness.paths import CARGO_LOCK, REPOSITORY, WASM_ARTIFACT, WASM_GLUE

# The crates between the workloads and the threads: the pool, its WASM start-up and the bindings.
RUNTIME_CRATES = ("rayon", "rayon-core", "wasm-bindgen", "wasm-bindgen-rayon")


def build_identity(spec: CampaignSpec, native: list[str] | None, browsers: Mapping[str, Path]) -> JsonObject:
    identity: JsonObject = {"commit": git_commit(REPOSITORY), "variant": spec.build}
    if RunEnvironment.NATIVE in spec.environments and native:
        identity["nativeSha256"] = sha256_file(Path(native[-1]))
    if browsers:
        identity["wasmSha256"] = sha256_file(WASM_ARTIFACT)
        identity["wasmGlueSha256"] = sha256_file(WASM_GLUE)
        identity["browsers"] = browser_versions(browsers)
    if RunEnvironment.FIREFOX in browsers:
        # Chrome's flags are in every run's launchFlags; Firefox's settings go in the profile.
        identity["firefoxPrefs"] = dict(FIREFOX_PREFS)
    identity["crates"] = crate_versions(CARGO_LOCK)
    return identity


def browser_versions(browsers: Mapping[str, Path]) -> JsonObject:
    return {name: command_output(COMMANDS[name]().version_command(executable)) for name, executable in browsers.items()}


def crate_versions(lock: Path) -> JsonObject:
    try:
        packages = tomllib.loads(lock.read_text()).get("package", [])
    except OSError:
        return {}
    return {package["name"]: package["version"] for package in packages if package["name"] in RUNTIME_CRATES}
