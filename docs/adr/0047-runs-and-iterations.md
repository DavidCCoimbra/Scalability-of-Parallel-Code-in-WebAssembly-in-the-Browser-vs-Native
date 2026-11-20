# ADR 0047: 30 runs per configuration and 10 measured iterations per run

Date: 2026-11-07

## Context

Two numbers set the precision and the cost of the campaign:

- the number of **runs** per configuration (a run is one fresh process, the unit of analysis,
  ADR 0005);
- the number of **measured iterations** per run (after the W warm-up iterations; their median
  is the run's value, ADR 0037).

The analysis plan (ADR 0037) asks for at least 10 runs per configuration. It leaves the exact
number to pilot data, judged by how stable the 99.5 % Bonferroni intervals of the primary
contrasts are. The primary contrasts are the 10 contrasts the plan tests formally: the RQ1
speedup ratio of the filter and the RQ2 interaction at k = 1, 4, 16 and 256, for each browser,
at N = 8.

### Run count pilot

The pilot (`harness/campaigns/pilot-runs-rq{1,2}.json`, 2026-11-07; in the working repository)
ran 30 runs of every cell the primary contrasts need:

- the filter at N = 1 and 8 (RQ1);
- `hist-atomic` (shared atomic counters) and `hist-local` (per-task local counters) at k = 1,
  4, 16 and 256 and N = 8 (RQ2);
- in the three environments, at 8192x8192, with the final W (ADR 0043) and 10 measured
  iterations.

That is 900 runs, 0 failed, all with `escapedProcesses` = 0, from commit 4960dd2 (tag
`measured/pilot-runs`).

`analysis/runcount.py` draws subsamples of n of the 30 runs (20 subsamples, 1000 bootstrap
resamples each) and reports the mean half-width of the 99.5 % percentile interval of each
contrast. The width is in logs, which is about a relative width:

| Contrast (N = 8) | n = 10 | n = 20 | n = 30 | n for 5 % (fit) |
|---|---|---|---|---|
| RQ1 Chrome filter | 1.1 % | 0.8 % | 0.7 % | 10 (floor) |
| RQ1 Firefox filter | 0.9 % | 0.6 % | 0.5 % | 10 (floor) |
| RQ2 Chrome k = 1 | 12.5 % | 9.2 % | 7.5 % | 59 |
| RQ2 Chrome k = 4 | 2.2 % | 1.5 % | 1.3 % | 10 (floor) |
| RQ2 Chrome k = 16 | 1.9 % | 1.4 % | 1.2 % | 10 (floor) |
| RQ2 Chrome k = 256 | 1.9 % | 1.4 % | 1.1 % | 10 (floor) |
| RQ2 Firefox k = 1 | 9.7 % | 7.0 % | 5.8 % | 36 |
| RQ2 Firefox k = 4 | 5.5 % | 4.2 % | 3.4 % | 12 |
| RQ2 Firefox k = 16 | 6.6 % | 4.7 % | 4.0 % | 16 |
| RQ2 Firefox k = 256 | 9.1 % | 6.8 % | 5.5 % | 28 |

Subsamples of close to 30 runs overlap almost fully with the pilot itself, so the widths at
n = 25 and 30 understate the width a new sample would have. The last column therefore fits
half-width = c / sqrt(n) on n = 5 to 20 and solves for a 5 % width.

A 5 % target in every contrast would need about 60 runs (Chrome k = 1), which would take more
campaign time than was available. On the other hand, the RQ2 effects are large: in the pilots,
Chrome `hist-atomic` k = 1 takes about 2.5 times the native time at N = 8 while `hist-local`
is close to native, an effect of about 0.9 in logs. An interval half-width of a few percent is
small against that.

### Iteration pilot

For the number of iterations, the long runs of the warm-up pilot (ADR 0043) were reused. For
each run, the median of the first M iterations after W was compared with the median of the
iterations after those M; if more iterations helped, the two would agree more often as M grows.

- Within 1 %, no M reaches agreement in 95 % of the runs (90.7 % at M = 10, 93.8 % at M = 30).
- Within 2 %, the share stays between 93 % and 96 % for every M (M = 10: 94.1 %, M = 15:
  95.8 %, M = 20: 94.9 %).
- The runs that miss are Firefox `hist-local` at N = 8 (6 of the 7 misses at M = 10, 4 of the
  5 at M = 15).

In the 30-run pilot, 24 of 120 Firefox `hist-local` runs have an iteration more than 1.3 times
their median (a "burst"); native has 2 and Chrome 0. These runs have no extra foreign CPU time
(CPU time used on the measured cores by processes outside the run, ADR 0028): their median is
-0.011 s, against -0.028 s over all of its runs. So the bursts come from inside Firefox
(garbage collection or its helper threads are possible causes), not from the machine.

## Decision

Decided on 2026-11-07. The author had asked for 30 runs, and the option recommended from the
data above was applied:

- **30 runs per configuration.** The 99.5 % half-width is then about 1 % for RQ1 and about
  7.5 % for RQ2 (widths from the 30 pilot runs, which slightly understate those of a new
  sample), small against the RQ2 effects seen in the pilots.
- **10 measured iterations per run.** The agreement of the per-run median does not improve
  steadily with more iterations: it plateaus at 93 to 96 % within 2 %, because the runs that
  miss are Firefox bursts, not short samples. M = 15 would add about 2.7 hours, mostly in
  `hist-atomic`, without removing the bursts. The bursts are variance between runs, which the
  30 runs carry into the intervals.
- **Two thresholds were relaxed after seeing the data:** the 5 % half-width target proposed
  before the pilot, and the 1 % agreement. They are dropped as decision rules; the achieved
  widths and agreement above are reported instead.
- **Scope of the pilot.** Runs and iterations were piloted at N = 8 (and N = 1 for the filter),
  with the W of ADR 0043. They are assumed to transfer to N = 2, 4, 6 and 7 and to the
  histogram at N = 1, and the widths hold for those W.

## Consequences

- The Firefox `hist-local` bursts are a threat to the validity of its within-run medians at
  N = 8 and are reported with the RQ2 results. (ADR 0048 later traced them to Firefox start-up
  work, which a start delay removes.)
- The full campaign (9 workloads, N = 1, 2, 4, 6, 7, 8, three environments, 30 runs) takes
  about 9.6 hours of runs by the pilot timings, two thirds of it `hist-atomic`.
- The paper reports the achieved interval widths, so a reader can judge the precision of each
  RQ2 contrast.

## Status

Accepted; sets the value left open by ADR 0037. Amended by ADR 0048.
