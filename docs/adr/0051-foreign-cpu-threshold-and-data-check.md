# ADR 0051: Foreign CPU threshold of 0.25 s and the data check before analysis

Date: 2026-11-07

## Context

The measured cores are shielded from the rest of the system (ADR 0028), but the shield cannot
stop everything: per-CPU kernel threads and interrupts still run there. So every run records
`foreignCpuSeconds`: the busy time of the measured CPUs during the run (from `/proc/stat`) minus
the run's own CPU time. A high value means that something else ran on the measured cores while
the run was being timed.

The analysis plan (ADR 0037, decision D7) removes no statistical outliers. It has only three
exclusions: failed runs, runs that fail strict validation, and runs whose `foreignCpuSeconds`
is above a threshold. That threshold needed a value from the pilots before the full campaign
was analysed.

The campaign started at 06:44 UTC on 2026-11-07 without it. This ADR fixes it at about 07:20,
from pilot data only. No campaign result had been looked at: the only campaign data read by
then were the contexts of its first four runs, to check that they pass strict validation.
Fixing the value before seeing results keeps it from being tuned to them.

### Pilot data

`foreignCpuSeconds` over the 1638 pilot runs taken with the confined browsers (ADR 0045) and
quiet mode (ADR 0042), that is, every strict pilot from `pilot-mask-p` onwards:

| Environment | median | maximum |
|---|---|---|
| native | -0.008 s | 0.054 s |
| Firefox | -0.020 s | 0.062 s |
| Chrome | -0.001 s | 0.125 s |

Over all runs: 99th percentile 0.062 s, 99.9th 0.12 s, 4 runs above 0.1 s and none above
0.25 s. Negative values come from the 10 ms tick of `/proc/stat` measured against the run's own
CPU time.

The same task also required a check of checksums, failures, outliers and drift before any
analysis, with what to do in each case decided beforehand.

## Decision

Decided on 2026-11-07; the option recommended from the data above was applied:

- **The foreign CPU threshold is 0.25 s** (`analysis/quality.py`, `FOREIGN_CPU_THRESHOLD`, the
  default of `analysis.results`), twice the largest value of the pilots: a safety margin, which excluded no pilot run. Above it, something
  else ran on the measured cores during the run. Exclusion 3 of the plan uses it, together with
  strict validation (exclusion 2, `--strict`, which `make results` passes).
- **A data check runs before the analysis.** `python3 -m analysis.datacheck data/raw/campaign`
  writes a short report with:
  - runs done, missing and failed;
  - checksum conflicts;
  - runs failing strict validation, by reason;
  - runs above the threshold;
  - clock warnings;
  - the configurations whose run values trend with the execution order: Spearman's rho between
    `orderPosition` and the run value, over the runs that pass strict validation and the
    threshold, flagged when |rho| > 0.5 with at least 10 runs. With 30 runs and no drift,
    |rho| > 0.5 has a probability of about 0.5 % (0.54 % by permutation), so about one of the
    162 configurations can be flagged by chance.

  A checksum conflict, a missing run or a failed run makes the check exit with an error.
- **What is done with each finding, fixed now:**
  - failed, strictly invalid and above-threshold runs are excluded and counted (plan D7);
  - a checksum conflict stops the analysis until it is explained;
  - missing or failed runs are re-run by resuming the campaign before the analysis;
  - a trending configuration is reported and kept, and its contrast is marked in the results.
    The random run order spreads drift over every configuration, so in expectation drift adds
    variance rather than bias;
  - no outlier is removed.

## Consequences

- The plan's last open value is fixed before any campaign result is seen.
- The data check report is kept with the campaign data.

## Status

Accepted; sets the value left open by ADR 0037 (D7)
