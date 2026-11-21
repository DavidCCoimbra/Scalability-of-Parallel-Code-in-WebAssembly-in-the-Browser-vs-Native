# ADR 0079: The results on measured/v2, in one place

Date: 2026-11-21

## Context

ADR 0069 made `measured/v2` the build of every reported number and had every campaign run
again on it. The result records written before that (ADR 0054, 0056, 0058, 0061, 0065, 0067)
hold the numbers of the build they were first measured on, and say so. No record held the
numbers of `measured/v2` themselves: they existed only as tables under `data/tables/*-v2`.

A reader of the decision records could therefore not tell which numbers the study stands on
without opening the tables. This record lists them, each with its table. It adds no analysis:
every value is copied from a committed table that `make tables-check` regenerates.

## Decision

The reported results are those below. Times are geometric means over 30 runs of the per-run
median; intervals are 95 % percentile bootstrap intervals unless a 99.5 % interval is named;
N is the thread count; "over native" is a ratio of absolute times at the same N.

### Main campaign (`data/tables/campaign-v2/`, 4860 runs, none excluded)

Speedup T1 / T8 and efficiency (`campaign-v2-scaling.csv`), and time over native at N = 1 and
N = 8 (`campaign-v2-contrasts.csv`, ABS rows):

| Workload | Environment | T1 (ms) | T8 (ms) | Speedup at N = 8 | Efficiency | Over native, N = 1 | Over native, N = 8 |
|---|---|---|---|---|---|---|---|
| filter | native | 23.0 | 3.27 | 7.04 [6.91, 7.20] | 0.880 | - | - |
| filter | Chrome | 26.7 | 3.84 | 6.97 [6.87, 7.11] | 0.871 | 1.163 | 1.175 |
| filter | Firefox | 30.6 | 4.15 | 7.39 [7.36, 7.42] | 0.924 | 1.332 | 1.269 |
| hist-local k = 1 | native | 154.9 | 19.49 | 7.95 | 0.994 | - | - |
| hist-local k = 1 | Chrome | 150.8 | 19.00 | 7.94 | 0.992 | 0.974 | 0.975 |
| hist-local k = 1 | Firefox | 155.7 | 19.80 | 7.86 | 0.983 | 1.005 | 1.016 |
| hist-local k = 256 | native | 27.0 | 3.42 | 7.88 | 0.985 | - | - |
| hist-local k = 256 | Chrome | 33.6 | 4.19 | 8.01 | 1.002 | 1.245 | 1.224 |
| hist-local k = 256 | Firefox | 34.6 | 4.09 | 8.47 | 1.059 | 1.284 | 1.195 |
| hist-atomic k = 1 | native | 379.6 | 870.6 | 0.436 | 0.055 | - | - |
| hist-atomic k = 1 | Chrome | 698.0 | 1847.7 | 0.378 | 0.047 | 1.838 | 2.122 |
| hist-atomic k = 1 | Firefox | 379.7 | 879.5 | 0.432 | 0.054 | 1.000 | 1.010 |
| hist-atomic k = 256 | native | 379.6 | 414.4 | 0.916 | 0.115 | - | - |
| hist-atomic k = 256 | Chrome | 411.9 | 210.5 | 1.957 | 0.245 | 1.085 | 0.508 |
| hist-atomic k = 256 | Firefox | 379.8 | 393.1 | 0.966 | 0.121 | 1.001 | 0.949 |

The k = 4 and k = 16 rows and every other N are in the same tables.

- **RQ1** (ratio of speedups at N = 8, browser over native, 99.5 % interval): Chrome 0.990
  [0.952, 1.028], not rejected and not robust; Firefox 1.049 [1.015, 1.074], rejected (ADR 0077).
- **RQ2** (exp(delta r) at N = 8, 99.5 % interval): Chrome 2.176 [2.044, 2.317], 1.776
  [1.752, 1.801], 1.446 [1.423, 1.473] and 0.415 [0.407, 0.423] at k = 1, 4, 16, 256; Firefox
  0.994 [0.937, 1.055], 0.969 [0.954, 0.984], 0.816 [0.805, 0.826] and 0.794 [0.779, 0.806].
  All rejected except Firefox at k = 1. They are read with their two factors (ADR 0078).
- **Fork-join** (`campaign-v2-fork-join.csv`, warm empty broadcast at N = 8, median of run
  medians): native 8.8 us, Chrome 110 us, Firefox 60 us (ADR 0076).

