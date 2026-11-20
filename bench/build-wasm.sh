#!/usr/bin/env bash
set -euo pipefail

CRATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CRATE_DIR
readonly OUT_DIR="${CRATE_DIR}/www/pkg"

pinned_wasm_bindgen_version() {
  sed -n 's/^wasm-bindgen = "=\(.*\)"$/\1/p' "${CRATE_DIR}/Cargo.toml"
}

require_wasm_bindgen() {
  local pinned installed
  pinned="$(pinned_wasm_bindgen_version)"
  installed="$(wasm-bindgen --version 2>/dev/null | awk '{print $2}')" || true
  if [[ -z "${pinned}" || "${installed}" != "${pinned}" ]]; then
    echo "error: wasm-bindgen ${pinned:-?} (pinned in Cargo.toml) required, found '${installed:-none}'" >&2
    echo "install: cargo install wasm-bindgen-cli --version ${pinned} --locked" >&2
    exit 1
  fi
}

main() {
  require_wasm_bindgen
  cd "${CRATE_DIR}"
  cargo build-wasm "$@"
  rm -rf "${OUT_DIR}"
  wasm-bindgen --target web --out-dir "${OUT_DIR}" \
    target/wasm32-unknown-unknown/release/bench.wasm
  echo "wrote ${OUT_DIR}"
}

main "$@"
