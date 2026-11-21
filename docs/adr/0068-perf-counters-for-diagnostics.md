# ADR 0068: Hardware counters made readable for the diagnostics

Date: 2026-11-09

## Context

The v2 build (all reported campaigns re-run on one tagged build, ADR 0069) comes with an audit
of bottlenecks that the benchmark code itself may cause:

- unintended false sharing (threads writing different variables that sit in the same cache
  line, so the line moves between cores as if the data were shared);
- cache misses;
- uneven work per thread.

That audit needs hardware performance counters, read with `perf stat` and `perf c2c` (the
latter reports cache lines that move between cores). Ubuntu ships
`kernel.perf_event_paranoid` = 4, which denies them to a normal user; ADRs 0060 and 0061
recorded that limit at the time. The value only controls who may open perf events, and no perf
session runs during a measured run.

## Decision

- **Setup.** `make env-setup` (`harness/env/setup.sh`) sets `kernel.perf_event_paranoid` to 1
  until the next reboot, like the rest of the machine state it sets. It first saves the value it
  found. A second setup keeps the first saved value, so the original is not lost.
- **Restore.** `make env-restore` puts the saved value back, or 4 if nothing was saved.
- **Record.** The `sysinfo` record of every campaign (`data/raw/<campaign>/sysinfo`) stores
  the value (`perfEventParanoid`), so every campaign states it. Read from those records on
  2026-11-21: the `measured/v2` campaigns started on 9 and 10 November (main, grain, cutoff
  and its controls) ran with 4, and those started from 11 November on (weak, SIMD, extras,
  hybrid, perf) ran with 1. An earlier wording here said every v2 campaign ran with 1.

## Consequences

- **What it enables.** The counter-based diagnostics of the v2 audit (C1 to C12) run without
  manual steps.
- **Effect on measurements.** None, because no perf event is open during a measured run.
- **Earlier ADRs.** The statements in ADRs 0060 and 0061 that counters are unavailable describe
  the machine at that time. They stay as written.

## Status

Accepted
