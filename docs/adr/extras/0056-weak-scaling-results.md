# ADR 0056: Weak scaling results

Date: 2026-11-08

## Context

The weak scaling campaign of ADR 0055 ran 1080 runs from the commit tagged `measured/weak`: the
filter and the local histogram at k = 1, on 8192 x 1024N pixels, N in {1, 2, 4, 6, 7, 8}, 30
runs per configuration.

Data, in the working repository: `data/raw/weak`, `data/tables/weak/weak-quality.md`,
`data/tables/weak/weak-scaling.csv` (from `analysis.v0 --weak`, which reports T1 / TN as
`weak_efficiency` and leaves out the speedup / N columns, which have no meaning for weak
scaling), `data/tables/weak/weak-iteration-drift.csv` (from `analysis.iteration_drift`) and the
figure `paper/figures/weak-absolute.pdf`. The campaign was later re-run on the `measured/v2`
build (ADR 0069), whose data are in `data/raw/weak-v2`; the numbers below are those of
`measured/weak`.

## Decision

Record the following results (geometric means, 95 % bootstrap intervals).

### Data quality

No failed run, no checksum conflict, no run above the foreign CPU threshold, no configuration
under 100 times the clock resolution, and no configuration that trends with the execution
order.

The warm-up concern of ADR 0055 is answered for drift: in every configuration the median of the
first three measured iterations is within 1 % of the median of the last three (0.994 to 1.010,
`weak-iteration-drift.csv`). This check cannot see a slower level that lasts through all ten
measured iterations. Two further checks cover that: the N = 8 times, whose W covers the same
wall time as in the main campaign, repeat that campaign's within 0.3 %; and the browser /
native ratios at N = 1 are within 1.5 % of the main campaign's (filter: Chrome 1.17 against
1.18, Firefox 1.36 against 1.35).

### Weak-scaling efficiency at N = 8

| Workload | native | Chrome | Firefox |
|---|---|---|---|
| filter | 0.857 [0.854, 0.860] | 0.850 [0.846, 0.855] | 0.921 [0.916, 0.927] |
| local histogram | 1.001 [0.993, 1.017] | 0.989 [0.985, 0.992] | 0.994 [0.993, 0.996] |

The filter loses efficiency progressively from N = 2 (native 0.93, 0.89 at N = 4); the
histogram stays within 3 % of 1 at every N.

### Agreement with strong scaling

The weak efficiencies at N = 8 are within about 2 points of the main campaign's strong
efficiencies at N = 8 (filter: 0.871, 0.871, 0.928; local k = 1: 0.994, 0.994, 0.983, for
native, Chrome and Firefox). The N = 8 times also repeat the main campaign's, as expected since
the input is the same (filter native 3.26 ms in both).

So the filter's sub-linear strong speedup is not a cost of splitting a fixed input into smaller
pieces. Rather, one thread working on 1/N of the image is slower when N threads run at once:
its time grows by 17 to 18 % natively and in Chrome, and by 9 % in Firefox. Candidate causes,
none of them measured:

- a resource shared by the cores (memory bandwidth or the L3 cache);
- Rayon's fork-join and scheduling cost with more threads. (Fork-join: the parallel region
  splits the work across the threads and waits for all of them to finish.) This campaign's own
  calibration (designed in ADR 0030) puts one warm fork-join at N = 8 at 47 us natively and
  163 us in Chrome (another campaign and statistic than the 7.5 and 110 us of ADR 0064), under 5 %
  of iterations of 3 to 4 ms, too little to explain the 14 % loss alone;
- per-core power or frequency limits with several cores busy (turbo is off, but the frequency
  is not logged).

First-touch page faults are unlikely: the buffers are allocated outside the timed region and
reused across iterations.

### The browser gap does not grow with N

Browser time over native time stays nearly constant across N (ratios of geometric means; no
intervals computed on the ratio):

- filter: Chrome 1.16 to 1.20, Firefox 1.27 to 1.36 (falling with N);
- local histogram: Chrome 0.96 to 0.99, Firefox 1.006 to 1.016.

With fixed work per thread, no per-thread browser cost grows with N beyond these few percent.
Firefox's better filter efficiency comes with a slower single thread (1.36 times native at
N = 1). This is consistent with a slower loop that asks less of the shared resource
(hypothesis).

## Consequences

- The paper reports weak scaling as an exploratory result. It supports the RQ1 reading that the
  browsers' scaling matches native for these workloads, and shows that the filter's loss is not
  a cost of splitting the input. The size of that loss differs between environments (Firefox
  loses less), and its cause is left open.
- Separating the candidate causes would need hardware counters (uncore bandwidth) and a
  frequency log; this is not planned.

## Status

Accepted
