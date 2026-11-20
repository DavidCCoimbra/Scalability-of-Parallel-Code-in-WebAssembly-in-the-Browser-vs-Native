import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

import json

from harness.context import sha256_file, validate
from unittest import mock

from harness.shield import scope_prefix, scope_stop_command
from harness.launcher import BrowserCommand, ChromeCommand, FirefoxCommand, Launcher, RunStatus, run_url


class FakeBrowser:
    name = "chrome"

    def __init__(self, code: str):
        self.code = code
        self.profiles: list[Path] = []

    def prepare_profile(self, profile: Path) -> None:
        self.profiles.append(profile)

    def argv(self, executable: Path, profile: Path, url: str, headless: bool) -> list[str]:
        return [sys.executable, "-c", self.code, url]

    def version_command(self, executable: Path) -> list[str]:
        return ["echo", "Fake Browser 1.0"]


class ProfileBrowser(FakeBrowser):
    def __init__(self, results: Path, run_id: str):
        super().__init__("")
        self.results = results
        self.run_id = run_id

    def argv(self, executable: Path, profile: Path, url: str, headless: bool) -> list[str]:
        code = (
            "import pathlib, subprocess, sys\n"
            "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)', sys.argv[1]], start_new_session=True)\n"
            f"pathlib.Path({str(self.results / (self.run_id + '.pid'))!r}).write_text(str(child.pid))\n"
            f"pathlib.Path({str(self.results / (self.run_id + '.csv'))!r}).write_text('ok')\n"
        )
        return [sys.executable, "-c", code, str(profile)]


def writes_result_then_hangs(results: Path, run_id: str, meta: dict[str, object] | None = None) -> str:
    page_meta = f"pathlib.Path({str(results / (run_id + '.json'))!r}).write_text({json.dumps(meta)!r})\n" if meta else ""
    return (
        "import pathlib, time\n"
        + page_meta
        + f"pathlib.Path({str(results / (run_id + '.csv'))!r}).write_text('ok')\n"
        "time.sleep(60)\n"
    )


def leader_exits_leaving_a_child(results: Path, run_id: str, pid_file: Path) -> str:
    return (
        "import pathlib, subprocess, sys\n"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        f"pathlib.Path({str(pid_file)!r}).write_text(str(child.pid))\n"
        f"pathlib.Path({str(results / (run_id + '.csv'))!r}).write_text('ok')\n"
    )


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class CommandTest(unittest.TestCase):
    def test_run_url_adds_run_and_environment(self) -> None:
        self.assertEqual(
            run_url(8000, "r1", "chrome", "workload=filter&threads=2", start_delay_ms=1500),
            "http://127.0.0.1:8000/index.html?run=r1&env=chrome&startDelayMs=1500&workload=filter&threads=2",
        )

    def test_query_cannot_override_run_or_environment(self) -> None:
        for query in ("run=other&threads=2", "env=firefox&threads=2", "startDelayMs=5&threads=2", "run=&threads=2"):
            with self.assertRaises(ValueError):
                run_url(8000, "r1", "chrome", query, start_delay_ms=0)

    def test_chrome_uses_the_profile_and_disables_first_run_and_updates(self) -> None:
        argv = ChromeCommand().argv(Path("/b/chrome"), Path("/p"), "http://x", headless=False)
        self.assertEqual(argv[0], "/b/chrome")
        self.assertEqual(argv[-1], "http://x")
        for flag in ("--user-data-dir=/p", "--no-first-run", "--no-default-browser-check", "--disable-component-update"):
            self.assertIn(flag, argv)
        self.assertNotIn("--headless=new", argv)

    def test_chrome_does_not_background_the_measured_page(self) -> None:
        argv = ChromeCommand().argv(Path("c"), Path("p"), "u", headless=False)
        for flag in (
            "--disable-renderer-backgrounding",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-domain-reliability",
        ):
            self.assertIn(flag, argv)

    def test_headless_is_opt_in(self) -> None:
        self.assertIn("--headless=new", ChromeCommand().argv(Path("c"), Path("p"), "u", headless=True))
        self.assertIn("-headless", FirefoxCommand().argv(Path("f"), Path("p"), "u", headless=True))

    def test_firefox_profile_gets_user_js_without_first_run_updates_or_telemetry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            FirefoxCommand().prepare_profile(profile)
            prefs = (profile / "user.js").read_text()
        for pref in ('"app.update.auto", false', '"toolkit.telemetry.enabled", false', '"browser.shell.checkDefaultBrowser", false'):
            self.assertIn(pref, prefs)

    def test_firefox_profile_disables_background_network_activity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            FirefoxCommand().prepare_profile(profile)
            prefs = (profile / "user.js").read_text()
        for pref in (
            '"browser.safebrowsing.malware.enabled", false',
            '"browser.safebrowsing.phishing.enabled", false',
            '"browser.safebrowsing.downloads.enabled", false',
            '"services.settings.server", "data:,#remote-settings-dummy/v1"',
            '"app.normandy.enabled", false',
            '"app.shield.optoutstudies.enabled", false',
            '"dom.push.connection.enabled", false',
            '"media.gmp-manager.updateEnabled", false',
            '"media.gmp-gmpopenh264.enabled", false',
            '"extensions.systemAddon.update.enabled", false',
            '"network.connectivity-service.enabled", false',
            '"network.dns.disablePrefetch", true',
            '"network.prefetch-next", false',
            '"browser.region.update.enabled", false',
        ):
            self.assertIn(pref, prefs)

    def test_firefox_runs_without_remote_on_its_own_profile(self) -> None:
        argv = FirefoxCommand().argv(Path("/b/firefox"), Path("/p"), "http://x", headless=False)
        self.assertEqual(argv[:5], ["/b/firefox", "-no-remote", "-new-instance", "-profile", "/p"])
        self.assertEqual(argv[-1], "http://x")


class LauncherTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.results = Path(self.tmp.name) / "results"
        self.results.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def launcher(
        self, browser: BrowserCommand, cpus: str | None = None, timeout: float = 5.0, scope_user: str | None = None
    ) -> Launcher:
        self.wasm = Path(self.tmp.name) / "bench_bg.wasm"
        self.wasm.write_bytes(b"\0asm-test")
        return Launcher(
            browser,
            Path("unused"),
            self.results,
            port=8000,
            cpus=cpus,
            timeout=timeout,
            poll=0.05,
            artifact=self.wasm,
            order_position=5,
            scope_user=scope_user,
        )

    def test_cpu_mask_prefixes_taskset(self) -> None:
        argv = self.launcher(ChromeCommand(), cpus="0-7").command(Path("/p"), "r1", "q=1")
        self.assertEqual(argv[:3], ["taskset", "-c", "0-7"])

    def test_scope_wraps_taskset_in_a_systemd_scope_on_the_mask(self) -> None:
        argv = self.launcher(ChromeCommand(), cpus="0,2", scope_user="david").command(Path("/p"), "r1", "q=1")
        prefix = scope_prefix("r1", "0,2", "david", os.environ)
        self.assertEqual(argv[: len(prefix)], prefix)
        self.assertEqual(argv[len(prefix) : len(prefix) + 3], ["taskset", "-c", "0,2"])

    def test_scoped_run_stops_its_scope_before_the_process_group(self) -> None:
        browser = FakeBrowser(writes_result_then_hangs(self.results, "r8"))
        launcher = self.launcher(browser, cpus="0", scope_user="david")

        def unconfined(profile: Path, run_id: str, query: str) -> list[str]:
            return browser.argv(Path("x"), profile, "u", False)

        with mock.patch.object(launcher, "command", unconfined), mock.patch("harness.launcher.launcher.subprocess.run") as system:
            launcher.run("r8", "workload=filter")
        system.assert_any_call(scope_stop_command("r8"), capture_output=True, timeout=30)
        self.assertEqual(json.loads((self.results / "r8.json").read_text())["runCpuMethod"], "scope")

    def test_reused_run_id_is_refused_before_launching(self) -> None:
        for leftover in ("r7.csv", "r7.json", "r7.error.json"):
            self.results.mkdir(parents=True, exist_ok=True)
            (self.results / leftover).write_text("old")
            browser = FakeBrowser(writes_result_then_hangs(self.results, "r7"))
            with self.assertRaises(FileExistsError, msg=leftover):
                self.launcher(browser).run("r7", "workload=filter")
            self.assertEqual(browser.profiles, [], leftover)
            (self.results / leftover).unlink()

    def test_processes_left_on_the_profile_are_killed_and_counted(self) -> None:
        browser = ProfileBrowser(self.results, "r6")
        self.launcher(browser).run("r6", "workload=filter")
        meta = json.loads((self.results / "r6.json").read_text())
        self.assertEqual(meta["leftoverProcesses"], 1)
        self.assertEqual(meta["escapedProcesses"], "unavailable")
        self.assertFalse(alive(int((self.results / "r6.pid").read_text())))

    def test_start_delay_must_fit_a_browser_timer(self) -> None:
        for delay in (-1, 2**31):
            with self.assertRaises(ValueError, msg=delay):
                Launcher(ChromeCommand(), Path("x"), self.results, start_delay_ms=delay)
        Launcher(ChromeCommand(), Path("x"), self.results, start_delay_ms=2**31 - 1)

    def test_scope_without_a_mask_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.launcher(ChromeCommand(), scope_user="david")

    def test_context_records_run_cpu_time_and_shield(self) -> None:
        browser = FakeBrowser(writes_result_then_hangs(self.results, "r9"))
        self.launcher(browser).run("r9", "workload=filter")
        meta = json.loads((self.results / "r9.json").read_text())
        self.assertIn("runCpuSeconds", meta)
        self.assertIn("foreignCpuSeconds", meta)
        self.assertIn("shield", meta)
        self.assertEqual(meta["runCpuMethod"], "session")
        self.assertEqual(meta["startDelayMs"], 0)
        self.assertEqual(meta["passes"], 1)
        self.assertEqual(meta["leftoverProcesses"], 0)

    def test_context_records_the_passes_of_the_query(self) -> None:
        browser = FakeBrowser(writes_result_then_hangs(self.results, "r10"))
        self.launcher(browser).run("r10", "workload=filter&passes=8")
        self.assertEqual(json.loads((self.results / "r10.json").read_text())["passes"], 8)

    def test_context_records_the_grain_of_the_query(self) -> None:
        browser = FakeBrowser(writes_result_then_hangs(self.results, "r11"))
        self.launcher(browser).run("r11", "workload=filter&grain=16")
        self.assertEqual(json.loads((self.results / "r11.json").read_text())["grain"], 16)

    def test_malformed_cpu_mask_is_rejected_up_front(self) -> None:
        with self.assertRaises(ValueError):
            self.launcher(ChromeCommand(), cpus="0,x")

    def test_no_cpu_mask_runs_the_browser_directly(self) -> None:
        argv = self.launcher(ChromeCommand()).command(Path("/p"), "r1", "q=1")
        self.assertEqual(argv[0], "unused")

    def test_finished_run_kills_the_browser_and_removes_the_profile(self) -> None:
        browser = FakeBrowser(writes_result_then_hangs(self.results, "r1"))
        outcome = self.launcher(browser).run("r1", "workload=filter")
        self.assertEqual(outcome.status, RunStatus.DONE)
        self.assertLess(outcome.seconds, 5)
        self.assertFalse(browser.profiles[0].exists())

    def test_run_without_result_times_out(self) -> None:
        browser = FakeBrowser("import time; time.sleep(60)")
        outcome = self.launcher(browser, timeout=0.5).run("r2", "workload=filter")
        self.assertEqual(outcome.status, RunStatus.TIMEOUT)
        self.assertFalse(browser.profiles[0].exists())

    def test_browser_that_exits_without_result_is_reported(self) -> None:
        outcome = self.launcher(FakeBrowser("raise SystemExit(3)")).run("r3", "workload=filter")
        self.assertEqual(outcome.status, RunStatus.EXITED)
        self.assertEqual(outcome.exit_code, 3)

    def test_children_that_outlive_the_leader_are_killed(self) -> None:
        pid_file = Path(self.tmp.name) / "child.pid"
        browser = FakeBrowser(leader_exits_leaving_a_child(self.results, "r4", pid_file))
        outcome = self.launcher(browser).run("r4", "workload=filter")
        self.assertEqual(outcome.status, RunStatus.DONE)
        child = int(pid_file.read_text())
        deadline = time.monotonic() + 2
        while alive(child) and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertFalse(alive(child))

    def test_finished_run_gets_its_context_in_the_metadata(self) -> None:
        build = {"features": [], "rustc": "rustc x", "rustflags": ""}
        browser = FakeBrowser(writes_result_then_hangs(self.results, "r5", {"userAgent": "ua", "build": build}))
        launcher = self.launcher(browser)
        launcher.run("r5", "workload=filter")
        meta = json.loads((self.results / "r5.json").read_text())
        self.assertEqual(validate(meta), [])
        self.assertEqual((meta["userAgent"], meta["browserVersion"]), ("ua", "Fake Browser 1.0"))
        self.assertEqual(meta["build"], build)
        self.assertEqual(meta["artifactSha256"], sha256_file(self.wasm))
        self.assertEqual(meta["orderPosition"], 5)
        self.assertLessEqual(meta["startedAt"], meta["finishedAt"])

    def test_page_error_is_reported_with_message_context_and_browser_log(self) -> None:
        code = (
            "import json, pathlib, time\n"
            "print('browser says hello', flush=True)\n"
            f"pathlib.Path({str(self.results / 'r6.error.json')!r}).write_text(json.dumps({{'error': 'InconsistentChecksum'}}))\n"
            "time.sleep(60)\n"
        )
        outcome = self.launcher(FakeBrowser(code)).run("r6", "workload=filter")
        self.assertEqual(outcome.status, RunStatus.ERROR)
        self.assertEqual(outcome.message, "InconsistentChecksum")
        stored = json.loads((self.results / "r6.error.json").read_text())
        self.assertEqual(stored["error"], "InconsistentChecksum")
        self.assertEqual(stored["browserVersion"], "Fake Browser 1.0")
        self.assertIn("browser says hello", (self.results / "r6.browser.log").read_text())


if __name__ == "__main__":
    unittest.main()
