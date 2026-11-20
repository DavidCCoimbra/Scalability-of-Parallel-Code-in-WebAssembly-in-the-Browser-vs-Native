"""The build a campaign measures: commit, binaries and browser versions, fixed for every resume."""

from collections.abc import Mapping
from pathlib import Path

from harness.campaign.spec import CampaignSpec
from harness.context import JsonObject, RunEnvironment, command_output, git_commit, sha256_file
from harness.launcher import COMMANDS
from harness.paths import REPOSITORY, WASM_ARTIFACT


def build_identity(spec: CampaignSpec, native: list[str] | None, browsers: Mapping[str, Path]) -> JsonObject:
    identity: JsonObject = {"commit": git_commit(REPOSITORY), "variant": spec.build}
    if RunEnvironment.NATIVE in spec.environments and native:
        identity["nativeSha256"] = sha256_file(Path(native[-1]))
    if browsers:
        identity["wasmSha256"] = sha256_file(WASM_ARTIFACT)
        identity["browsers"] = browser_versions(browsers)
    return identity


def browser_versions(browsers: Mapping[str, Path]) -> JsonObject:
    return {name: command_output(COMMANDS[name]().version_command(executable)) for name, executable in browsers.items()}
