# ADR 0053: Parameters of the extras campaign

Date: 2026-11-07

## Context

ADR 0052 defined four new workloads (`hist-atomic-private`, `hist-atomic-packed`, `sort` and
`sort-unstable`) to run in one interleaved campaign with their controls. Their warm-up W and
input size had to be fixed from a pilot, as for the main workloads (ADR 0043).

The pilot `pw-extras` (`data/earlier/pilot/pw-extras`) ran every new workload with no warm-up and
60 measured iterations, at N = 1 and N = 8, two runs per environment (72 runs, no failures).
From the pilot (about 5 s per run plus the iterations), the full design would take about 30 h:
4 histogram variants x 3 levels of k, plus 2 sorts, in 3 environments, at 6 thread counts, with
30 runs each.

## Decision

Decided on 2026-11-07, following the rule that the campaign is shortened by cutting
configurations, never runs (30 runs per configuration, ADR 0047):

- **Warm-up** by the criterion of ADR 0043, computed by `analysis.warmup`: W = 5 for every new
  workload, except `hist-atomic-private` at k = 256, which gets W = 8. The basis is thin: two
  runs per environment, at N = 1 and 8 only, and the same W is used at every N of the campaign.
  The controls keep the main campaign's W.
- **Input:** 8192x8192 for every workload, the sorts included. The fastest configuration
  takes 47 ms per iteration at N = 8, far above 100 times the browser clock resolution (the
  clock factor of ADR 0041), so no other sort input size is needed.
- **k in {1, 256}**, the two ends of contention (every pixel on one counter, and contention
  spread over 256 counters). k = 16 is left out to keep the campaign at about 21 h by the
  pilot's estimate. The estimate was pessimistic: the campaign took 16 h (2026-11-07 21:59 to
  2026-11-08 14:04).
- **Configurations:** `hist-local`, `hist-atomic-private`, `hist-atomic` and
  `hist-atomic-packed` at k = 1 and 256, plus `sort` and `sort-unstable` on the noise input:
  10 configurations, N in {1, 2, 4, 6, 7, 8}, 30 runs, 5400 runs in one seeded random order.
  The controls (`hist-local` and `hist-atomic`) are measured again instead of reusing the main
  campaign's runs, so every comparison is between interleaved runs of the same commit.

## Consequences

- The ladder local / private atomic / shared atomic / packed atomic is measured at the two
  extremes of contention only; the shape between them (k = 4 and 16) comes from the main
  campaign.
- The controls give a second, independent measurement of the main campaign's k = 1 and k = 256
  configurations, which serves as a reproducibility check.
- The results are exploratory (ADR 0052): 95 % intervals, not part of the Holm-corrected family
  of primary contrasts.

## Status

Accepted
