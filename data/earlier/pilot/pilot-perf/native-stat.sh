#!/usr/bin/env bash
# native-stat.sh BINARY K N OUT
bin=$1; k=$2; n=$3; out=$4
ev=cpu_core/cycles/,cpu_core/mem_inst_retired.lock_loads/,cpu_core/ocr.demand_rfo.l3_hit.snoop_hitm/,cpu_core/ocr.demand_data_rd.l3_hit.snoop_hitm/
sudo -n systemd-run --scope --quiet --slice=ppc-bench.slice -p AllowedCPUs=0,2,4,6,8,10,12,14 \
  perf stat -x, -e $ev -- taskset -c 0,2,4,6,8,10,12,14 "$bin" --workload hist-atomic --input few --k "$k" \
  --threads "$n" --width 8192 --height 8192 --warmup 5 --iters 10 --calibration 0 > "$out.csv" 2> "$out.perf"
