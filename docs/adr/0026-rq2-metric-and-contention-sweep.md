# ADR 0026: RQ2 metric and contention sweep, fixed before the pilot

Date: 2026-10-17

## Context

RQ2 asks how much thread synchronization contributes to the gap between native and WebAssembly.
It is studied with the image histogram in two variants: `hist-atomic`, where all threads update
shared atomic counters, and `hist-local`, where each task counts into its own private histogram
and the results are merged at the end (the control, without shared updates). The first design
crossed these two variants with two inputs, `noise` (meant as "low contention") and a few-colors
input (meant as "high contention").

A review of the benchmark code once it was first complete (finding R5) showed that these factors
manipulate more than their names say:

- **"noise = low contention" is imprecise.** With 256 counters and N >= 2, most `fetch_add`s still
  find the counter's cache line modified by another core, so they still contend. What the input
  changes is how the contention is spread: over 256 lines, or concentrated on k lines.
- **The input also changes the control.** With few distinct values, the private histogram updates
  the same address again and again. Each increment then has to wait for the previous store to the
  same address (a store-to-load forwarding chain), which slows the local variant down already at
  N = 1, with no synchronization involved.
- **Speedup hides the cost of the atomic.** The speedup T1/TN of each variant hides the absolute
  cost of the atomic operation, because T1 of the atomic variant already pays for `lock xadd` (the
  x86 atomic add instruction) on one thread.

## Decision

Decided by the author before any data.

- **Primary RQ2 metric: the interaction contrast on a log scale.** Atomic and local runs are
  separate processes, so the estimand is defined at configuration level:
  - each run is summarised into one time (the per-run summary, median or mean of its measured
    iterations, is chosen in the pilot as ADR 0005 says);
  - `T(e, k, N, variant)` is the central value of those run summaries;
  - `r(e, k, N) = log T(atomic) - log T(local)`, the log of the time ratio of the two variants;
  - RQ2 compares `r` between environments (WASM minus native) at the same k and N, with confidence
    intervals from resampling the runs of each variant and environment independently (details in
    the analysis plan, ADR 0037).
  - "Interaction" means the difference of differences: how much the atomic-over-local ratio
    changes when the environment changes.
  - Speedups of each variant are reported as descriptives only.
- **`r` is a contrast, not a decomposition.** At small k it also contains the store-to-load
  forwarding cost of the local variant. Comparing `r` between environments at the same k is what
  isolates how the environment changes the cost of synchronization.
- **Within one input.** The synchronization effect is always measured within one input (atomic
  against local on the same k), never by comparing inputs.
- **Contention sweep** for the histograms: `few_colors` with k in {1, 4, 16, 256}.
  - k = 256 has the same value distribution as the former `noise` input (uniform over 256 values,
    though not the same pixel sequence: a different generator path) and replaces it for the
    histograms.
  - k = 1 puts every update on one counter.
  - The filter keeps `noise` (it has no shared counters).
- **Names.** Inputs are described by k ("contention spread over k counters"), not as "low" or
  "high" contention.
- Statistical tests, confidence intervals and multiple-comparison handling for this metric are
  fixed in the analysis plan (ADR 0037) and implemented by ADR 0038.

## Consequences

- About twice the histogram runs of the former 2x2 design; the pilot checks that the campaign still
  fits, otherwise k in {1, 16, 256}.
- The CI correctness check (ADR 0024) and the native runner test cover k in {1, 4, 16, 256}.
- Amends ADR 0011 (input names and the "low/high contention" wording).

## Status

Accepted
