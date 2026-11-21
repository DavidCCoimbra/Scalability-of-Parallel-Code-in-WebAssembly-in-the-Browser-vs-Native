# ADR 0082: Throughput and the absolute speedup are tabulated next to the relative speedup

Date: 2026-11-21

## Context

RQ1 is about relative speedup: T1 / TN inside one environment (ADR 0037). A relative speedup
says how well an environment scales and nothing about how fast it is: an environment with a slow
T1 can scale better than one with a fast T1 and still be slower at every N. The absolute time
ratios (ADR 0039) compare the environments at each N, but no table gave the two readings a
performance reader asks for first: how much work per second, and the speedup against the best
one-thread time available, which here is native's.

The audit of the methodology (2026-11-20) listed them as missing derived metrics. Both follow
from the per-run medians already measured; nothing is re-measured.

## Decision

- `analysis.throughput` writes `<campaign>-throughput.csv` for the main campaign, per
  configuration:
  - `ns_per_pixel` and `megapixels_per_second`, from the geometric centre of the per-run
    medians of the time of one pass and the image's pixels (8192x8192, one byte each, so a
    megapixel per second is also a megabyte of input per second);
  - `absolute_speedup` = T(native, 1) / T(environment, N) for the same workload, input and k,
    with a 95 % percentile bootstrap interval over runs (10 000 resamples, the plan's seed).
- The table is descriptive and post hoc. It is not part of the primary family (D8 of ADR 0037),
  carries no test, and changes no decision. The relative speedup stays the RQ1 metric.
- The campaign is read through the common loader (ADR 0081), with the plan's exclusions.

## Consequences

- The cost of the browser at one thread is visible in the same table as the scaling. At N = 8
  the filter reaches an absolute speedup of 6.00 in Chrome, where its relative speedup is 6.97
  (table `campaign-v2-scaling.csv`), because Chrome's one-thread filter runs at 0.860 of
  native's one-thread speed.
- For the atomic histogram with k = 1 the absolute speedup is below 0.45 at every N above 1 in
  every environment (0.44 native, 0.43 Firefox and 0.21 Chrome at N = 8): more threads on one
  contended counter are slower than native's one thread.
- "Absolute" here is against native's one-thread run of the same parallel code, not against a
  sequential implementation without Rayon; that limit is declared in ADR 0080.

## Status

Accepted
