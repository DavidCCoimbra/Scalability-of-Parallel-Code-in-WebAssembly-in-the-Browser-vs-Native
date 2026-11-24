# ADR 0045: P-cores only, confirmed by a pilot, and every browser process in the run scope

Date: 2026-11-07

## Context

ADR 0001 measures on the 8 P-cores only (the performance cores of the hybrid i9-14900KF, as
opposed to its slower E-cores). That choice needed preliminary experiments to justify it. The mask
pilot (`pilot-mask-{p,pe}` in `data/earlier/pilot`, 2026-11-07) ran the
filter and `hist-local` k = 16 at 8192x8192, N = 1 and 8, 10 runs per environment, with two masks:

- P: the P-cores, `0,2,...,14`, strict validation;
- P+E: every online CPU, `0,2,...,14,16-31`;

both in quiet mode (ADR 0042).

### Chrome's browser process escaped the run

A sampler of every thread's `Cpus_allowed_list` during the first attempt showed that Chrome's
browser process moves itself, through the D-Bus session bus, into its own systemd scope
(`app-org.chromium.Chromium-<pid>.scope` in `user.slice`). It therefore ran on the E-cores,
outside the run scope and its P-core mask (ADR 0028). Firefox's processes all stayed in the run
scope, so the two browsers were not confined alike. Without the session bus address, every Chrome
process stays in the run scope. The renderer, where the WASM and its workers run, had stayed on
the P-cores throughout.

### Results with the fix

Per configuration: the median of the per-run medians and the run-to-run coefficient of variation
(CV, standard deviation over mean) for each mask, the P+E / P ratio of medians with a 95 %
percentile bootstrap interval over runs, and Cliff's delta over runs. Cliff's delta is a
non-parametric effect size from -1 to +1: the probability that a run of one group is slower than a
run of the other, minus the reverse; here positive means P+E slower.

| Configuration | P (ms, CV) | P+E (ms, CV) | P+E / P [95 % CI] | Cliff's delta |
|---|---|---|---|---|
| Chrome filter N = 1 | 26.35, 0.7 % | 26.40, 0.4 % | 1.00 [0.99, 1.01] | +0.20 |
| Chrome `hist-local` k16 N = 1 | 36.10, 0.9 % | 36.48, 10.3 % | 1.01 [1.00, 1.11] | +0.58 |
| Firefox filter N = 1 | 30.68, 0.7 % | 30.77, 1.0 % | 1.00 [1.00, 1.01] | +0.39 |
| Firefox `hist-local` k16 N = 1 | 37.17, 4.0 % | 37.30, 0.4 % | 1.00 [1.00, 1.05] | +0.31 |
| native filter N = 1 | 22.57, 0.1 % | 22.56, 0.5 % | 1.00 [1.00, 1.01] | +0.10 |
| native `hist-local` k16 N = 1 | 29.17, 0.3 % | 29.08, 0.3 % | 1.00 [0.99, 1.00] | -0.56 |
| Chrome filter N = 8 | 3.99, 0.6 % | 4.10, 1.6 % | 1.03 [1.02, 1.04] | +1.00 |
| Chrome `hist-local` k16 N = 8 | 4.54, 2.9 % | 4.98, 4.1 % | 1.10 [1.07, 1.15] | +1.00 |
| Firefox filter N = 8 | 4.25, 0.9 % | 4.54, 3.9 % | 1.07 [1.03, 1.09] | +0.92 |
| Firefox `hist-local` k16 N = 8 | 5.42, 7.2 % | 5.05, 7.8 % | 0.93 [0.84, 0.99] | -0.70 |
| native filter N = 8 | 3.32, 0.9 % | 3.79, 7.2 % | 1.14 [1.08, 1.19] | +1.00 |
| native `hist-local` k16 N = 8 | 3.65, 0.4 % | 4.35, 5.9 % | 1.19 [1.14, 1.26] | +1.00 |

- **N = 1:** the medians agree within 1 % in every cell (intervals within [0.99, 1.11]). The
  Chrome `hist-local` CV under P+E comes from runs whose single thread landed on an E-core.
- **N = 8:** P+E is slower in 5 of 6 cells, by 3 % (Chrome filter) to 19 % (native
  `hist-local`), and its CV grows in the native and Chrome cells (native filter 0.9 to 7.2 %).
  Firefox `hist-local` k16 goes the other way: 7 % faster under P+E, with a similar CV,
  consistent with the oversubscription noted in the thread count pilot (ADR 0044): with more
  cores, Firefox's own threads stop competing with its 8 workers.

## Decision

Decided on 2026-11-07; the recommended option was applied:

- **The P-core mask stays (ADR 0001).** With P+E, N = 8 runs are slower in 5 of 6 cells and
  markedly more variable in the native and Chrome cells, because the workers share the cores with
  the system and land on slower cores. The Firefox `hist-local` exception is recorded as evidence
  of oversubscription, not as a reason to widen the mask: with E-cores the workers would no longer
  run on the same kind of core.
- **No session bus for the browsers.** The harness no longer passes `DBUS_SESSION_BUS_ADDRESS` to
  the browsers (ADR 0028 listed it among the session variables), so every browser process stays
  in the run scope.
- **Escaped processes are recorded and rejected.** Each run records `escapedProcesses`: the
  descendants of the launching `sudo` and the processes of its profile that are outside the run
  scope. It is sampled once, when the result has arrived, so a process that left the scope and
  exited earlier is not counted. Strict validation rejects a run with any, and runs without the
  field (the earlier pilots) fail strict validation.

## Consequences

- Chrome and Firefox are confined alike; all 240 runs of this pilot have `escapedProcesses` = 0.
- The earlier pilots (image size, ADR 0041; warm-up, ADR 0043; the first thread count pilot, ADR
  0044) ran Chrome's browser process on the E-cores. Their decisions do not rest on it (clock
  resolution, warm-up of the renderer's code, the Firefox knee); the thread count pilot is
  repeated with the fix (ADR 0044).
- Threat to validity: the GPU process sets some of its threads to a subset of the mask
  (`0,2,4,6`); they are idle in headless runs.

## Status

Accepted; amends ADR 0001 (confirms it with pilot data) and ADR 0028; amended by ADR 0048 (the
Firefox `hist-local` k16 gain under P+E at N = 8 is most likely browser start-up work, which then
had more cores)
