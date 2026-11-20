#!/usr/bin/env bash
# Usage: harness/env/setup.sh [P_MASK] [E_CPUS]
# Prepares the measuring PC until the next reboot, then checks it.
# perf_event_paranoid 1 lets the user read hardware counters (perf stat, perf c2c)
# for the diagnostics; it changes nothing while no perf session runs.
# https://docs.kernel.org/admin-guide/perf-security.html
set -euo pipefail

p_mask=${1:-0,2,4,6,8,10,12,14}
e_cpus=${2:-16-31}
cpu=/sys/devices/system/cpu
readonly PERF_PARANOID_DIAGNOSTICS=1
readonly PERF_PARANOID_FILE=/proc/sys/kernel/perf_event_paranoid
# restore.sh puts back the value found here; a second setup keeps the first saved value.
perf_saved="${XDG_RUNTIME_DIR:-/tmp}/ppc-perf-event-paranoid.saved"

echo off | sudo tee "$cpu/smt/control" >/dev/null
if [[ -e $cpu/intel_pstate/no_turbo ]]; then
  echo 1 | sudo tee "$cpu/intel_pstate/no_turbo" >/dev/null
elif [[ -e $cpu/cpufreq/boost ]]; then
  echo 0 | sudo tee "$cpu/cpufreq/boost" >/dev/null
else
  echo "no turbo control found (intel_pstate/no_turbo or cpufreq/boost)" >&2
  exit 1
fi
for core in "$cpu"/cpu[0-9]*; do
  [[ -e $core/online && $(<"$core/online") == 0 ]] && continue
  echo performance | sudo tee "$core/cpufreq/scaling_governor" >/dev/null
done

[[ -e $perf_saved ]] || cat "$PERF_PARANOID_FILE" >"$perf_saved"
echo "$PERF_PARANOID_DIAGNOSTICS" | sudo tee "$PERF_PARANOID_FILE" >/dev/null

"$(dirname "$0")/shield.sh" on "$e_cpus" "$p_mask"
exec "$(dirname "$0")/check.sh" "$p_mask"
