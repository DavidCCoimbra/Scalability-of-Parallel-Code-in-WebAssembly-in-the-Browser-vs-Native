"""How to start each browser on a fresh profile with quiet settings."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from harness.context.run_environment import RunEnvironment

USER_PREFS_FILE = "user.js"
CHROME_HEADLESS_FLAG = "--headless=new"
FIREFOX_HEADLESS_FLAG = "-headless"
VERSION_FLAG = "--version"

FIREFOX_PREFS: dict[str, str | bool | int] = {
    "app.normandy.api_url": "",
    "app.normandy.enabled": False,
    "app.shield.optoutstudies.enabled": False,
    "app.update.auto": False,
    "app.update.checkInstallTime": False,
    "browser.aboutwelcome.enabled": False,
    "browser.shell.checkDefaultBrowser": False,
    "browser.startup.homepage_override.mstone": "ignore",
    "browser.newtabpage.enabled": False,
    "browser.region.network.url": "",
    "browser.region.update.enabled": False,
    "browser.safebrowsing.downloads.enabled": False,
    "browser.safebrowsing.downloads.remote.enabled": False,
    "browser.safebrowsing.malware.enabled": False,
    "browser.safebrowsing.phishing.enabled": False,
    "datareporting.healthreport.uploadEnabled": False,
    "datareporting.policy.dataSubmissionEnabled": False,
    "dom.push.connection.enabled": False,
    "dom.push.serverURL": "",
    "extensions.getAddons.cache.enabled": False,
    "extensions.systemAddon.update.enabled": False,
    "extensions.update.enabled": False,
    "media.gmp-gmpopenh264.enabled": False,
    "media.gmp-manager.updateEnabled": False,
    "media.gmp-manager.url": "",
    "network.captive-portal-service.enabled": False,
    "network.connectivity-service.enabled": False,
    "network.dns.disablePrefetch": True,
    "network.http.speculative-parallel-limit": 0,
    "network.prefetch-next": False,
    "services.settings.server": "data:,#remote-settings-dummy/v1",
    "startup.homepage_welcome_url": "",
    "toolkit.telemetry.enabled": False,
    "toolkit.telemetry.reportingpolicy.firstRun": False,
}

CHROME_FLAGS = (
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-client-side-phishing-detection",
    "--disable-domain-reliability",
    "--disable-renderer-backgrounding",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-sync",
    "--metrics-recording-only",
    "--password-store=basic",
)


class BrowserCommand(Protocol):
    @property
    def name(self) -> str: ...

    def prepare_profile(self, profile: Path) -> None: ...

    def argv(self, executable: Path, profile: Path, url: str, headless: bool) -> list[str]: ...

    def version_command(self, executable: Path) -> list[str]: ...


class ChromeCommand:
    name = RunEnvironment.CHROME

    def __init__(self, extra_flags: tuple[str, ...] = ()):
        self.extra_flags = extra_flags

    def version_command(self, executable: Path) -> list[str]:
        return [str(executable), VERSION_FLAG]

    def prepare_profile(self, profile: Path) -> None:
        pass

    def argv(self, executable: Path, profile: Path, url: str, headless: bool) -> list[str]:
        headless_flags = [CHROME_HEADLESS_FLAG] if headless else []
        return [
            str(executable),
            f"--user-data-dir={profile}",
            *CHROME_FLAGS,
            *self.extra_flags,
            *headless_flags,
            url,
        ]


class FirefoxCommand:
    name = RunEnvironment.FIREFOX

    def version_command(self, executable: Path) -> list[str]:
        return [str(executable), VERSION_FLAG]

    def prepare_profile(self, profile: Path) -> None:
        lines = [f"user_pref({json.dumps(key)}, {json.dumps(value)});" for key, value in FIREFOX_PREFS.items()]
        (profile / USER_PREFS_FILE).write_text("\n".join(lines) + "\n")

    def argv(self, executable: Path, profile: Path, url: str, headless: bool) -> list[str]:
        headless_flags = [FIREFOX_HEADLESS_FLAG] if headless else []
        return [str(executable), "-no-remote", "-new-instance", "-profile", str(profile), *headless_flags, url]


COMMANDS: dict[str, Callable[[], BrowserCommand]] = {
    RunEnvironment.CHROME: ChromeCommand,
    RunEnvironment.FIREFOX: FirefoxCommand,
}
