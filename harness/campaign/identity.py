"""The build a campaign measures: commit, binaries and browser versions, fixed for every resume."""

import hashlib
import tomllib
from collections.abc import Mapping
from pathlib import Path

from harness.campaign.spec import CampaignSpec
from harness.context import UNAVAILABLE, JsonObject, RunEnvironment, command_output, git_commit, sha256_file
from harness.launcher import COMMANDS, FIREFOX_PREFS
from harness.paths import CARGO_LOCK, REPOSITORY, WASM_ARTIFACT, WASM_PACKAGE

# The crates between the workloads and the threads: the pool, its WASM start-up and the bindings.
RUNTIME_CRATES = ("rayon", "rayon-core", "wasm-bindgen", "wasm-bindgen-rayon")


def build_identity(spec: CampaignSpec, native: list[str] | None, browsers: Mapping[str, Path]) -> JsonObject:
    identity: JsonObject = {"commit": git_commit(REPOSITORY), "variant": spec.build}
    if RunEnvironment.NATIVE in spec.environments and native:
        identity["nativeSha256"] = sha256_file(Path(native[-1]))
    if browsers:
        identity["wasmSha256"] = sha256_file(WASM_ARTIFACT)
        identity["wasmGlueSha256"] = glue_digest(WASM_PACKAGE)
        identity["browsers"] = browser_versions(browsers)
    if RunEnvironment.FIREFOX in browsers:
        # Chrome's flags are in every run's launchFlags; Firefox's settings go in the profile.
        identity["firefoxPrefs"] = dict(FIREFOX_PREFS)
    identity["crates"] = crate_versions(CARGO_LOCK)
    return identity


def browser_versions(browsers: Mapping[str, Path]) -> JsonObject:
    return {name: command_output(COMMANDS[name]().version_command(executable)) for name, executable in browsers.items()}


# One digest over every JavaScript file wasm-bindgen wrote: the bindings and the snippets, which
# hold the worker start-up of wasm-bindgen-rayon. Each file enters with its path, in path order.
def glue_digest(package: Path) -> str:
    scripts = sorted(package.rglob("*.js"))
    if not scripts:
        return UNAVAILABLE
    digest = hashlib.sha256()
    for script in scripts:
        digest.update(script.relative_to(package).as_posix().encode())
        digest.update(script.read_bytes())
    return digest.hexdigest()


# A crate locked at two versions is recorded with both.
def crate_versions(lock: Path) -> JsonObject:
    try:
        packages = tomllib.loads(lock.read_text()).get("package", [])
    except OSError:
        return {}
    versions: dict[str, list[str]] = {}
    for package in packages:
        if package["name"] in RUNTIME_CRATES:
            versions.setdefault(package["name"], []).append(package["version"])
    return {name: ", ".join(sorted(found)) for name, found in versions.items()}
