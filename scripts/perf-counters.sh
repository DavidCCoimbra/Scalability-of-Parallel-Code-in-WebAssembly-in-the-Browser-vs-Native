#!/usr/bin/env bash
# Hardware counters of the atomic histogram on one measured build (MEASURED, default v2).
#
# Runs the perf-<build> campaign (an ordinary randomized campaign, quiet mode) while `perf stat`
# counts the eight P-cores system-wide in 100 ms intervals. analysis/extras/perf_counters.py sums the
# intervals inside each run's startedAt..finishedAt window, so every run gets its own counts.
# perf needs CPU-wide events, which perf_event_paranoid = 1 denies to a user, so it runs as a
# transient system unit (sudo is allowed for systemd-run and systemctl only). The unit lives in
# the system slice, which the shield keeps on the E-cores.
#
# A resumed campaign appends a new segment: each segment keeps its own start time.
set -euo pipefail

MEASURED=${MEASURED:-v2}
SPEC=harness/campaigns/perf-$MEASURED.json
OUT=data/raw/perf-$MEASURED/counters
P_CORES=0,2,4,6,8,10,12,14
INTERVAL_MS=100
# Seven events is what the P-cores count at once here: with a third cache event perf multiplexes,
# and the analysis refuses intervals that were not counted whole.
EVENTS=cpu_core/cycles/,cpu_core/instructions/,cpu_core/mem_inst_retired.lock_loads/,cpu_core/ocr.demand_rfo.l3_hit.snoop_hitm/,cpu_core/ocr.demand_data_rd.l3_hit.snoop_hitm/,cpu_core/longest_lat_cache.miss/,cpu_core/mem_load_retired.l2_miss/
UNIT=ppc-perf-$MEASURED
SEGMENT=$(date -u +%Y%m%dT%H%M%SZ)
TMP=/tmp/$UNIT-$SEGMENT

mkdir -p "$OUT"
stop_perf() {
  sudo -n systemctl kill -s INT "$UNIT.service" 2>/dev/null || true
  sleep 2
  cp "$TMP.csv" "$OUT/$SEGMENT.csv" && cp "$TMP.start" "$OUT/$SEGMENT.start" || echo "perf output missing" >&2
}

sudo -n systemd-run --quiet --unit="$UNIT" --collect -- sh -c \
  "date +%s.%N > $TMP.start; exec perf stat -x, -a -C $P_CORES -I $INTERVAL_MS -e $EVENTS -o $TMP.csv -- sleep 86400"
trap stop_perf EXIT
sleep 2

QUIET_KEEP_CLAUDE=1 make campaign SPEC="$SPEC"
make status SPEC="$SPEC"
