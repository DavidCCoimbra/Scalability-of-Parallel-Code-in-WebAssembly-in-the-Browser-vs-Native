# ADR 0055: Weak scaling campaign

Date: 2026-11-08

## Context

The main campaign uses strong scaling (ADR 0003): the same input for every N, so each thread
gets 1/N of the work. In weak scaling the input grows with N, so the work per thread stays
fixed; ideal behaviour is then a constant time, and T1 / TN is the weak-scaling efficiency
(ideal 1).

ADR 0052 planned weak scaling as its own campaign with `heightPerThread` = 1024: the image is
8192 wide and 1024 x N rows high, so every thread gets the per-thread work of the main campaign
at N = 8. It complements strong scaling: the main campaign showed that the browsers' gap appears
when there is little work per parallel region, and weak scaling holds that work fixed while N
grows.

## Decision

Decided within the extras design agreed on 2026-11-07 (ADR 0052):

- **Workloads:** the filter (the RQ1 reference) and the local histogram at k = 1
  (synchronization-free, and the slowest local configuration), with the main campaign's W
  (15 and 71).
- **Every other parameter is the main campaign's:** N in {1, 2, 4, 6, 7, 8}, 30 runs, 10
  measured iterations, 3 s start delay, quiet mode and strict validation. That gives 1080 runs
  in one seeded order.
- **Clock resolution.** The shortest iteration (filter, N = 1, 8192 x 1024) takes about 3 ms in
  the browsers, above 100 times Firefox's 20 us clock resolution (the clock factor of
  ADR 0041); the data check confirms it per configuration.

## Consequences

- W is counted in iterations, and at N = 1 the iterations are about eight times shorter than
  the main campaign's, so the warm-up lasts less wall time and might not cover warm-up effects
  that depend on time rather than on iterations. The analysis therefore checks that the
  run values do not trend within the measured iterations, and any sign of incomplete warm-up is
  reported.
- The results are exploratory (ADR 0052).

## Status

Accepted