### Extras campaign (`data/tables/extras-v2/`)

Speedup at N = 8, T8, and time over native at N = 8:

| Workload | native | Chrome | Firefox |
|---|---|---|---|
| hist-atomic-private k = 1 | 7.96, 47.7 ms | 7.93, 88.0 ms, 1.846 | 7.94, 47.8 ms, 1.003 |
| hist-atomic-private k = 256 | 7.97, 47.6 ms | 7.91, 52.1 ms, 1.094 | 7.94, 47.8 ms, 1.005 |
| hist-atomic-packed k = 1 | 0.438, 869.9 ms | 0.384, 1821.9 ms, 2.094 | 0.440, 863.7 ms, 0.993 |
| hist-atomic-packed k = 256 | 0.777, 488.6 ms | 0.562, 725.0 ms, 1.484 | 0.773, 491.4 ms, 1.006 |
| sort (stable) | 7.80, 188.2 ms | 7.78, 205.7 ms, 1.093 | 7.79, 195.7 ms, 1.040 |
| sort-unstable | 6.39, 84.4 ms | 6.22, 109.9 ms, 1.302 | 6.24, 109.3 ms, 1.295 |

### Weak scaling (`data/tables/weak-v2/weak-v2-scaling.csv`)

Weak-scaling efficiency T1 / T8 with 1024 rows per thread: filter 0.855 native, 0.852 Chrome,
0.913 Firefox; hist-local k = 1 0.997, 0.995 and 0.996.

### SIMD build variants (`data/tables/simd-v2/simd-v2-variants.csv`)

Filter at N = 8: efficiency, the excess time TN - T1 / N, and time over the same environment's
baseline build:

| Build | native | Chrome | Firefox |
|---|---|---|---|
| scalar | 0.981, 211 us, 3.44 | 0.968, 546 us, 4.40 | 0.982, 330 us, 4.33 |
| baseline (128-bit) | 0.880, 391 us, 1 | 0.871, 494 us, 1 | 0.924, 316 us, 1 |
| avx2 (native only) | 0.727, 728 us, 0.818 | - | - |

### Hybrid P+E campaign (`data/tables/hybrid-v2/hybrid-v2-scaling.csv`)

Filter time and speedup within the campaign: native 3.50 ms at N = 8 and 2.83 ms at N = 20
(speedup 6.49 and 8.02); Chrome 4.06 and 3.47 ms (6.61 and 7.72); Firefox 4.35 and 3.57 ms
(7.05 and 8.59).

### Cutoff (`data/tables/cutoff-v2/cutoff-estimates.csv`)

No workload reaches break-even (speedup 1) at any size measured, down to 512^2, in any
environment. The size at which efficiency is 0.5 at N = 8, as an image side with its interval
and as sequential work per region:

| Workload | native | Chrome | Firefox |
|---|---|---|---|
| filter | 606 [603, 609], 123 us | 1003 [997, 1009], 399 us | 1011 [1002, 1020], 469 us |
| hist-local k = 256 | 697 [685, 708], 186 us | 837 [820, 854], 339 us | 862 [836, 887], 367 us |

These come from K back-to-back passes and are lower bounds for a single call (ADR 0065).

### Grain sweep (`data/tables/grain-v2/grain-best.csv`)

At 8192^2 the best grain is 4 rows for the filter in every environment (flat from 1 to 8 rows
natively, 2 to 4 in Chrome, 2 to 8 in Firefox) and, for hist-local k = 256, 128 KB natively
(flat from 64 KB to 4096 KB), 64 KB in Chrome and 128 KB in Firefox (flat from 64 to 128 KB in
both). Rayon's adaptive split is within 0.5 % (filter) to 2.5 % (hist-local, Chrome) of the
best. At 1024^2 the adaptive split is 4 % to 19 % slower than the best fixed grain.

### Hardware counters (`data/tables/perf-v2/`)

The per-operation counters of the atomic histogram are in ADR 0072, which was written on
`measured/v2`.

## Consequences

- A number quoted from the study is one of these or comes from the same tables; a number in an
  earlier result record that differs from these belongs to the earlier build.
- The earlier result records keep their reasoning; where their conclusions were later narrowed,
  ADR 0076, 0077 and 0078 say how.
- When a table changes, `make tables-check` fails, and this record must be updated with it.

## Status

Accepted
