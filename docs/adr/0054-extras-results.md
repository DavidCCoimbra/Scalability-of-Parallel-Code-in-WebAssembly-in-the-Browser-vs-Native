# ADR 0054: Results of the extras campaign

Date: 2026-11-08

## Context

The extras campaign (ADR 0053, tag `measured/extras`, commit 4c56012) ran 5400 runs from
2026-11-07 21:59 to 2026-11-08 14:04. The data check (ADR 0051) found:

- no failures, no checksum conflicts, no run failing strict validation and no run above the
  foreign CPU threshold;
- one configuration trending with the execution order (native `hist-atomic` k = 1, N = 2,
  rho = -0.51), which is at the level expected by chance.

The tables are `data/tables/extras/extras-quality.md`, `data/tables/extras/extras-scaling.csv`
and `data/tables/extras/extras-contrasts.csv`, in the working repository. This campaign was
later re-run on the `measured/v2` build (ADR 0069), whose data are in `data/raw/extras-v2`; the
numbers below are those of `measured/extras`.

All numbers below are exploratory (ADR 0052): geometric means over 30 runs with 95 % bootstrap
intervals. The speedup ratio browser / native compares relative speedups (T1 / TN within each
environment); "x times native" compares absolute times.

## Decision

The results are read as follows and reported in the paper.

### Reproducibility of the main campaign

The controls use the main campaign's W (71 and 15 for the local histogram, 5 for the shared
one). The RQ2 interaction exp(delta r) at N = 8 is the browser's atomic / local time ratio
divided by native's (ADR 0026). It repeats the main campaign's value, with overlapping 95 %
intervals:

| Browser, k | extras campaign | main campaign |
|---|---|---|
| Chrome k = 1 | 2.32 [2.19, 2.45] | 2.26 |
| Chrome k = 256 | 0.41 [0.41, 0.41] | 0.41 |
| Firefox k = 1 | 0.98 [0.94, 1.03] | 0.97 |
| Firefox k = 256 | 0.61 [0.61, 0.62] | 0.62 |

### Private atomics

One table of padded atomics per thread scales like the local control everywhere: speedup 7.9 to
8.0 at N = 8, speedup ratio browser / native 0.99. With no other thread touching the counters,
its absolute cost is the cost of the atomic instruction without contention:

- Chrome is 1.79 to 1.80 times native at k = 1 and 1.13 to 1.15 at k = 256, at every N
  including N = 1;
- Firefox is 0.97 to 0.98 times native at k = 1 and 1.00 at k = 256.

So Chrome's single-thread penalty in the shared histogram is the uncontended atomic add itself,
and it grows when consecutive adds hit the same counter (k = 1). A hypothesis, not measured
here: the different lowering of ADR 0049 (for example a load plus a compare-and-swap loop),
whose dependency chain would be longer on one address. Contention adds the rest: at k = 1,
N = 8, Chrome's shared histogram is 2.26 times native, against 1.80 for the private one.

### False sharing

- At k = 1, packed and padded counters are equal, because there is one hot counter either way.
  This is a sanity check.
- At k = 256, N = 8, packing eight counters per line makes the shared histogram 1.15 times
  slower natively, 1.55 times in Firefox and 3.35 times in Chrome.
- The browsers' advantage over native at k = 256 disappears: Chrome becomes 1.47 times native
  (speedup 0.59 against native's 0.77), and Firefox equals native.

Chrome's advantage under spread contention therefore depends on each counter having its own
cache line.

### Parallel sort

- The stable `par_sort` scales the same in every environment (speedup 7.8 at N = 8, ratio
  browser / native 1.00) and costs a constant 1.11 (Chrome) and 1.06 (Firefox) times native.
- The in-place `par_sort_unstable` scales less (6.2 to 6.3, because its first partition is
  sequential) but again equally in every environment (ratio 0.98 and 0.99), at 1.34 to 1.36
  times native.
- The allocation in the stable sort does not hurt WASM, so the hypothesis of ADR 0052, that the
  sort would expose the WASM allocator and its global lock, is not supported. A likely reason,
  not measured here: the buffer is allocated once per sort, so the allocator's lock is barely
  contended.

### Superlinear Firefox local histogram at k = 256

Firefox's `hist-local` speedup at k = 256, N = 8 is 8.34 (8.27 by medians: T1 34.2 ms, T8
4.14 ms), against 7.94 natively and 7.86 in Chrome; the main campaign gave the same (8.33). A
few slow T1 runs (up to 44 ms) raise the geometric mean, but the ratio of medians is
superlinear too. It is reproducible and unexplained. It points to a slower T1 rather than a
faster T8 (Firefox is 1.27 times native at N = 1 and 1.21 at N = 8). A slower T1 would leave the
RQ2 value, which is computed at N = 8 only, untouched. (Corrected after review: an earlier
version said it lowered that value by about 4 %.)

## Consequences

- RQ1's finding, that WASM threads cost a constant factor and not scalability, holds for two
  more synchronization-free workloads, one of them with allocation.
- RQ2's Chrome gap splits into a per-operation part (the atomic add without contention) and a
  contention part; both remain to be confirmed by inspecting V8's generated code (ADR 0052).
- Weak scaling and SIMD remain to be run (ADR 0055 and ADR 0057).

## Status

Accepted
