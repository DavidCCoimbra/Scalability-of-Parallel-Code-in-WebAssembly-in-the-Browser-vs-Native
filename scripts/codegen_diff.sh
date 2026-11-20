#!/usr/bin/env bash
# Builds a base git ref and the working tree of bench/ at the SAME absolute
# path, so panic locations and other embedded paths do not differ, then
# compares the code of every function with scripts/codegen_diff.py.
#
# Usage: scripts/codegen_diff.sh [BASE_REF]   (default: main)
# Environment: CODEGEN_DIFF_WORK=/path/to/scratch (default: ${TMPDIR:-/tmp}/codegen-diff)
#              CODEGEN_DIFF_REUSE_BASE=1 keeps the base artifacts of an earlier run
# Exit status 1 means at least one hot function differs in some variant.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPO
readonly BASE_REF="${1:-main}"
readonly WORK="${CODEGEN_DIFF_WORK:-${TMPDIR:-/tmp}/codegen-diff}"
readonly SRC="${WORK}/src"
readonly NATIVE_VARIANTS=(default pad64 avx2 scalar)
readonly WASM_VARIANTS=(default pad64 scalar)

populate() {
  local side="$1" export_dir="${WORK}/export"
  rm -rf "${export_dir}"
  mkdir -p "${export_dir}" "${SRC}"
  if [[ "${side}" == base ]]; then
    local paths=(bench Makefile)
    # Refs before the Makefile split into make/*.mk have no make/ directory.
    if git -C "${REPO}" cat-file -e "${BASE_REF}:make" 2>/dev/null; then
      paths+=(make)
    fi
    git -C "${REPO}" archive "${BASE_REF}" "${paths[@]}" | tar -x -C "${export_dir}"
  else
    rsync -a --exclude target --exclude www/pkg "${REPO}/bench" "${export_dir}/"
    cp "${REPO}/Makefile" "${export_dir}/"
    cp -R "${REPO}/make" "${export_dir}/"
  fi
  rsync -a --delete --exclude target --exclude www/pkg "${export_dir}/bench/" "${SRC}/bench/"
  cp "${export_dir}/Makefile" "${SRC}/Makefile"
  rm -rf "${SRC}/make"
  if [[ -d "${export_dir}/make" ]]; then
    cp -R "${export_dir}/make" "${SRC}/make"
  fi
  # Copied files keep their mtimes, which can be older than the other side's
  # build, and cargo would then reuse it.
  find "${SRC}/bench" \( -path "${SRC}/bench/target" -o -path "${SRC}/bench/www/pkg" \) -prune \
    -o -type f -exec touch {} +
}

make_in_src() {
  make -s -C "${SRC}" NAME=codegen BUILD=baseline "$@"
}

cargo_in_src() {
  (cd "${SRC}/bench" && cargo "$@")
}

build_native() {
  local variant="$1"
  case "${variant}" in
    default) make_in_src build-native ;;
    pad64) cargo_in_src build --release --bin native --features pad64 --target-dir target/pad64 ;;
    avx2) make_in_src build-native-avx2 ;;
    scalar) make_in_src build-native-scalar ;;
  esac
}

native_binary() {
  case "$1" in
    default) echo "${SRC}/bench/target/release/native" ;;
    *) echo "${SRC}/bench/target/$1/release/native" ;;
  esac
}

build_wasm() {
  local variant="$1" out="$2"
  case "${variant}" in
    default) make_in_src build-wasm ;;
    pad64) (cd "${SRC}/bench" && ./build-wasm.sh --features pad64) ;;
    scalar) make_in_src build-wasm-scalar ;;
  esac
  cp "${SRC}/bench/target/wasm32-unknown-unknown/release/bench.wasm" "${out}/wasm-${variant}-raw.wasm"
  cp "${SRC}/bench/www/pkg/bench_bg.wasm" "${out}/wasm-${variant}-pkg.wasm"
}

build_side() {
  local side="$1" out="${WORK}/out/$1" variant
  mkdir -p "${out}"
  populate "${side}"
  for variant in "${NATIVE_VARIANTS[@]}"; do
    build_native "${variant}"
    cp "$(native_binary "${variant}")" "${out}/native-${variant}"
  done
  for variant in "${WASM_VARIANTS[@]}"; do
    build_wasm "${variant}" "${out}"
  done
}

compare() {
  local failed=0 variant artifact
  for variant in "${NATIVE_VARIANTS[@]}"; do
    echo "== native ${variant}"
    python3 "${REPO}/scripts/codegen_diff.py" native \
      "${WORK}/out/base/native-${variant}" "${WORK}/out/head/native-${variant}" || failed=1
  done
  for variant in "${WASM_VARIANTS[@]}"; do
    for artifact in raw pkg; do
      echo "== wasm ${variant} ${artifact}"
      python3 "${REPO}/scripts/codegen_diff.py" wasm \
        "${WORK}/out/base/wasm-${variant}-${artifact}.wasm" \
        "${WORK}/out/head/wasm-${variant}-${artifact}.wasm" || failed=1
    done
  done
  return "${failed}"
}

main() {
  # shellcheck source=/dev/null
  source "${HOME}/.cargo/env"
  if [[ "${CODEGEN_DIFF_REUSE_BASE:-0}" != 1 || ! -d "${WORK}/out/base" ]]; then
    build_side base
  fi
  build_side head
  compare
}

main "$@"
