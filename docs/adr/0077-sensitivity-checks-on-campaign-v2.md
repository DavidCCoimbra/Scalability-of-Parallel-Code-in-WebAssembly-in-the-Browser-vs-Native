# ADR 0077: The plan's sensitivity checks, run on the main campaign of measured/v2

Date: 2026-11-21

## Context

The analysis plan (ADR 0037), fixed before any campaign data, lists three sensitivity checks on
the primary contrasts and one rule:

- the per-run mean instead of the per-run median;
- the median of the run values as the centre of a configuration, instead of the geometric mean;
- no exclusion of runs by foreign CPU time;
- "a conclusion that changes under a sensitivity check is reported as not robust".

ADR 0038 implemented them as options of `analysis.results`, but no make target ran them and no
table held their results. The audit of the final repository found the gap. This record runs
them on `data/raw/campaign-v2` and applies the rule. Nothing here was chosen after seeing the
data: the checks and the rule are those of the plan.

The plan also defines no smallest effect of interest: it says when a contrast is rejected, not
how small a difference would count as "the same".

## Decision

- **The checks are part of `make results`.** `make sensitivity` writes the three contrast
  tables under `data/tables/campaign-v2/sensitivity/` and
  `data/tables/campaign-v2/campaign-v2-sensitivity.csv`, which puts the ten primary contrasts
  side by side with a `robust` column (`analysis.sensitivity`). `analysis.results` gains
  `--no-foreign-cpu-threshold` for the third check.
- **Result: nine of the ten primary decisions are robust.** Every RQ2 decision (Chrome and
  Firefox at k = 1, 4, 16, 256) and the RQ1 decision for Firefox are the same under the three
  checks (the third cannot differ here; see below).
- **RQ1 for Chrome is not robust.** Ratio of speedups at N = 8, Chrome over native, with the
  Bonferroni 99.5 % interval and the Holm-adjusted p-value:

  | Analysis | Effect | 99.5 % interval | Holm p | Rejected |
  |---|---|---|---|---|
  | Primary (per-run median, geometric centre) | 0.990 | [0.952, 1.028] | 0.904 | no |
  | Per-run mean | 0.991 | [0.952, 1.029] | 0.756 | no |
  | Median centre | 0.992 | [0.989, 1.001] | 0.018 | yes |
  | No foreign-CPU exclusion | 0.990 | [0.952, 1.028] | 0.904 | no |

  The primary decision stays the reported one, as the plan says, and is reported as not robust.
  The point estimate hardly moves (0.990 to 0.992); what changes is the width, for two reasons
  that both hold:
  - *Slow T1 runs widen the geometric-mean interval.* Each configuration has 30 runs. At
    N = 1, three native runs and two Chrome runs of the filter are 1.21 times their
    configuration's median; no Firefox run and no N = 8 run is. They raise the geometric mean
    of T1 by 1.9 % natively and 1.2 % in Chrome. Without those five runs the primary estimate
    is 0.996 (and Firefox's 1.070). A factor of 1.21 is what a core at about 2.6 GHz against
    3.2 GHz would give, which fits the degraded P-core of this machine, but no run records
    the frequency of the core it ran on, so that cause is not established. The per-core check
    of 2026-11-21 does not support it: pinned to that core the filter is as fast as on the
    others (ADR 0085).
  - *The median-centre interval is narrow partly by construction.* The bootstrap of a median
    over 30 runs can only take values that occur in the sample, so its distribution is
    discrete and its interval can be much narrower than the spread of the runs. The rejection
    under this check is therefore partly a property of the estimator, not only of the data.

  Either way the conclusion is the same: the data do not settle whether Chrome's speedup at
  N = 8 differs from native's by about 1 %.
- **`robust` compares decisions, and decisions come from Holm.** The plan decides with
  Holm-adjusted p-values and reports Bonferroni 99.5 % intervals. The two can disagree, because
  Holm tests the later-ranked contrasts at a level looser than 0.005: under the median centre
  RQ1 for Chrome is rejected while its interval still contains 1, and under the per-run mean
  RQ1 for Firefox is rejected while the lower end of its interval is 1.000.
- **The third check is vacuous on this campaign.** No run is above the foreign-CPU threshold,
  so the table without the exclusion equals the primary one line by line.
- **Non-rejections are stated as bounds, never as equality.** For the two primary contrasts
  that are not rejected, the data support only:
  - RQ1, Chrome: the speedup at N = 8 is within 3.7 % of native's (95 % interval
    [0.963, 1.016]) or 4.8 % (99.5 % interval [0.952, 1.028]);
  - RQ2, Firefox at k = 1: the relative cost of the shared atomics is within 4.7 % of native's
    (95 % interval [0.953, 1.037]) or 6.3 % (99.5 % interval [0.937, 1.055]).

  Any threshold of practical importance applied to these would be chosen after the data and
  must be labelled so.
- **RQ1 for Firefox.** Rejected under every check (1.049, 1.037, 1.065). Under the per-run
  mean the lower end of its 99.5 % interval is 1.000, so the size of the effect, not its
  existence, depends on the summary.

## Consequences

- A reader can no longer take "Chrome scales like native" as an established equality: it is a
  difference of about 1 % whose sign and significance depend on the centre, bounded at about
  5 %.
- `make tables-check` covers the new tables like every other.
- The two readings of ADR 0037 that looked contradictory are settled in the plan's sense: RQ1
  is reported as an estimate with its interval (its D4), and it is also one of the ten tested
  contrasts (its D8).

## Status

Accepted; amends ADR 0037 and ADR 0038
