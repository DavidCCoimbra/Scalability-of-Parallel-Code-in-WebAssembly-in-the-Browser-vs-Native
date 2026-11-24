# ADR 0065: Results of the cutoff campaign

Date: 2026-11-09

## Context

ADR 0064 designed the cutoff campaign, which asks below which image size parallelizing stops
paying. It has five sizes (512^2 to 8192^2) with K = (8192 / side)^2 passes per timed sample,
so that every sample is long enough for the browser clock; the filter and hist-local k256; N in
{1, 2, 4, 8}; native, Chrome and Firefox; 30 runs per configuration. It also added two native
K = 1 control campaigns at 512^2 and 2048^2, to see whether repeating the work K times changes
the time per pass. All seven campaigns ran on the night of 2026-11-08/09 on build `4dace4db`
(tag `measured/cutoff`). This ADR records what they found and how they are read.

The tables named below are those of this build, kept in `data/earlier/v1/tables/cutoff`. The
campaign was run again on the v2 build (ADR 0069) and on v3 (`data/tables/cutoff-v3/`).

Data quality (`data/tables/cutoff/cutoff-*-quality.md`): 4080 runs, none missing or failed, no
checksum conflict, none above the foreign CPU threshold, none under 100 times the clock
resolution. One configuration trends with the execution order (control 2048, native filter
N = 1, rho = +0.51 over 30 runs, later runs slower). The trend is small: the geometric mean of
the first 15 runs is 1489 us and of the last 15 runs 1495 us (0.4 %), and the section 5 ratios
computed from either half differ by at most 0.04 (N = 8: 1.69 and 1.73).

## Decision

Record the following as the cutoff results. They are exploratory (ADR 0052): point estimates
with bootstrap intervals, no test.

### 1. Break-even lies below 512^2 everywhere

At every size, environment, workload and N in {2, 4, 8}, the speedup is above 1
(`data/tables/cutoff/cutoff-table.csv`). The smallest is the Chrome and Firefox filter at
512^2, N = 8: 1.97 and 1.89, with T1 per pass of 116 and 133 us. A sequential fallback in the
strict sense (parallel slower than serial) is therefore not reached at this study's sizes: it
lies below about 100 us of sequential work in all three environments.

### 2. The "worth it" cutoff (efficiency 0.5) at N = 8

With N = 2 and N = 4 the efficiency (speedup / N) stays above 0.5 at every size. At N = 8 it
crosses 0.5 between 512^2 and 1024^2 everywhere (`data/tables/cutoff/cutoff-estimates.csv`,
log-linear interpolation, 95 % interval):

| Workload | Environment | Side | Interval | Sequential work at the crossing |
|---|---|---|---|---|
| filter | native | 621 | 618 to 624 | 126 us |
| filter | Chrome | 993 | 988 to 999 | 392 us |
| filter | Firefox | 1011 | 999 to 1021 | 469 us |
| hist-local k256 | native | 695 | 682 to 707 | 188 us |
| hist-local k256 | Chrome | 814 | 798 to 830 | 324 us |
| hist-local k256 | Firefox | 888 | 870 to 906 | 384 us |

So, to use 8 threads at half efficiency or better, the browsers need 3.1 (Chrome) and 3.7
(Firefox) times the sequential work that native needs for the filter, and 1.7 and 2.0 times for
hist-local.

A caveat for hist-local: it splits the image into 64 KB chunks (`CHUNK_BYTES`), so a 512^2
image has 4 chunks and a 1024^2 image 16. At 512^2, N = 8 can keep at most 4 threads busy,
which is why its speedup there is below N = 4's in all three environments (native 2.68 against
2.92). Its crossing at N = 8 is therefore partly a granularity limit of the workload, not only
the fork-join cost. The filter splits per row (512 rows at 512^2) and has no such limit.

### 3. The fork-join model predicts the order of magnitude

