# ADR 0090: Counters of the loop alone, by the difference of two pass counts

Date: 2026-11-23

## Context

The counters campaign `perf-v3` counts the eight P-cores for the whole of each run and divides
by the pixels of its timed iterations (ADR 0072). For the atomic histogram that is close to the
loop's own cost: its 15 iterations take 6 to 28 seconds and dominate the run. For the filter and
the local histogram, added for questions 1, 2, 3 and 5 of ADR 0088, it is not. Their 25
iterations take about half a second, less than the start of a browser, the generation of the
input and the checksums that the same window holds.

The first look at `perf-v3` shows it. Instructions per pixel of the local histogram at k = 256
with one thread: 3.7 natively, 12.6 in Chrome and 21.3 in Firefox, where the loop itself is 2.75
instructions per pixel natively (`data/probes/engine-code`). Most of what is counted in the
browsers is not the loop. The differences between one and eight threads inside an environment
survive, since the rest of the run is the same, but they are small against the total (the
filter's cycles per pixel go from 5.77 to 6.05 natively), and nothing can be said across
environments.

## Decision

**Two campaigns that differ only in the passes per timed sample**, counted as `perf-v3` is:
`perf-loop1-v3` with one pass and `perf-loop8-v3` with eight. Cells: the filter, and the local
histogram at k = 16 and 256, at N = 1 and 8, in the three environments, 10 runs each (180 runs
per campaign). Both workloads repeat identically, so a pass is the same work each time
(`repeats_identically`).

A run of the second does seven more passes of every timed sample than a run of the first, and
nothing else differs: the same start, the same input, the same number of samples, the same
checksums. So for each cell and counter

    (mean count of perf-loop8 - mean count of perf-loop1) / (7 x samples x pixels)

is the count per pixel of the loop alone. The interval comes from a bootstrap over the runs of
both campaigns.

The two campaigns run one after the other, not interleaved: a spec has one pass count. A count
of instructions or of cache misses does not drift as a time does, and the two blocks are 25
minutes apart.

**What the counters of the loop should show**, written before the runs (questions of ADR 0088):

| Question | If the hypothesis holds | If it does not |
|---|---|---|
| 1. The filter is bound by memory at eight threads | Per pixel, the same instructions at N = 1 and 8, more cycles at N = 8 (about 1.15 times, the inverse of its efficiency of 0.87), and more last-level misses | Cycles per pixel as at N = 1: the lost efficiency is not in the cores' own work |
| 2. Firefox scales better because its thread is slower | The rise in cycles per pixel from N = 1 to 8 is smaller in Firefox than natively, in proportion | The same rise as natively |
| 3. Why the filter takes 1.36 times the native time in Firefox and 1.17 in Chrome at N = 1 | More instructions per pixel than natively, or as many with fewer per cycle; the counters say which | - |
| 5. The local histogram's speedup passes 8 in Firefox | Fewer cache misses per pixel at N = 8 than at N = 1 in Firefox, and not natively | The same misses: unexplained. `perf-v3` already points this way (11.4 against 11.5 L2 misses per thousand pixels), diluted as described |

## Consequences

- `perf-v3` keeps its use for the atomic histogram (ADR 0072, ADR 0089). Its filter and local
  histogram cells are read only as differences between thread counts inside one environment,
  and are superseded by the counters of the loop.
- The difference assumes that seven more passes add only loop work. The pool's threads also
  spin between samples for longer runs; with eight threads that is part of what the cores do
  during the loop, and with one thread it is one idle worker.
- Exploratory. No primary conclusion rests on it.

## Status

Accepted
