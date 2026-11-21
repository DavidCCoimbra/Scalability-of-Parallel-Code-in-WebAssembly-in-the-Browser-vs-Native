#!/usr/bin/env bash
# Builds the native runner and the WASM package twice from scratch and fails unless both builds
# give the same digests. A build that a failing core corrupted without crashing would differ.
#
# Usage: scripts/build_twice.sh DIGESTS_FILE
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="${1:?usage: scripts/build_twice.sh DIGESTS_FILE}"
NATIVE=bench/target/release/native
PACKAGE=bench/www/pkg

digests() {
  sha256sum "$NATIVE" "$PACKAGE/bench_bg.wasm"
  find "$PACKAGE" -name '*.js' -print0 | sort -z | xargs -0 sha256sum
}

from_scratch() {
  # shellcheck source=/dev/null
  (source "$HOME/.cargo/env" && cd bench && cargo clean --quiet)
  rm -rf "$PACKAGE"
  make build
}

from_scratch
first="$(digests)"
from_scratch
second="$(digests)"
if [[ "$first" != "$second" ]]; then
  printf 'the two builds differ:\n%s\n---\n%s\n' "$first" "$second"
  exit 1
fi
{
  echo "# commit $(git rev-parse HEAD), two builds from scratch with equal digests"
  echo "$first"
} >"$OUT"
cat "$OUT"