The model's worth-it point (W = N F, ADR 0064), with the calibrated fork-join cost F at N = 8
(native 10.7 us, Chrome 107.5 us, Firefox 60.0 us), gives 86, 860 and 480 us. Measured: 126
(native), 392 (Chrome) and 469 us (Firefox) for the filter. Native and Firefox land within a
factor 1.5 of the model; Chrome's measured cutoff is 2.2 times below it. That is the direction
ADR 0064 predicted. Chrome's F is dominated by the cold wake-up of parked workers
(`Atomics.wait`), and K back-to-back passes pay it once per sample, because the other K - 1
passes find the workers still spinning.

### 4. The 100:1 rule: only native meets it at the largest size

The common rule of thumb asks for sequential work at least 100 times the fork-join cost, so that
the fork-join is at most about 1 % of TN. It is checked at 8192^2, N = 8, the largest measured
size: the fork-join share of TN is 0.33 % natively (both workloads), 1.45 % in Firefox and 2.5
to 2.8 % in Chrome. By that rule the browsers would need a larger region than this study
measured (the model's 1 % side with this campaign's T1: filter about 5000 native, 10200
Firefox, 14700 Chrome; `data/tables/cutoff/cutoff-model.csv`).

### 5. The K = 1 controls: hist-local is unaffected, the filter is not

The time per pass at K = 1 divided by the time per pass at K = 256 (512^2) or K = 16 (2048^2),
native:

| Side | Workload | N = 1 | N = 2 | N = 4 | N = 8 |
|---|---|---|---|---|---|
| 512 | filter | 1.04 | 1.13 | 1.27 | 1.25 |
| 512 | hist-local | 0.97 | 1.00 | 1.03 | 1.05 |
| 2048 | filter | 1.14 | 1.38 | 1.66 | 1.71 |
| 2048 | hist-local | 1.00 | 1.01 | 1.01 | 1.02 |

Hist-local's cutoff describes a single call as well as a repeated one. The filter's does not:
with one pass per sample, native N = 8 reaches a speedup of 2.79 at 512^2 (efficiency 0.35) and
4.55 at 2048^2 (0.57), against 3.37 and 6.85 with K passes. The native single-call filter
cutoff therefore lies between 512^2 and 2048^2, above the 621 of the table, and the K-pass
figures are a lower bound for it.

A hypothesis, not verified: between two timed samples the checksum (outside the timed region)
reads the filter's whole output on the main thread. The next pass's workers then first have to
take those cache lines back from that core, a coherence cost that grows with N and is paid once
per sample. Hist-local's checksum reads 256 counters, and its output is those counters, so it
has no such cost. The browsers' K = 1 behaviour is not measured, because their clock cannot
time one pass at these sizes (ADR 0064).

### 6. Non-monotonic filter at 4096^2

The filter speedup at N = 8 drops at 4096^2 in Chrome (6.05, against 6.60 at 2048^2) and rises
natively (7.53, against 7.01 at 8192^2). At 4096^2 the input and output together are 32 MB,
close to the 36 MB L3 cache. This is noted, not explained; the cutoffs above come from the 512
to 1024 crossing and do not depend on it.

## Consequences

- **The answer.** Below which size does parallelizing stop paying? For break-even, never at
  these sizes. For half efficiency at N = 8, below about 130 to 190 us of sequential work
  natively and 320 to 470 us in the browsers (2 to 4 times more), with the filter's native
  value a lower bound (the control, section 5).
- **Advice for web developers.** Fork only regions worth at least about 0.5 ms of sequential
  work in the browser at 8 threads; below that, use fewer threads or run sequentially. This is a
  lower bound: it comes from K back-to-back warm passes, a single call is not measured in the
  browsers (section 5), and natively a single pass of the filter is up to 1.71 times slower at
  N = 8.
- **Phase 2.** Applying a threshold inside the workloads, with a grain-size sweep, is ADR 0066,
  approved on 2026-11-09.
- **Reproduction.** `make cutoff-results` regenerates every number in this ADR from
  this build's `data/raw/cutoff-*`. Those runs are not in this repository; the tables are.

## Status

Accepted
