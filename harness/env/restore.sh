#!/usr/bin/env bash
# Usage: harness/env/restore.sh [P_MASK] [E_CPUS]
# Undoes setup.sh: shield off, SMT on, turbo on, powersave governor, perf counters
# restricted again: the value setup.sh saved, or 4, the Ubuntu default.
set -euo pipefail

p_mask=${1:-0,2,4,6,8,10,12,14}
e_cpus=${2:-16-31}
cpu=/sys/devices/system/cpu
readonly PERF_PARANOID_DEFAULT=4
readonly PERF_PARANOID_FILE=/proc/sys/kernel/perf_event_paranoid
perf_saved="${XDG_RUNTIME_DIR:-/tmp}/ppc-perf-event-paranoid.saved"

"$(dirname "$0")/shield.sh" off "$e_cpus" "$p_mask"
echo on | sudo tee "$cpu/smt/control" >/dev/null
if [[ -e $cpu/intel_pstate/no_turbo ]]; then
  echo 0 | sudo tee "$cpu/intel_pstate/no_turbo" >/dev/null
elif [[ -e $cpu/cpufreq/boost ]]; then
  echo 1 | sudo tee "$cpu/cpufreq/boost" >/dev/null
fi
for core in "$cpu"/cpu[0-9]*; do
  [[ -e $core/online && $(<"$core/online") == 0 ]] && continue
  echo powersave | sudo tee "$core/cpufreq/scaling_governor" >/dev/null
done
perf_value=$PERF_PARANOID_DEFAULT
if [[ -e $perf_saved ]]; then
  perf_value=$(<"$perf_saved")
  rm -f "$perf_saved"
fi
echo "$perf_value" | sudo tee "$PERF_PARANOID_FILE" >/dev/null
echo "restored: SMT $(cat "$cpu/smt/control"), governor powersave, shield off, perf_event_paranoid $(<"$PERF_PARANOID_FILE")"
