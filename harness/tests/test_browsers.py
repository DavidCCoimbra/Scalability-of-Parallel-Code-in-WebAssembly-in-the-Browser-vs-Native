import hashlib
import io
import json
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from harness.browsers import BrowserSpec, ChecksumMismatch, Installer, UnpinnedChecksum, firefox_spec, load_specs


def zip_with(path: str, content: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        info = zipfile.ZipInfo(path)
        info.external_attr = 0o755 << 16
        archive.writestr(info, content)
    return buffer.getvalue()


def tar_xz_with(path: str, content: bytes, *extra: tuple[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:xz") as archive:
        for name, data in ((path, content), *extra):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o755
            archive.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


class FakeFetch:
    def __init__(self, responses: dict[str, bytes]):
        self.responses = responses
        self.calls: list[str] = []

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        return self.responses[url]


CHROME_URL = "https://storage.googleapis.com/chrome-for-testing-public/155.0.8059.84/linux64/chrome-linux64.zip"
FIREFOX_BASE = "https://archive.mozilla.org/pub/firefox/releases/158.0"
FIREFOX_URL = f"{FIREFOX_BASE}/linux-x86_64/en-US/firefox-158.0.tar.xz"


class InstallerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.chrome_zip = zip_with("chrome-linux64/chrome", b"#!chrome")
        self.firefox_tar = tar_xz_with("firefox/firefox", b"#!firefox", ("firefox/application.ini", b"[App]\nVersion=158.0\n"))
        sums = f"{hashlib.sha256(self.firefox_tar).hexdigest()}  linux-x86_64/en-US/firefox-158.0.tar.xz\n"
        self.fetch = FakeFetch(
            {CHROME_URL: self.chrome_zip, FIREFOX_URL: self.firefox_tar, f"{FIREFOX_BASE}/SHA256SUMS": sums.encode()}
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def specs(self, chrome_sha: str | None = None) -> dict[str, BrowserSpec]:
        config = {"chrome": {"version": "155.0.8059.84", "sha256": chrome_sha}, "firefox": {"version": "158.0"}}
        path = self.root / "browsers.json"
        path.write_text(json.dumps(config))
        return load_specs(path)

    def test_specs_use_the_official_download_urls(self) -> None:
        specs = self.specs()
        self.assertEqual(specs["chrome"].url, CHROME_URL)
        self.assertEqual(specs["firefox"].url, FIREFOX_URL)

    def test_installs_and_returns_the_executable(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        good = hashlib.sha256(self.chrome_zip).hexdigest()
        chrome = installer.install(self.specs(chrome_sha=good)["chrome"])
        firefox = installer.install(self.specs()["firefox"])
        self.assertEqual(chrome.read_bytes(), b"#!chrome")
        self.assertEqual(firefox.read_bytes(), b"#!firefox")
        self.assertTrue(chrome.stat().st_mode & 0o100)

    def test_second_install_downloads_nothing(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        spec = self.specs()["firefox"]
        first = installer.install(spec)
        calls = len(self.fetch.calls)
        self.assertEqual(installer.install(spec), first)
        self.assertEqual(len(self.fetch.calls), calls)

    def test_firefox_checksum_mismatch_installs_nothing(self) -> None:
        self.fetch.responses[f"{FIREFOX_BASE}/SHA256SUMS"] = b"0" * 64 + b"  linux-x86_64/en-US/firefox-158.0.tar.xz\n"
        installer = Installer(self.root / "browsers", self.fetch)
        with self.assertRaises(ChecksumMismatch):
            installer.install(self.specs()["firefox"])
        self.assertFalse((self.root / "browsers" / "firefox-158.0").exists())

    def test_a_pinned_firefox_checksum_wins_over_the_sums_file(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        with self.assertRaises(ChecksumMismatch):
            installer.install(firefox_spec("158.0", "0" * 64))
        good = hashlib.sha256(self.firefox_tar).hexdigest()
        self.fetch.responses[f"{FIREFOX_BASE}/SHA256SUMS"] = b"0" * 64 + b"  linux-x86_64/en-US/firefox-158.0.tar.xz\n"
        self.assertEqual(installer.install(firefox_spec("158.0", good)).read_bytes(), b"#!firefox")

    def test_the_repository_pins_both_browsers(self) -> None:
        specs = load_specs(Path(__file__).resolve().parents[1] / "browsers.json")
        self.assertTrue(all(spec.sha256 for spec in specs.values()))

    def test_pinned_chrome_checksum_is_verified(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        with self.assertRaises(ChecksumMismatch):
            installer.install(self.specs(chrome_sha="0" * 64)["chrome"])
        good = hashlib.sha256(self.chrome_zip).hexdigest()
        self.assertTrue(installer.install(self.specs(chrome_sha=good)["chrome"]).exists())

    def test_unpinned_chrome_is_refused_and_reports_its_checksum(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        with self.assertRaises(UnpinnedChecksum) as error:
            installer.install(self.specs()["chrome"])
        self.assertIn(hashlib.sha256(self.chrome_zip).hexdigest(), str(error.exception))
        self.assertFalse((self.root / "browsers" / "chrome-155.0.8059.84").exists())

    def test_trust_on_first_use_installs_and_reports_the_checksum(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch, trust_on_first_use=True)
        self.assertTrue(installer.install(self.specs()["chrome"]).exists())
        self.assertEqual(installer.reported["chrome"], hashlib.sha256(self.chrome_zip).hexdigest())

    def test_firefox_gets_the_policy_that_turns_off_its_self_update(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        executable = installer.install(self.specs()["firefox"])
        policies = executable.parent / "distribution" / "policies.json"
        self.assertEqual(json.loads(policies.read_text()), {"policies": {"DisableAppUpdate": True}})

    def test_an_existing_firefox_install_gets_the_policy_without_a_download(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        executable = installer.install(self.specs()["firefox"])
        policies = executable.parent / "distribution" / "policies.json"
        policies.unlink()
        calls = len(self.fetch.calls)
        installer.install(self.specs()["firefox"])
        self.assertTrue(policies.exists())
        self.assertEqual(len(self.fetch.calls), calls)

    def test_a_firefox_that_updated_itself_in_place_is_reinstalled(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        executable = installer.install(self.specs()["firefox"])
        (executable.parent / "application.ini").write_text("[App]\nVersion=160.0\n")
        calls = len(self.fetch.calls)
        installer.install(self.specs()["firefox"])
        self.assertIn("Version=158.0", (executable.parent / "application.ini").read_text())
        self.assertGreater(len(self.fetch.calls), calls)

    def test_chrome_gets_no_policy_file(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        good = hashlib.sha256(self.chrome_zip).hexdigest()
        chrome = installer.install(self.specs(chrome_sha=good)["chrome"])
        self.assertFalse((chrome.parent / "distribution").exists())

    def test_missing_executable_triggers_a_reinstall(self) -> None:
        installer = Installer(self.root / "browsers", self.fetch)
        executable = installer.install(self.specs()["firefox"])
        executable.unlink()
        self.assertTrue(installer.install(self.specs()["firefox"]).exists())

if __name__ == "__main__":
    unittest.main()
