# ADR 0037: Analysis plan fixed before the campaign

Date: 2026-10-18

## Context

Choosing the statistics after seeing the data invites picking the one that gives the nicest
answer. Several decisions had been left open on purpose until a plan existed: ADR 0005 leaves
the per-run summary to the pilot, ADR 0026 leaves the tests, intervals and multiple-comparison
handling of the RQ2 metric to an analysis plan, and ADR 0036 marks the analysis defaults as
provisional.

The analysis plan was written as a separate document and committed and tagged `analysis-plan`
on `main` in the working repository before the full campaign. This ADR, with ADR 0038 (its
implementation) and ADR 0039 (its first amendment), carries its content.

## Decision

Decided by the author on 2026-10-18, before any campaign data, from eight decisions (D1 to D8)
each weighed with its options, pros and cons; the recommended option was taken for all eight.

### Data and unit of analysis

- The unit of analysis is the run: one fresh process (ADR 0005). Iterations inside a run are not
  independent observations.
- Runs come from one campaign directory, loaded with `harness.collect` (ADR 0033). Only
  `measured` rows are used; warm-up and calibration rows are not part of the timing analysis.
- Run times are expected to be positive and right-skewed, and the questions are about ratios
  (speedup, relative cost of synchronization). The analysis therefore works on log times and
  reports ratios.

### Summaries (D1, D2)

- **D1, per run:** the median of its measured iterations. The mean of the measured iterations is
  reported as a sensitivity check.
- **D2, per configuration:** a configuration is (environment, workload, input, k, N). Its central
  value `T` is the geometric mean of its run values, `exp(mean(log run value))`, which matches
  working on log times.
- Speedup of a configuration is `T(N = 1) / T(N)` within the same environment, workload and
  input (ADR 0003); efficiency is speedup / N.

### Confidence intervals (D3)

- 95 % percentile bootstrap, 10 000 resamples, fixed seed `0x5EED`.
- Runs are resampled, never iterations. Groups that are different processes (N = 1 and N; atomic
  and local; native and browser) are resampled independently, because they are not paired.
- The bootstrap needs at least 10 runs per configuration. The number of runs is set by the pilot
  and is never below 10.

### RQ1: scaling, native vs browser (D4)

Estimation, not hypothesis tests. For each browser (Chrome, Firefox), workload, input and N:

- the efficiency of each environment, with its interval;
- the ratio of speedups `S(browser) / S(native)`, with its interval (1 means the browser scales
  like native).

### RQ2: synchronization (D5)

The metric of ADR 0026: `r(e, k, N) = log T(atomic) - log T(local)` for each environment e,
k in {1, 4, 16, 256} and N, that is the log of how much slower the shared-atomic histogram is
than the per-task local one. The estimand is

`Δr(browser, k, N) = r(browser, k, N) - r(native, k, N)`

for each browser, k and N. Its interval resamples the runs of the four cells (browser atomic,
browser local, native atomic, native local) independently. A contrast whose interval excludes 0
is reported as an effect of the environment on the cost of synchronization at that k and N.

### Effect sizes (D6)

- RQ1: the speedup ratio `S(browser) / S(native)`.
- RQ2: `exp(Δr)`, the ratio between the relative cost of the atomic variant in the browser and
  in native (1 means the same relative cost).
- Both are scale-free ratios with a direct reading. Cliff's delta between run values may be
  added as a complement; it does not replace the ratios.

### Exclusions (D7)

No statistical outlier removal (no IQR or z-score rules). Only these exclusions, decided in
advance, are allowed, and every one is counted and reported per environment and configuration:

1. failed runs (`<run>.error.json`, ADR 0027);
2. runs that fail strict validation (`harness.context.validate`, strict);
3. runs whose `foreignCpuSeconds` (CPU time of other processes on the measured CPUs, ADR 0028)
   is above a threshold set from the pilot data before the full campaign.

### Multiple comparisons (D8)

- **Primary contrasts,** a family of 10:
  - RQ2: `Δr` at the campaign's maximum N, for k in {1, 4, 16, 256} and both browsers
    (8 contrasts);
  - RQ1: the log speedup ratio `log S(browser) - log S(native)` at the maximum N for the
    filter, for both browsers (2 contrasts).
