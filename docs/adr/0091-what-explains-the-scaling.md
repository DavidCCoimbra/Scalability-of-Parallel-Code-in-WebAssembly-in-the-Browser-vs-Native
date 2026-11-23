# ADR 0091: What the counters of the loop, the SIMD builds, the cutoff and the grain by threads show (questions 1 to 5 and 9)

Date: 2026-11-23

## Context

ADR 0088 listed the open questions behind the results and what would test each. ADR 0089
answered the two about the atomic counters. This record is about the rest: why the filter does
not scale to 8, why it scales better in Firefox, why it is slower in the browsers with one
thread, the dip at six and seven threads, the speedup above 8 in Firefox, and the time levels of
the contended cells.

The campaigns ran on `measured/v3` on 2026-11-22 and 23, all without a failed, missing or
excluded run, a checksum conflict or an order trend: `perf-v3` (720 runs), `perf-loop1-v3` and
`perf-loop8-v3` (180 each, ADR 0090), `simd-scalar-v3` (540), `simd-avx2-v3` (180), the seven
`cutoff-*-v3` (4080) and `grain-threads-v3` (1080). The tables are in `data/tables/*-v3`,
written by `make v3-results simd-results cutoff-results perf-results MEASURED=v3`.

Counters below are those of the loop alone (ADR 0090), per pixel, with 95 % bootstrap intervals.
The check of that method holds: the native local histogram at one thread gives 2.77
[2.76, 2.79] instructions per pixel against the 2.75 of its code.

## Decision

### Question 3: why the filter is slower in the browsers with one thread. Answered as far as counters go.

| Filter, one thread | Instructions per pixel | Cycles per pixel | Instructions per cycle |
|---|---|---|---|
| native | 4.10 | 1.07 | 3.84 |
| Chrome | 5.52 | 1.24 | 4.44 |
| Firefox | 5.41 | 1.45 | 3.73 |

Both engines run about a third more instructions per pixel than native code (1.34 and 1.32
times). Chrome runs them at a higher rate and ends 1.17 times the native cycles; Firefox runs
them at the native rate or below and ends 1.36 times. Those two ratios are the time ratios of
the main campaign. Why SpiderMonkey's instructions are slower is not known: its code could not
be read (ADR 0060).

The local histogram is the same in larger: 2.77 instructions per pixel natively against 7.0 in
Chrome and 6.8 in Firefox, at twice the native rate, for 1.23 and 1.31 times the cycles.

### Question 1: why the filter reaches an efficiency of 0.87. Supported, for about half of it.

From one to eight threads the loop runs the same instructions per pixel and more cycles:

| Filter, N = 8 over N = 1 | Instructions | Cycles | Last-level misses | L2 misses |
|---|---|---|---|---|
| native | 1.001 [0.998, 1.004] | 1.085 [1.076, 1.093] | 1.43 | 1.66 |
| Chrome | 1.003 [0.996, 1.012] | 1.049 [1.029, 1.071] | 1.47 | 1.29 |
| Firefox | 1.007 [1.002, 1.014] | 1.032 [1.012, 1.054] | 1.25 | 1.15 |

The prediction was the same instructions, more cache misses and about 1.15 times the cycles, the
inverse of the efficiency. The first two hold. The cycles rise by 8.5 % natively, not 15 %: the
cores' own work per pixel explains about half of the lost efficiency. The rest is time in which
a core is not running the loop at all (a counter of cycles does not see a halted core), which
fits the cost of handing out and collecting the tasks and was not measured here.

Two other sources agree that memory is what the eight threads run into:

- **The SIMD builds.** Efficiency at eight threads against what one thread reads per second:

  | Build and environment | MB/s with one thread | Efficiency at N = 8 |
  |---|---|---|
  | scalar, Firefox | 476 | 0.982 |
  | scalar, Chrome | 515 | 0.966 |
  | scalar, native | 760 | 0.982 |
  | baseline, Firefox | 2178 | 0.917 |
  | baseline, Chrome | 2533 | 0.865 |
  | baseline, native | 2969 | 0.869 |
  | AVX2, native | 4337 | 0.721 |

  The faster one thread goes through memory, the less eight threads gain, across three builds
  and three environments. At eight threads the baseline native filter reads 20.6 GB/s and
  writes as much.
- **The cutoff.** Natively the efficiency at eight threads is 0.940 at 4096x4096, where the
  input and the output together are 32 MB, and 0.866 at 8192x8192, where they are 128 MB. The
  browsers do not show this (Chrome 0.758 and 0.863, Firefox 0.885 and 0.928), and below
  2048x2048 the efficiency of every environment falls for another reason, the fixed cost of a
  parallel region (ADR 0065). The cutoff supports the reading natively and is not clear for the
  browsers.

### Question 2: why the filter scales better in Firefox. Supported.

By the rule of ADR 0090 the rise of the cycles per pixel from one to eight threads is smaller in
Firefox than natively: 1.032 [1.012, 1.054] against 1.085 [1.076, 1.093], the intervals apart.
Its last-level misses rise less too (1.25 against 1.43 times). And in the table of the SIMD
builds Firefox's baseline filter sits where its one-thread throughput puts it, between the
scalar builds and the native baseline. The tier campaign adds an intervention inside one engine:
with the baseline compiler the filter is slower per thread and scales slightly better in both
browsers (ADR 0089).

