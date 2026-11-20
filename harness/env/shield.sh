#!/usr/bin/env bash
# Usage: harness/env/shield.sh on|off E_CPUS P_MASK
# Moves system.slice, user.slice and init.scope to the E-cores until the
# next reboot (--runtime) and checks the effective cpusets.
set -euo pipefail

if [[ $# -ne 3 || ($1 != on && $1 != off) ]]; then
  echo "usage: $0 on|off E_CPUS P_MASK" >&2
  exit 2
fi

action=$1
e_cpus=$2
p_mask=$3
units=(system.slice user.slice init.scope)

for unit in "${units[@]}"; do
  if [[ $action == on ]]; then
    sudo systemctl set-property --runtime "$unit" "AllowedCPUs=$e_cpus"
  else
    sudo systemctl set-property --runtime "$unit" "AllowedCPUs="
  fi
done

cd "$(dirname "$0")/../.."
if [[ $action == on ]]; then
  python3 -m harness.shield check --cpus "$p_mask"
fi
