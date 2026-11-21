# ADR 0078: How the RQ2 ratio is read: its two factors, and what moves it

Date: 2026-11-21

## Context

ADR 0026 fixed the RQ2 metric before the pilots: per environment the ratio r = T_atomic /
T_local at the same k and N, and between environments the difference of its logarithms,
reported as exp(delta r). It reads "how many times more the shared atomics cost, relative to
the local control, in the browser than natively". The primary contrasts of the main campaign
of `measured/v2` are in `data/tables/campaign-v2/campaign-v2-contrasts.csv`.

An audit of the analysis pointed out what the metric is arithmetically:

    exp(delta r) = (A_b / A_n) / (L_b / L_n)

with A the time of the atomic histogram, L of the local one, b a browser and n native. It is a
ratio of two ratios of absolute times. At N = 8 the atomic histogram takes 45 to 121 times
longer than the local one, so the local kernel is about 1 % of the atomic time, yet its own
environment gap, L_b / L_n, divides the result with full weight. A browser whose local kernel
is slower than native's gets a lower exp(delta r) even if its atomics cost exactly what
native's do.

ADR 0026 named a confound of the control at small k (store-to-load forwarding). It did not name
this one, which matters at large k.

## Decision

- **The metric stays.** exp(delta r) remains the primary RQ2 quantity, with the decisions of
  ADR 0037 and ADR 0077. It is always shown with its two factors.
- **A decomposition table is part of `make results`.**
  `data/tables/campaign-v2/campaign-v2-rq2-decomposition.csv` (`analysis.rq2_decomposition`) has,
  per browser and k at N = 8, the RQ2 ratio, the atomic ratio A_b / A_n, the local ratio
  L_b / L_n, and the ratio of the excesses (A_b - L_b) / (A_n - L_n): the time the shared
  counters add in the browser over the time they add natively. It is post hoc, not in the
  plan, so its intervals are uncorrected 95 % percentile bootstrap intervals and it decides
  nothing.

  | Browser, k | exp(delta r) | atomic A_b / A_n | local L_b / L_n | excess ratio [95 %] |
  |---|---|---|---|---|
  | Chrome, 1 | 2.176 | 2.122 | 0.975 | 2.148 [2.055, 2.246] |
  | Chrome, 4 | 1.776 | 1.913 | 1.077 | 1.918 [1.901, 1.935] |
  | Chrome, 16 | 1.446 | 1.781 | 1.231 | 1.785 [1.778, 1.792] |
  | Chrome, 256 | 0.415 | 0.508 | 1.224 | 0.502 [0.501, 0.503] |
  | Firefox, 1 | 0.994 | 1.010 | 1.016 | 1.010 [0.968, 1.055] |
  | Firefox, 4 | 0.969 | 0.987 | 1.018 | 0.987 [0.976, 0.997] |
  | Firefox, 16 | 0.816 | 1.010 | 1.239 | 1.009 [1.004, 1.014] |
  | Firefox, 256 | 0.794 | 0.949 | 1.195 | 0.947 [0.945, 0.948] |

- **What the table changes in the reading.**
  - *Firefox.* At k = 16 the RQ2 ratio is 0.816, a clear rejection, but Firefox's atomic
    histogram takes 1.010 times native's: the whole effect is its local histogram being 1.239
    times slower. At k = 256 the atomics cost 5 % less than natively in absolute terms, and
    the ratio of 0.794 mostly reflects the local kernel again (1.195). So "synchronization is
    relatively cheaper in Firefox" at k = 16 and 256 is true of the ratio and misleading as a
    statement about synchronization: in absolute time Firefox's atomic histogram takes
    1.010, 0.987, 1.010 and 0.949 times native's at k = 1, 4, 16 and 256 (the k = 1 interval
    contains 1; the others do not, by 1 % to 5 %). The k = 256 value is also the one that moved
    most between builds (below), so its size is not firm either.
  - *Chrome.* The atomic ratio stays near 1.8 to 2.1 for k = 1, 4 and 16, while exp(delta r)
    falls from 2.18 to 1.45 only because Chrome's local kernel gets slower relative to native
    as k grows. The excess ratio says the same: shared atomics add about twice the time in
    Chrome at k <= 16, and about half at k = 256.
- **Three more limits of the RQ2 numbers, stated with them.**
  - *The Firefox values depend on the build.* Between the first measured build and
    `measured/v2`, with the measurement corrections of ADR 0069, Firefox's exp(delta r) at
    k = 256 went from 0.620 to 0.794, and at k = 4 from 0.998 (not rejected) to 0.969
    (rejected). A 3 % effect is smaller than that shift between builds, so the k = 4 rejection
    is not read as an effect of the environment.
  - *The k = 1 cells are mixtures.* With one counter fought over by eight threads, a run lands
    on one of several time levels. The Chrome k = 1 ratio is 2.275 over the first 15 runs in
    campaign order and 2.082 over the last 15 with the geometric centre; both are inside the
    99.5 % interval [2.044, 2.317]. That split was chosen after the data, and it cannot tell a
    mixture of levels from a drift over the campaign; either way this cell is the widest.
  - *The two histograms do not share one iteration pipeline.* Only the local histogram passes
    its chunks through the grain control of ADR 0066 (`Grain::tasks`, which calls Rayon's
    `with_max_len`); the atomic one iterates its chunks directly. The comparison is between two
    programs that differ in more than the counters.

## Consequences

- RQ2 can be answered in two ways and the answer must say which: relative to each
  environment's own local control (the primary metric, ADR 0026), or in absolute time added
  by the shared counters (the excess ratio). They tell the same story for Chrome. For Firefox they differ
  most at k = 16: 0.816 by the ratio, 1.009 by the excess.
- No number of ADR 0037's family changes, and nothing is re-measured.
- The decomposition is regenerated and checked by `make tables-check` like every other table.

## Status

Accepted; amends ADR 0026
