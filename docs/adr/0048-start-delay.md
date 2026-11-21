# ADR 0048: A 3 s start delay for every browser run

Date: 2026-11-07

## Context

Every browser run starts from a fresh launch with a fresh profile (ADR 0005). A freshly launched
browser keeps doing start-up work of its own for a while after the page loads. That work runs
inside the same CPU mask as the measurement, so if the page starts measuring at once, the
start-up work can compete with the workers and slow down or disturb the first measured
iterations.

ADR 0029 therefore added a start delay: the page waits before it creates the coordinating
worker, so module compilation, the thread pool and the measurement only start after the wait.
It left the length of the delay to pilot data. The warm-up pilot (ADR 0043) ran with no delay,
and its runs of short iterations end less than a second after the page loads, so it could not
show start-up work that lasts seconds.

### Delay pilot

The delay pilot (`harness/campaigns/pilot-delay-{0,3000}.json`, 2026-11-07; in the working
repository) ran the filter and `hist-local` k = 16 (W = 15) at N = 8, 10 runs per browser, with
no delay and with 3000 ms, one after the other. All 80 runs have `escapedProcesses` = 0.
Ratio of geometric means with a 3 s delay over none (`analysis/compare.py`, 95 % bootstrap
interval):

| Configuration | no delay | 3 s | ratio [95 % CI] | runs with a burst | run CV |
|---|---|---|---|---|---|
| Chrome filter N = 8 | 3.87 ms | 3.91 ms | 1.011 [0.999, 1.025] | 1 / 0 of 10 | 0.7 / 2.2 % |
| Chrome `hist-local` k16 N = 8 | 4.54 ms | 4.54 ms | 0.999 [0.979, 1.018] | 0 / 0 | 2.0 / 2.6 % |
| Firefox filter N = 8 | 4.15 ms | 4.13 ms | 0.995 [0.989, 1.001] | 0 / 0 | 0.8 / 0.7 % |
| Firefox `hist-local` k16 N = 8 | 5.89 ms | 4.46 ms | 0.756 [0.721, 0.790] | 3 / 0 | 7.6 / 1.6 % |

A burst is an iteration above 1.3 times its run's median. The pairs in the last two columns are
no delay / 3 s.

Without the delay, Firefox is still starting up while short iterations are measured. Its
start-up work competes with 8 workers on the 8 P-cores (the performance cores, ADR 0001), which
shows as slower and bursty iterations. With 3 s, the bursts go away and the within-run spread
(slowest over fastest iteration) drops from 1.37 to 1.03.

### Thread pilot with the delay

ADR 0044 had found a "knee" in Firefox: on `hist-local`, its speedup fell away from native's at
N = 7 and 8. A thread pilot with the delay (`pilot-threads-delay.json`: `hist-local` k = 1 and
16, Chrome and Firefox, N in {1, 2, 4, 6, 7, 8}, 3 runs, 72 runs) no longer shows that knee. Speedup at
N = 8 with the final W, against native:

- k = 1: Firefox 7.86 [7.80, 7.90], Chrome 7.89, native 7.96;
- k = 16: Firefox 8.29 [8.23, 8.40], Chrome 7.85, native 7.96.

Firefox's k = 16 speedup above native is a baseline effect: its N = 1 time is 1.27 times
native's, so a slower T1 raises T1 / T8.

## Decision

Decided on 2026-11-07; the option recommended from the data above was applied:

- Every browser run of the campaign waits 3000 ms before it starts. The value is passed as
  `startDelayMs` and recorded in every run's context; the orchestrator checks that it is the
  same for every browser run (ADR 0029).
- Earlier conclusions are amended:
  - **ADR 0044:** the Firefox knee on `hist-local` at N = 7 and 8, and its gain with 10 cores,
    most likely came from Firefox start-up work rather than from its own threads during the
    measurement: with the delay no browser shows a knee (3 runs per configuration, and no
    no-delay control in the same session). Oversubscription (more busy threads than cores)
    stays a possible threat, now much smaller; start-up work is the main one, and the delay
    controls it.
  - **ADR 0045:** Firefox `hist-local` k16 being faster under the P+E mask at N = 8 is most
    likely the same start-up work, which then had more cores to run on.
  - **ADR 0043:** the 26 to 47 slow iterations of Firefox `hist-local` k = 1 at N = 8 (0.5 to
    1 s) may be start-up work rather than tier-up (the JIT moving the hot code to its
    optimizing compiler). W stays as it is: a warm-up longer than needed is harmless.
  - **ADR 0047:** the Firefox `hist-local` bursts that lowered its iteration agreement are
    start-up work; with the delay, the 30 runs are conservative.

## Consequences

- The campaign takes about 2.7 hours more (3240 browser runs times 3 s).
- **3 s against 6 s.** A second pilot (`pilot-delay-long-{3000,6000}.json`: Firefox
  `hist-local` k = 1 and 16 at N = 7 and 8, 8 runs each, one after the other) gives ratios
  between the two delays of 0.997 [0.993, 1.002] and 0.995 [0.992, 0.998] for k = 1, and 1.006 [0.997,
  1.015] and 1.013 [0.992, 1.034] for k = 16. A longer delay changes the medians by at most
  1.3 % (point estimates); the widest interval, k = 16 at N = 8, reaches 3.4 %, so this pilot
  cannot rule out an effect of that size there. 3 s is kept.
- **Asymmetry with native.** Native runs have no delay: the browsers wait 3 s idle before
  measuring and native does not. This is a known asymmetry between environments. It affects
  N = 1 and N = N alike within an environment, so relative speedup is not expected to change;
  the absolute browser / native ratios (ADR 0039) are read with it in mind.
- The delay modes were not interleaved. With ratios this far from 1 (Firefox `hist-local`) or
  this close to 1 (the rest), drift does not change the conclusion.

## Status

Accepted; amends ADR 0029, ADR 0043, ADR 0044, ADR 0045 and ADR 0047
