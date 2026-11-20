# ADR 0038: Inference implemented from the analysis plan

Date: 2026-10-18

## Context

The analysis plan (ADR 0037) fixes the statistics before the data: the per-run median, the
geometric mean per configuration, a bootstrap over runs, RQ1 as a speedup ratio, RQ2 as the
interaction contrast of ADR 0026, ratio effect sizes, predefined exclusions, and Holm over a
primary family of 10 contrasts. This ADR records how that plan is turned into code, so the final
tables leave no statistical choice to be made after seeing the data.

## Decision

### Contrasts

`analysis/inference.py` (now the package `analysis/inference/`) computes, on log run values:

- RQ2: `Δr = [c(browser atomic) - c(browser local)] - [c(native atomic) - c(native local)]` for
  each browser, k and N, where `c` is the mean of the log run values (the log of the geometric
  mean);
- RQ1: `[c(browser N=1) - c(browser N)] - [c(native N=1) - c(native N)]`, the log speedup ratio,
  for each browser, workload, input and N > 1.

Both are the same four-cell interaction (a difference of differences between two environments
and two conditions), resampled with the four groups of runs drawn independently (10 000
resamples, seed `0x5EED`). Effects are reported as `exp(estimate)` with 95 % percentile
intervals.

### Primary family

- The primary family is RQ2 at the maximum N and RQ1 for the filter on the `noise` input (the
  uniform random image the filter uses) at the maximum N.
- The maximum N is the pre-registered value passed as `--max-threads` (set by the thread count
  pilot, ADR 0044), not the largest N in the data, so the family does not depend on which
  thread counts happen to be in the data. A family other than the planned 10 contrasts is an
  error.
- For the primary contrasts, the output gives the two-sided bootstrap p-value (floored at one
  over the number of resamples), the Holm-adjusted p-value at α = 0.05, the decision, and the
  Bonferroni interval at `1 - 0.05 / m`, where m is the family size.
- Other contrasts are exploratory: interval only, no p-value.
- `--partial` (for pilot data) reports every contrast as exploratory, without p-values or Holm.

### Command and outputs

- `python3 -m analysis.results <dir> --contrasts c.csv [--shape s.csv]` loads the campaign with
  `harness.collect` and stops on checksum conflicts. It excludes runs above
  `--foreign-cpu-threshold` and, with `--strict`, runs that fail strict validation.
- It writes `c.json` with the options, the maximum N, whether the data was partial, every
  exclusion count overall and per environment, the failed and missing runs, the campaign's order
  seed and build (from `campaign.json`) and the commit. Machine state stays in each run's own
  JSON.
- The shape table gives, per configuration, the run count and the skewness of the run values and
  of their logs, to look at the real distributions before reading the contrasts.

## Consequences

- The final tables come from one command with no choices left to make after the data. The
  sensitivity checks of the plan are the `--summary mean` and `--center median` options and a
  run without `--foreign-cpu-threshold`.
- A campaign-sized dataset (86 contrasts) takes about 2 s.
- Looking at the real distributions, which this work also required, happens on the campaign
  data with the shape table.

## Status

Accepted; amended by ADR 0039 (absolute time ratios, clock check)
