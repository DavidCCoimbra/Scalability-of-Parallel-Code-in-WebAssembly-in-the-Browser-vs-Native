# ADR 0044: Thread counts N = 1, 2, 4, 6, 7, 8

Date: 2026-11-07

## Context

The campaign measures on the 8 P-cores (ADR 0001), so the thread counts must stop at N = 8. But a
browser also runs its own threads (main, compositor, garbage collector, compilers). At N = 8 the
workers plus those threads may ask for more cores than the mask gives: oversubscription, where
threads wait for a core and the slowdown would look like poor scaling. The thread counts had to
be chosen so that such an effect can be located, at an acceptable campaign time.

### The pilots

- **First thread count pilot** (`pilot-threads-{local,atomic}.json`, 2026-11-07): the filter,
  `hist-local` k = 1 and 16 and `hist-atomic` k = 1 and 256 at 8192x8192, N = 1, 2, 4, 6, 7, 8, 3
  runs per environment, 270 runs. It ran Chrome's browser process outside the run scope (ADR
  0045) and used W = 56 for the filter and `hist-local`.
- **Repeated with the final W.** The filter and `hist-local` part was repeated with the final W of
  ADR 0043 (filter 15, k = 1: 71, k = 16: 15) for all three environments: Chrome and Firefox with
  every browser process in the scope (`pilot-threads-scoped.json`, 108 runs) and native
  (`pilot-threads-native.json`, 54 runs).
- **10-core check.** A check with 10 cores (the 8 P-cores and E-cores 16 and 17) ran `hist-local`
  k = 1 and 16 at N = 6, 7, 8, 5 runs per environment (`pilot-oversubscription.json`, 90 runs; not
  strict, because its mask is not the P-cores).
- All 252 new runs have `escapedProcesses` = 0 (no browser process outside the run scope,
  ADR 0045).

The specs and the pilot data are in `data/earlier/pilot` (`pilot-threads-*`).

### Speedups

Relative speedup at N = 6 / 7 / 8 and its 95 % bootstrap interval at N = 8, from `analysis.v0`
(geometric mean of the per-run medians, 3 runs), all with the final W:

| Workload | Native | Chrome | Firefox |
|---|---|---|---|
| filter | 5.47 / 6.12 / 6.84 [6.80, 6.88] | 5.32 / 6.06 / 6.82 [6.80, 6.84] | 5.62 / 6.45 / 7.43 [7.38, 7.48] |
| `hist-local` k = 1 | 5.94 / 6.82 / 7.96 [7.96, 7.96] | 5.84 / 6.82 / 7.91 [7.89, 7.94] | 5.89 / 6.88 / 7.70 [7.68, 7.72] |
| `hist-local` k = 16 | 5.84 / 6.73 / 7.96 [7.90, 8.01] | 5.70 / 6.76 / 7.82 [7.65, 8.09] | 6.19 / 6.19 / 6.53 [6.35, 6.85] |

A browser "follows" native when the ratio of its speedup to native's stays flat as N grows; a
"knee" is that ratio dropping at the highest N.

- **Chrome follows native** up to N = 8 in every workload (ratio to native 0.97 to 1.00 at every N
  shown), also with its browser process back on the P-cores.
- **Firefox has a knee only on `hist-local`.** At k = 1 its ratio to native is about 1.00 up to
  N = 7 and 0.97 at N = 8; at k = 16 it is 1.06 at N = 6 and 0.82 at N = 8. The filter shows none.
- **The Firefox k = 16 values are fragile.** The Firefox `hist-local` k = 16 values at N = 7 and 8
  come from bursts within runs, not from a steady plateau: in a single run the iterations go from
  about 4.7 to 11 ms, and the fastest are close to native's pace. With 3 runs and 10 iterations
  these speedups are fragile; the run count pilot (ADR 0047) measures how often the bursts occur.
- **Speedups above N are baseline effects.** Firefox `hist-local` k = 16 has an efficiency above 1
  at N = 4 (1.036 [1.006, 1.094]) and N = 6 (1.031 [1.020, 1.044]), and the Firefox filter is
  above native at N = 8. At N = 1, Firefox takes 1.28 times native on `hist-local` k = 16 (37.33
  against 29.13 ms) and 1.36 times on the filter (30.70 against 22.60 ms), and at N = 8 it is still
  slower in absolute terms. The absolute ratios of ADR 0039 report this.
- **With 10 cores** (`python3 -m analysis.compare data/raw/pilot-threads-native
  data/raw/pilot-threads-scoped --against data/raw/pilot-oversubscription`: ratio of geometric
  means, 95 % bootstrap interval, runs resampled within each side), Firefox gets faster at N = 8
  although the extra cores are slower E-cores (k = 1: 0.980 [0.977, 0.983]; k = 16: 0.892 [0.830,
  0.978]). At N = 7 the k = 16 interval includes 1 (0.920 [0.820, 1.040]) and k = 1 does not
  change (1.003). Native and Chrome get the same or slower at N = 7 and 8 (up to 1.058). Even with
  the room, Firefox k = 16 reaches a speedup of about 7.3 at N = 8, against native's 7.96: the
  room recovers part of the knee. Firefox k = 16 also gains a little at N = 6 (0.979 [0.965,
  0.994]).
- **The 10-core check is confounded.** It is consistent with Firefox's own threads competing with
  its workers at N = 8, but its 8-core baseline comes from other sessions (not interleaved), and
  E-cores 16 and 17 also host the harness and the rest of the system (the shield uses 16-31), so
  the extra room is smaller than two cores. Foreign CPU time is also higher in these runs (native
  maximum 0.09 s against 0.04 s).
- **W holds at the intermediate N** with the final W. Over the 108 scoped runs, (median of the
  first 5 measured iterations - median of the last 5) / median of the last 5 has a median of
  +0.04 % (19 runs above 1 %, 15 below -1 %); the largest, -32 %, is a Firefox `hist-local`
  k = 16 burst, not a trend. The `hist-atomic` W of 5 is the final value of ADR 0043 (first pilot:
  median 0.0 %, 6 runs above 1 %, 5 below -1 %).
- **An open question for RQ2.** `hist-atomic` k = 256 scales in the browsers and not natively
  (first pilot: speedup at N = 8 native 0.89, Chrome 2.00, Firefox 1.19). This was investigated
  separately with the fixed harness (ADR 0049).

A run's CPU time cannot measure the browser's extra threads directly: it includes untimed work
(input generation, calibration, checksums), which dominates on short iterations.

## Decision

Decided on 2026-11-07; the recommended option was applied:

- **The campaign uses N = 1, 2, 4, 6, 7, 8.** N = 7 locates where the Firefox knee starts, which
  differs by workload. The primary contrasts stay at N = 8 (the analysis plan's maximum N,
  ADR 0037).
- **Oversubscription at N = 8 in Firefox is a threat to validity.** The Firefox N = 8 contrasts,
  including the RQ1 gap and the RQ2 ratios of `hist-local`, may include it. The 10-core check is
  consistent with it but confounded, and is not part of the campaign.

## Consequences

- One more thread count than the plan's minimum costs about 20 % more campaign time.
- The pilot specs are pilot-only; their data are not reused in the campaign analysis. In
  `pilot-threads-scoped.json` every workload sets its own `warmup`, so the top-level
  `"warmup": 5` never applies; the file is left as it ran.

## Status

Accepted; amended by ADR 0048 (with a 3 s start delay no browser shows a knee; the knee most
likely came from Firefox start-up work, and oversubscription stays a smaller possible threat)
