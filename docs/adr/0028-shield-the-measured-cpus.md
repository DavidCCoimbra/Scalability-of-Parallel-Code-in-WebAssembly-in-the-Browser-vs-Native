# ADR 0028: Shield the measured CPUs and record foreign CPU time

Date: 2026-10-17

## Context

`taskset` (ADR 0001) keeps the measured process on the P-cores, but it does not keep anything else
off them. The results server, the launcher's polling, the desktop compositor and system daemons can
all run there. On a hybrid CPU the scheduler (ITMT, Linux's support for preferring the faster
cores) even prefers the P-cores, which are exactly the measured ones. Any such foreign work steals
time from a measured thread, and it hurts more at high N, when every measured CPU is busy.

The review of the benchmark code once it was first complete (finding R2) listed three options:

1. a cgroup cpuset (a kernel control that limits which CPUs a group of processes may use) for the
   rest of the system;
2. `taskset` for the harness only;
3. no shielding, with the load recorded.

The load average from ADR 0027 is a one minute mean, too coarse to show interference within one
run, so option 3 alone would not show what happened during a run.

## Decision

The first option is taken (with the second for the harness), plus a per-run measurement of what is
left.

- **cpuset at runtime.** `harness/env/shield.sh on E_CPUS P_MASK` sets `AllowedCPUs` of
  `system.slice`, `user.slice` and `init.scope` to the E-cores (efficiency cores) with
  `systemctl set-property --runtime` (undone by a reboot or by `shield.sh off`). It then runs
  `python3 -m harness.shield check`, which reads `cpuset.cpus.effective` of each unit and fails if
  any of them can use a measured CPU.
- **The run gets its own scope.** A process started from the session inherits the `user.slice`
  restriction, so `taskset` to the P-cores would fail. With `--scope-user USER` the launcher and
  the native wrapper start the run as `sudo -n systemd-run --scope --slice=ppc-bench.slice
  --unit=ppc-run-<id> --uid=USER -p AllowedCPUs=<mask> env <session variables>`, followed by the
  same `taskset -c <mask>` as before.
  - `sudo` resets the environment, so the session variables a browser needs (`HOME`, `USER`,
    `LOGNAME`, `PATH`, `DISPLAY`, `WAYLAND_DISPLAY`, `XAUTHORITY`, `XDG_RUNTIME_DIR`,
    `DBUS_SESSION_BUS_ADDRESS`) are passed explicitly, and nothing else. The run id must be a valid
    unit name.
  - The `taskset` stays: it resets the affinity inherited from the harness (pinned to the E-cores)
    and keeps `cpuMask` meaning the same with or without the shield.
  - A scoped run is stopped with `systemctl stop ppc-run-<id>.scope` before the process group is
    killed, because a root-owned `sudo` (possibly on its own pty) can keep the browser out of reach
    of `killpg`.
  - The PC needs a sudoers rule that allows `systemd-run` and `systemctl stop ppc-run-*` without a
    password.
- **Harness on the E-cores.** The launcher and the native wrapper take `--harness-cpus` and pin
  themselves there (`sched_setaffinity`); the results server is started under
  `taskset -c <E-cores>`, as ADR 0019 required.
- **Foreign CPU time per run.** Busy time of the measured CPUs is read from `/proc/stat` before and
  after each run, and the run's own CPU time is subtracted. What remains is CPU time that something
  else used on the measured CPUs.
  - For browser runs, the run's own time is the scope's `cpu.stat` (`usage_usec`, all browser
    processes) or, without a scope, the CPU time of the browser's process session.
  - For native runs, it is the children's `getrusage` (the scope is gone once the runner exits).
    Both count the CPU time of the run's whole process tree, and the few milliseconds of `sudo` and
    `systemd-run` run on the E-cores.
  - New context keys: `shield` (effective CPUs of the three units), `runCpuSeconds`,
    `runCpuMethod` (`scope`, `session` or `rusage`) and `foreignCpuSeconds`.
  - Strict validation rejects `shield` or `foreignCpuSeconds` that are `unavailable` and a shield
    whose units can use a measured CPU.

## Consequences

- The shield does not isolate per-CPU kernel threads (`kworker`, `ksoftirqd`) or interrupts; that
  would need `isolcpus`/`nohz_full` and IRQ affinity, which is beyond this project.
  `foreignCpuSeconds` measures what is left, including that kernel work, for each run.
- SMT stays off (ADR 0025), so there are no P-core siblings to shield.
- The pilot compares the variance between runs with and without the shield, using
  `foreignCpuSeconds`, and only compares runs with the same `runCpuMethod` (the session method
  misses processes that exited before the end). A threshold on `foreignCpuSeconds` for strict
  validation is set from that pilot data, not before (ADR 0051).
- `foreignCpuSeconds` has the resolution of `/proc/stat` (10 ms per CPU) and can be slightly
  negative when the run's own time is counted in a different tick; the analysis treats values near
  zero as zero.
- Nothing here runs on macOS: runs on the development Mac keep `shield` and `foreignCpuSeconds` as
  `unavailable` and fail strict validation, as before. The scope and the shield are checked on the
  PC in the end-to-end smoke test.

## Status

Accepted; amends ADR 0023 (context keys)
