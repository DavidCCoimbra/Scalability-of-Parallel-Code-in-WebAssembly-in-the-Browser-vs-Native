# ADR 0035: Environment setup and check before every session

Date: 2026-10-17

## Context

Three ADRs describe the machine state a measurement needs: ADR 0002 (turbo boost off and the
CPU frequency governor set to `performance`, so the clock frequency does not change during a
run), ADR 0025 (SMT, simultaneous multithreading or "hyper-threading", off, so each measured CPU
is one physical P-core, a performance core of the hybrid i9-14900KF) and ADR 0028 (the shield, a
cpuset that keeps the rest of the system off the measured CPUs). Each run already records that
state, and strict validation rejects a run that breaks it. But none of these settings survive a
reboot, and a session should not start on a machine that would fail every run.

## Decision

- **Setup.** `harness/env/setup.sh [P_MASK] [E_CPUS]` (defaults `0,2,4,6,8,10,12,14` and
  `16-31`) turns SMT off, turns turbo off (`intel_pstate/no_turbo`, or `cpufreq/boost` where
  that is the control, failing if neither exists), sets every online CPU's governor to
  `performance`, and then turns the shield on (`shield.sh on`). Nothing is persistent: a reboot
  undoes it.
- **Check.** `harness/env/check.sh [P_MASK]` runs `python3 -m harness.environment check` before
  every session. It exits non-zero if turbo is not off, the governor is not `performance` on
  every measured CPU, SMT is not off, the mask is not exactly one CPU on every physical P-core,
  or the shield lets a system unit use a measured CPU.
- **P-core mask from sysfs.** The mask is derived from sysfs (`/sys/devices/cpu_core/cpus` and
  each CPU's `core_cpus_list`), which gives the same answer as `lscpu -e` without parsing its
  table; `python3 -m harness.environment mask` prints it.
- **Saved system state.** Every check saves the system state to
  `data/sysinfo/<UTC time>.json`: CPU model, kernel, governor, turbo, SMT, P-core mask, shield
  state, commit, the minimum, maximum and current frequency of each measured CPU (the current
  frequency is one idle sample, for information only), `rustc` and browser versions, load
  averages and the problems found.

## Consequences

- A session on a machine with turbo on, for example after a reboot, stops before the first run
  instead of producing a campaign that strict validation then throws away.
- The check uses the same rules as strict validation (the same functions for SMT and topology),
  so the two cannot disagree.
- Only the Linux PC passes; on the Mac every item is reported as unavailable.

## Status

Accepted; amended by ADR 0040 (environment check enforced on every start)
