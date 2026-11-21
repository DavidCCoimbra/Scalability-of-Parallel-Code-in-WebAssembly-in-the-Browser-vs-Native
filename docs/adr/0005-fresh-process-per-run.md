# ADR 0005: One fresh process per run, warm-up inside the run, run as unit of analysis

Date: 2026-10-17

## Context

A benchmark usually repeats the measured work many times (iterations). Iterations inside one
process are not independent: they share the just-in-time (JIT) compiler's state (which code has been compiled
and optimised), the caches and the allocator. If each iteration were treated as an independent
sample, the statistics would count the same process state many times and claim more certainty
than the data holds. This is pseudo-replication (Georges et al. 2007).

Iterations are also not alike at the start: the first ones pay for JIT compilation and cold
caches (warm-up), so they do not represent the steady state.

## Decision

- One independent run = one fresh process. For the browser, that means a fresh launch with a
  fresh profile, so no compiled code or cache from an earlier run is reused.
- Warm-up iterations happen inside each run, with the same warm-up length W for native and WASM;
  they are not counted as measured iterations.
- Statistics are done over runs: each run is summarised into one value from its measured
  iterations, and the runs are the samples.
- The raw per-iteration data, warm-up included, is always stored.

## Consequences

- The statistics are valid over independent samples.
- Relaunching the browser adds about 1-2 s per run to the duration of a campaign.
- W and the per-run summary are decided from pilot data (W in ADR 0043, the summary in the
  analysis plan, ADR 0037).

## Status

Accepted
