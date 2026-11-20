"""Download the pinned browser builds (Linux x64) listed in harness/browsers.json.

Usage: python3 harness/browsers.py [--dest harness/browsers] [--trust-on-first-use]
Prints the path of each browser executable. Running it again downloads nothing.

Standard library only, so it also runs as a plain script.
"""

import argparse
import hashlib
import io
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

CHROME_BASE = "https://storage.googleapis.com/chrome-for-testing-public"
FIREFOX_BASE = "https://archive.mozilla.org/pub/firefox/releases"
MARKER = ".installed"
STAGING_PREFIX = ".staging-"
ZIP_SUFFIX = ".zip"
SUMS_SEPARATOR = "  "
# A zip entry made on Unix keeps its file mode in the high 16 bits of external_attr.
# https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT (4.4.15)
ZIP_MODE_SHIFT = 16
PERMISSION_BITS = 0o777
# Firefox from archive.mozilla.org updates itself in place even with app.update.auto off; only an
# enterprise policy stops it. 158.0 became 160.0 that way on 2026-11-10, between two campaigns.
# https://mozilla.github.io/policy-templates/#disableappupdate
FIREFOX_POLICIES = {"policies": {"DisableAppUpdate": True}}
FIREFOX_POLICIES_FILE = "firefox/distribution/policies.json"
FIREFOX_VERSION_FILE = "firefox/application.ini"
VERSION_KEY = "Version="

Fetch = Callable[[str], bytes]


class ChecksumMismatch(RuntimeError):
    pass


class UnpinnedChecksum(RuntimeError):
    pass


@dataclass(frozen=True)
class BrowserSpec:
    name: str
    version: str
    url: str
    executable: str
    sha256: str | None = None
    sums_url: str | None = None
    sums_entry: str | None = None
    policies_file: str | None = None
    version_file: str | None = None

    @property
    def directory_name(self) -> str:
        return f"{self.name}-{self.version}"


def chrome_spec(version: str, sha256: str | None) -> BrowserSpec:
    return BrowserSpec(
        name="chrome",
        version=version,
        url=f"{CHROME_BASE}/{version}/linux64/chrome-linux64.zip",
        executable="chrome-linux64/chrome",
        sha256=sha256,
    )


def firefox_spec(version: str) -> BrowserSpec:
    entry = f"linux-x86_64/en-US/firefox-{version}.tar.xz"
    return BrowserSpec(
        name="firefox",
        version=version,
        url=f"{FIREFOX_BASE}/{version}/{entry}",
        executable="firefox/firefox",
        sums_url=f"{FIREFOX_BASE}/{version}/SHA256SUMS",
        sums_entry=entry,
        policies_file=FIREFOX_POLICIES_FILE,
        version_file=FIREFOX_VERSION_FILE,
    )


def load_specs(path: Path) -> dict[str, BrowserSpec]:
    config = json.loads(path.read_text())
    return {
        "chrome": chrome_spec(config["chrome"]["version"], config["chrome"].get("sha256")),
        "firefox": firefox_spec(config["firefox"]["version"]),
    }


def download(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:
        data: bytes = response.read()
        return data


class Installer:
    def __init__(self, root: Path, fetch: Fetch = download, trust_on_first_use: bool = False):
        self.root = root
        self.fetch = fetch
        self.trust_on_first_use = trust_on_first_use
        self.reported: dict[str, str] = {}

    def install(self, spec: BrowserSpec) -> Path:
        target = self.root / spec.directory_name
        executable = target / spec.executable
        if (target / MARKER).exists() and executable.exists() and installed_version(spec, target) in (None, spec.version):
            write_policies(spec, target)
            return executable
        archive = self.fetch(spec.url)
        self.verify(spec, hashlib.sha256(archive).hexdigest())
        self.unpack(spec, archive, target)
        return executable

    def verify(self, spec: BrowserSpec, digest: str) -> None:
        expected = self.expected_digest(spec)
        if expected is None:
            if not self.trust_on_first_use:
                raise UnpinnedChecksum(
                    f"{spec.name} {spec.version} has no pinned sha256 (downloaded: {digest}); "
                    "pin it in browsers.json or pass --trust-on-first-use"
                )
            self.reported[spec.name] = digest
        elif digest != expected:
            raise ChecksumMismatch(f"{spec.name} {spec.version}: sha256 {digest}, expected {expected}")

    def expected_digest(self, spec: BrowserSpec) -> str | None:
        if spec.sha256:
            return spec.sha256
        if spec.sums_url is None:
            return None
        for line in self.fetch(spec.sums_url).decode().splitlines():
            digest, _, entry = line.partition(SUMS_SEPARATOR)
            if entry.strip() == spec.sums_entry:
                return digest
        raise ChecksumMismatch(f"{spec.sums_entry} not listed in {spec.sums_url}")

    def unpack(self, spec: BrowserSpec, archive: bytes, target: Path) -> None:
        # Unpack next to the target and rename, so an interrupted install never looks installed.
        self.root.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(dir=self.root, prefix=STAGING_PREFIX))
        try:
            extract(spec, archive, staging)
            write_policies(spec, staging)
            (staging / MARKER).write_text(f"{spec.version}\n")
            if target.exists():
                shutil.rmtree(target)
            staging.rename(target)
        finally:
            if staging.exists():
                shutil.rmtree(staging)


def installed_version(spec: BrowserSpec, root: Path) -> str | None:
    # An install that updated itself in place keeps its marker, so the version is read from its own files.
    if spec.version_file is None:
        return None
    path = root / spec.version_file
    if not path.exists():
        return ""
    for line in path.read_text().splitlines():
        if line.startswith(VERSION_KEY):
            return line.removeprefix(VERSION_KEY).strip()
    return ""


def write_policies(spec: BrowserSpec, root: Path) -> None:
    # Also written over an existing install, so installs made before the policy get it too.
    if spec.policies_file is None:
        return
    path = root / spec.policies_file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(FIREFOX_POLICIES, indent=2) + "\n")


def extract(spec: BrowserSpec, archive: bytes, destination: Path) -> None:
    if spec.url.endswith(ZIP_SUFFIX):
        extract_zip(archive, destination)
    else:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:xz") as tar:
            tar.extractall(destination, filter="data")


def extract_zip(archive: bytes, destination: Path) -> None:
    # zipfile drops the executable bit, so the mode is restored from each entry.
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        for info in zipped.infolist():
            path = (destination / info.filename).resolve()
            if not path.is_relative_to(destination.resolve()):
                raise ValueError(f"unsafe path in archive: {info.filename}")
            zipped.extract(info, destination)
            mode = info.external_attr >> ZIP_MODE_SHIFT
            if mode:
                path.chmod(mode & PERMISSION_BITS)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=Path, default=Path("harness/browsers"))
    parser.add_argument("--versions", type=Path, default=Path(__file__).with_name("browsers.json"))
    parser.add_argument("--trust-on-first-use", action="store_true")
    args = parser.parse_args(argv)
    installer = Installer(args.dest, trust_on_first_use=args.trust_on_first_use)
    for name, spec in load_specs(args.versions).items():
        print(f"{name} {spec.version}: {installer.install(spec)}")
    for name, digest in installer.reported.items():
        print(f"{name} installed unverified; pin this sha256 in browsers.json: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
