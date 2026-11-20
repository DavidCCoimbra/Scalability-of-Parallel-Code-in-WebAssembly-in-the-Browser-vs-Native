#!/usr/bin/env bash
# One perf c2c record per browser around a single hist-atomic k=16 N=8 run on measured/v2.
set -u
S=$1
for b in chrome firefox; do
  sudo -n systemd-run --quiet --unit=ppc-c2c-$b --collect -- perf c2c record -a -C 0,2,4,6,8,10,12,14 -o /tmp/ppc-c2c-$b.data -- sleep 900
  sleep 3
  python3 -m harness.campaign $S/c2c-$b.json --results $S/results-$b > $S/campaign-$b.log 2>&1
  echo "campaign $b exit $?"
  sudo -n systemctl kill -s INT ppc-c2c-$b.service; sleep 5
  sudo -n systemd-run --quiet --pipe --wait --collect -- perf c2c report -i /tmp/ppc-c2c-$b.data --stdio -N --full-symbols > $S/c2c-$b.txt 2>&1
  echo "report $b exit $? lines $(wc -l < $S/c2c-$b.txt)"
done
