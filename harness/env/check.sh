#!/usr/bin/env bash
# Usage: harness/env/check.sh [P_MASK]
# Fails unless turbo is off, the governor is performance, SMT is off, the
# mask is every physical P-core and the shield is on; saves the system state.
set -euo pipefail

p_mask=${1:-0,2,4,6,8,10,12,14}
cd "$(dirname "$0")/../.."
exec python3 -m harness.environment check --cpus "$p_mask" \
  --sysinfo "data/sysinfo/$(date -u +%Y%m%dT%H%M%SZ).json"