- **p-values:** each primary contrast is a log ratio whose null value is 0. Its two-sided
  bootstrap p-value is `2 * min(P*(estimate <= 0), P*(estimate >= 0))`, the share of the
  bootstrap estimates on each side of 0 (from the same resamples as its interval), floored at
  `1 / 10 000`.
- **Decision:** Holm at a family-wise α = 0.05 over the 10 p-values.
- **Intervals:** primary contrasts are shown with Bonferroni intervals at `1 - 0.05 / 10` =
  99.5 % (percentile bootstrap), which hold simultaneously for the family; with 10 000 resamples
  each tail still has 25 estimates. The pilot checks that the run count gives stable 99.5 %
  bounds.
- Everything else (other N, other workloads and inputs, efficiency curves) is exploratory:
  reported with uncorrected 95 % intervals and labelled exploratory.

### Sensitivity checks

- Per-run mean instead of median (D1).
- Median of run values instead of the geometric mean (D2).
- With and without exclusion 3 (`foreignCpuSeconds`).

A conclusion that changes under a sensitivity check is reported as not robust.

### Defaults of the code

- `analysis.v0` (ADR 0036) defaults to D1 and D2: median per run, geometric mean per
  configuration.

### Values left to the pilot

The plan leaves these values to pilot data, recorded as dated amendments before the first run
of the full campaign. Their final values and the ADRs that set them:

| Value | Final value | ADR |
|---|---|---|
| Image size | 8192x8192 | 0041 |
| Warm-up W per workload | per workload | 0043 |
| Runs per configuration (at least 10) | 30, with 10 measured iterations per run | 0047 |
| `foreignCpuSeconds` threshold for exclusion 3 | 0.25 s | 0051 |
| The campaign's maximum N | 8, with N = 1, 2, 4, 6, 7, 8 | 0044 |

### Later amendments of the plan

Each change to the plan was added as a dated amendment with its reason; the tagged version stays
the reference.

- 2026-10-18 (review of the plan, before any data): the Holm decision is defined on bootstrap
  p-values and the primary intervals are Bonferroni 99.5 % intervals, as written above; D8
  itself is unchanged.
- 2026-10-19 (methodology review, before any data): absolute time ratios and a clock resolution
  warning (ADR 0039).
- 2026-11-06 (size pilot, before any campaign data): the clock factor is 100, not 1000, and the
  image is 8192x8192 (ADR 0041).
- 2026-11-07 (before any campaign result was seen): the foreign CPU threshold is 0.25 s, twice
  the pilots' maximum, and the data check of ADR 0051 runs before the analysis.
- 2026-11-09 (after the campaign and after its primary results were published in the paper, at a
  methods review): a robustness check is added, not a change of the primary
  analysis. It was written after the robustness results were computed; they agree with every
  primary decision, so nothing in the paper hinges on that order. Each of the 10 primary
  contrasts is also tested with Mann-Whitney U and Cliff's delta on per-run ratios
  (log(T1 / TN) for RQ1, log(T atomic / T local) for RQ2; the two runs of a ratio are paired by
  repetition index, browser against native is unpaired), with Holm over the 10
  (`analysis.robustness`; the table was `data/tables/campaign/campaign-robustness.csv`, and for
  the final v2 build it is `data/tables/campaign-v2/campaign-v2-robustness.csv`). The bootstrap
  decisions stay the reported ones; a disagreement would be reported as not robust.

## Consequences

- The plan was in git before the data, so any later change is visible as a dated amendment.
- The pilot still had to set the number of runs (at least 10), the `foreignCpuSeconds` threshold
  and the maximum N, recorded before the full campaign (table above).
- ADR 0038 implements the RQ2 contrast and the Holm correction from this plan.

## Status

Accepted; amends ADR 0036 (analysis defaults); amended by ADR 0039 (absolute time ratios, clock check) and ADR 0041 (clock factor, image size); amended by ADR 0077 (sensitivity checks run, RQ1 for Chrome not robust)