So Firefox does not scale better because of how it runs threads. Its filter does more work
between two accesses to memory, and eight such threads ask less of it. In time, Firefox stays
the slowest at every thread count (4.20 ms at N = 8 against 3.25 ms natively).

Chrome is the case this does not close: its cycles rise less than the native ones (1.049) and
its efficiency is the native one (0.865 against 0.869). By the same accounting Chrome loses more
outside the loop, which fits the larger cost of its parallel region (ADR 0076), not measured
here.

### Question 5: the speedup above 8 of the local histogram in Firefox. Supported.

| Local histogram, N = 8 over N = 1 | Cycles, k = 16 | Cycles, k = 256 | L2 misses, k = 16 | L2 misses, k = 256 |
|---|---|---|---|---|
| native | 1.033 [1.017, 1.051] | 1.010 [0.995, 1.025] | 0.94 [0.90, 0.97] | 0.95 [0.90, 0.99] |
| Chrome | 1.007 [0.998, 1.016] | 1.006 [0.975, 1.034] | 0.96 [0.90, 1.01] | 0.93 [0.85, 1.01] |
| Firefox | 0.983 [0.972, 0.994] | 0.947 [0.881, 0.991] | 0.72 [0.62, 0.82] | 0.74 [0.64, 0.84] |

In Firefox a pixel costs fewer cycles with eight threads than with one, 5 % fewer at k = 256,
which is the size of the excess over 8 (8.48). Its L2 misses per pixel fall by a quarter, and
those of native code and Chrome by a twentieth. The prediction held: the one-thread run pays
for cache misses that the eight-thread run does not. The speedup above 8 is also there against
the sequential reference (8.09 and 8.12), so it is not a slow pool of one thread. What
SpiderMonkey's one-thread loop does to miss more is not known.

This is also what puts Firefox's RQ2 effect under 1 at k = 16 and 256 (question 8): the
denominator of the effect scales more than 8 while its atomic times are the native ones.

### Question 4: the dip at six and seven threads. Not supported.

The local histogram at k = 16 with Rayon's adaptive split and with fixed grains:

| Native | N = 6 | N = 7 | N = 8 |
|---|---|---|---|
| adaptive: time, efficiency | 4.98 ms, 0.959 | 4.30 ms, 0.952 | 3.63 ms, 0.987 |
| 256 KB: time, efficiency | 4.99 ms, 0.997 | 4.34 ms, 0.981 | 3.68 ms, 1.013 |
| 1024 KB: time, efficiency | 5.09 ms, 0.975 | 4.59 ms, 0.927 | 3.70 ms, 1.005 |

A fixed grain does not make six or seven threads faster: the times with 256 KB are those of the
adaptive split, and with 1024 KB they are worse. The efficiencies with a fixed grain look better
only because the one-thread run with a fixed grain is slower (29.8 against 28.7 ms), which
raises every speedup computed from it. In Chrome and Firefox the times do not improve either.
The hypothesis that Rayon's splitting in powers of two causes the dip is not supported. The dip
stays unexplained; placement of six or seven threads on eight cores was not tested.

### Question 9: the time levels of the contended cells. Supported.

In `perf-v3` the atomic histogram at k = 1 with eight threads spreads over 25 to 32 % between
its fastest and slowest run, and a run's time follows its own count of contended line transfers
(Spearman's rho with the lines taken for writing from another core: +0.94 in Chrome, +0.63
natively, +0.56 in Firefox; in Chrome also +0.92 with the compare-and-swap attempts). At
k = 256 the runs are within 1 % and there is nothing to follow. The levels are states of
contention that differ from run to run; what sets the state of a run is not known.

### What the main campaign adds

- **The pool of one thread** costs between -7 % and +5 % against the sequential reference
  (`campaign-v3-sequential.csv`): the relative speedup is not inflated by its baseline.
- **Placement at one thread** (`campaign-v3-core-split.csv`): the busiest core of a run is CPU
  12 or 14. For the native filter it is CPU 12, the degraded core (ADR 0085), in 9 of its 30
  runs, with a median 1.0003 times that of the configuration. The busiest core has 70 to 80 %
  of a native run's busy time and 47 to 64 % of a browser run's, the rest being the main thread
  and, in a browser, its other threads: the split says where most of the work was, not that one
  core did it all.

## Consequences

- Of the nine questions of ADR 0088: 6 answered and 7 answered for the sequence (ADR 0089); 3
  answered as far as counters go; 1, 2, 5 and 9 supported; 8 follows from 5; 4 not supported
  and open.
- What stays open, to be declared: why SpiderMonkey's code is slower per instruction and misses
  more with one thread; what Chrome loses outside the loop; the mechanism at k = 256; the dip at
  six and seven threads; what sets a run's state of contention.
- For the paper: the RQ1 finding (Firefox scales better) is read as a slower loop asking less
  of the memory, supported by three sources and by an intervention inside one engine. It is not
  evidence that a browser runs threads better.

## Status

Accepted
