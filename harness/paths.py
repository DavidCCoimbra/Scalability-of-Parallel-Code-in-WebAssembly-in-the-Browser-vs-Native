"""Paths inside the repository that the harness reads or launches."""

from pathlib import Path

REPOSITORY = Path(__file__).resolve().parent.parent
WWW = REPOSITORY / "bench/www"
WASM_ARTIFACT = WWW / "pkg/bench_bg.wasm"
NATIVE_TARGET = REPOSITORY / "bench/target"
NATIVE_BINARY = NATIVE_TARGET / "release/native"
BROWSER_VERSIONS = REPOSITORY / "harness/browsers.json"
BROWSERS_ROOT = REPOSITORY / "harness/browsers"
