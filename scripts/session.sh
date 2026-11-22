#!/usr/bin/env bash
# One stage of the measuring session of a build, as numbered steps that resume where they
# stopped. The stages run in this order, each started by hand once the one before passed:
#
#   scripts/session.sh preflight   # environment, tests, checksums in both browsers
#   scripts/session.sh build       # the Rust tests, then two builds from scratch, digests compared
#   scripts/session.sh gate        # the gate campaign and its check
#   scripts/session.sh main        # the main campaign, then its tables
#   scripts/session.sh extras      # the exploratory campaigns, most wanted first
#
#   RUN_DRY=1 scripts/session.sh main   # only prints the steps
#   FRESH=1 scripts/session.sh gate     # forgets the done marks of the stage; progress.log is kept,
#                                       # and a campaign still resumes from the runs it has
#
# MEASURED (default v3) names the build: specs harness/campaigns/*-<it>.json, runs
# data/raw/*-<it>. Progress and logs go to data/sessions/<it>/<stage>/.
set -euo pipefail
cd "$(dirname "$0")/.."

STAGE="${1:?usage: scripts/session.sh preflight|build|gate|main|extras}"
export MEASURED="${MEASURED:-v3}"
SESSION="data/sessions/$MEASURED/$STAGE"
source scripts/lib/steps.sh

spec() { echo "harness/campaigns/$1-$MEASURED.json"; }

campaign() { step "$1" make campaign SPEC="$(spec "$2")"; }

preflight() {
  step 01-env-check make env-check
  step 02-test make test
  # Not `make quick`: its specs pin with a plain taskset, which the shield of a prepared machine
  # refuses. The gate is the end-to-end run of the real protocol.
  step 03-browser-check python3 -m harness.browser_check
}

# The tests come first, so that nothing builds after the digests are taken: the binaries left in
# place are the ones that were compared.
build() {
  step 01-test make test-rust
  step 02-build-twice scripts/build_twice.sh "$SESSION/digests.txt"
}

gate() {
  campaign 01-campaign gate
  step 02-check python3 -m analysis.gate "data/raw/gate-$MEASURED"
}

main() {
  campaign 01-campaign campaign
  step 02-status make status SPEC="$(spec campaign)"
  step 03-results make results
}

# In the order of what the open questions of the study need (ADR 0088), so that a short week
# drops from the end. The scalar SIMD build overwrites bench/www/pkg, hence the rebuild after it.
extras() {
  campaign 01-tier tier
  step 02-perf scripts/perf-counters.sh
  campaign 03-simd-scalar simd-scalar
  step 04-rebuild make build
  campaign 05-simd-avx2 simd-avx2
  step 06-cutoff make cutoff-campaigns
  campaign 07-grain-threads grain-threads
  step 08-grain make grain-campaigns
  campaign 09-weak weak
  campaign 10-extras extras
}

case "$STAGE" in
  preflight | build | gate | main | extras) ;;
  *)
    echo "no stage $STAGE: choose preflight, build, gate, main or extras"
    exit 1
    ;;
esac
if ! is_dry_run; then
  mkdir -p "$SESSION"
  [[ "${FRESH:-0}" != 1 ]] || find "$SESSION" -maxdepth 1 -name '*.done' -delete
fi
"$STAGE"
is_dry_run || log "stage $STAGE finished"
