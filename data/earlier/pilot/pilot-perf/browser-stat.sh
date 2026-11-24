#!/usr/bin/env bash
# browser-stat.sh SPEC OUT : system-wide counters on the P-cores while one campaign runs
spec=$1; out=$2
sudo -n systemd-run --quiet --pipe --wait --collect rm -f /tmp/ppc-perf-probe.txt
ev=cpu_core/cycles/,cpu_core/mem_inst_retired.lock_loads/,cpu_core/ocr.demand_rfo.l3_hit.snoop_hitm/,cpu_core/ocr.demand_data_rd.l3_hit.snoop_hitm/
sudo -n systemd-run --quiet --unit=ppc-perf-probe --collect perf stat -x, -a -C 0,2,4,6,8,10,12,14 -e $ev -o /tmp/ppc-perf-probe.txt -- sleep 600 &
sleep 2
rm -rf "$out.results"; python3 -m harness.campaign "$spec" --results "$out.results" > "$out.log" 2>&1
sudo -n systemctl kill -s INT ppc-perf-probe.service 2>/dev/null || sudo -n systemctl stop ppc-perf-probe.service
sleep 2; cp /tmp/ppc-perf-probe.txt "$out.perf" 2>/dev/null
