# ADR 0067: Results of the grain sweep (U-curve)

Date: 2026-11-09

## Context

ADR 0066 designed the grain sweep. A fixed task size (`grain`: rows for the filter, KB for
hist-local k256) is swept over powers of two, plus Rayon's adaptive split as a reference, at
1024^2 (K = 64 passes) and 8192^2 (K = 1), N = 8, native, Chrome and Firefox, 30 runs per
configuration. The question is whether there is a best task size, and whether it is coarser in
the browsers, whose fork-join costs more. Both campaigns ran on 2026-11-09 on build `841b788a`
(tag `measured/grain`), and this ADR records what they found.

The tables named below are those of this build, kept in `data/earlier/v1/tables/grain`. The
sweeps were run again on the v2 build (ADR 0069) and on v3 (`data/tables/grain-v3/`).

Data quality (`data/tables/grain/grain-*-quality.md`): 4050 runs (1620 and 2430), none missing
or failed, no checksum conflict, none failing strict validation or above the foreign CPU
threshold, none under 100 times the clock resolution, no configuration trending with the
execution order.

## Decision

Record the following as the grain results. They are exploratory (ADR 0052): point estimates
with bootstrap intervals, no test. Times are the geometric mean of the run medians of the time
per pass (`data/tables/grain/grain-points.csv`, `grain-best.csv`,
`paper/figures/grain-ucurve.pdf`). "Relative" is the time divided by the best grain's. The flat
region is the run of neighbouring grains around the best whose 95 % intervals overlap the
best's.

### 1. The U appears at 8192^2; at 1024^2 the curve is an L

At 8192^2 both workloads have a fine and a coarse side (relative times):

| Workload | Environment | Best grain | Flat region | Finest grain | Coarsest grain |
|---|---|---|---|---|---|
| filter | native | 4 rows | 2 to 4 | 1.00 | 1.09 (1024 rows) |
| filter | Chrome | 4 rows | 2 to 4 | 1.02 | 1.13 |
| filter | Firefox | 4 rows | 4 | 1.03 | 1.06 |
| hist-local | native | 256 KB | 128 to 256 | 2.09 (1 KB) | 1.02 (8192 KB) |
| hist-local | Chrome | 128 KB | 64 to 128 | 2.11 | 1.09 |
| hist-local | Firefox | 128 KB | 64 to 128 | 2.97 | 1.15 |

At 1024^2 the time falls monotonically with the grain up to the largest swept grain (side / N,
one task per thread: 128 rows, 128 KB). That grain is the best everywhere except Chrome's filter
(best 32 rows, with 128 rows at 1.003 times it). The finest grain costs 1.20 to 1.24 times the
best for the filter and 1.84 to 2.46 times for hist-local. The coarse side would need fewer
tasks than threads and was not swept.

### 2. The fine side: the cost per task is below a microsecond

The extra time of the finest grain over the best, times N, divided by the extra number of
tasks, estimates the cost of one more task (`task_cost_ns`):

| Workload, side | Native | Chrome | Firefox |
|---|---|---|---|
| filter, 1024 | 94 (90 to 97) ns | 147 (140 to 155) | 188 (175 to 199) |
| filter, 8192 | 17 (1 to 32) ns | 84 (56 to 111) | 141 (108 to 173) |
| hist-local, 1024 | 503 (498 to 509) ns | 655 (646 to 664) | 1179 (1170 to 1189) |
| hist-local, 8192 | 463 (461 to 464) ns | 579 (574 to 584) | 996 (990 to 1002) |

The interval (`task_cost_low_ns`, `task_cost_high_ns`) combines the two points' 95 % intervals
at their extremes, a rough bound. The best grain is the minimum of noisy means, so the estimate
leans high.

For the filter this is the scheduling cost of a Rayon task inside a running region: a split, a
push and a pop on a work-stealing deque, sometimes a steal. For hist-local it adds a 2 KB
partial histogram per task and its merge. Per task the browsers pay 1.3 to 1.6 (Chrome) and 2.0
to 2.3 (Firefox) times native, except the filter at 8192^2, where native's 17 ns is close to
zero (its finest grain is within 1 % of the best). The region's fork-join F, by contrast, costs
6 to 10 times native's (the calibration of these campaigns, values in section 3). F is 20 to more than 1000 times the cost of a task.

### 3. The 100:1 rule: right with the cost per task, not with F

`grain_100f` (`grain-best.csv`) is the grain whose sequential work is 100 F, with F the region's
fork-join cost at N = 8 (native 10.6 us, Chrome 110, Firefox 60). For hist-local at 8192^2 it is
2.5 MB natively, 21 MB in Chrome and 12 MB in Firefox, against a measured best of 128 to
256 KB. The image is 64 MB, so Chrome's 100 F grain would give three tasks to eight threads. F
is paid once per region, not per task; ADR 0065 applies the rule to the region, where it
belongs.

`grain_100task` applies the same rule to the cost of one task (section 2): the grain whose work
is 100 times that cost. At 8192^2 it lands on or next to the measured flat region in every case
where the cost is resolved:

| Workload | Environment | 100 x task cost | Measured best (flat) |
|---|---|---|---|
| filter | Chrome | 2.2 rows | 4 (2 to 4) |
| filter | Firefox | 3.5 rows | 4 (4) |
| hist-local | native | 111 KB | 256 (128 to 256) |
| hist-local | Chrome | 112 KB | 128 (64 to 128) |
| hist-local | Firefox | 197 KB | 128 (64 to 128) |

At 1024^2 it gives 19 to 20 rows and 82 to 137 KB, below or at the largest swept grain, which
is consistent with the L-shaped curves there. The cost per task is read off the same sweep, so
this is a consistency check of the 100:1 rule, not an independent prediction. The unit of work
comes from the adaptive split at N = 8 times N (the grain campaigns do not measure N = 1), so it
includes the parallel overheads. A grain 100 times the per-task cost is where the fine side of
the U flattens.

### 4. The coarse side: the browsers lose more from few tasks

At 8192^2, hist-local with 8192 KB tasks (8 tasks, one per thread) is 1.02 times the best
natively, 1.09 in Chrome and 1.15 in Firefox. Natively every grain from 128 KB to 4096 KB is
within 0.5 % of the best. With one task per thread, the region lasts as long as its slowest
thread, and nothing can be stolen. The browsers' workers start and run less evenly (their late
wake-up is the fork-join cost that the calibration of ADR 0030 measures), so they need more, smaller tasks for work stealing
to even out the load. The best grain is therefore not coarser in the browsers, as ADR 0066 asked
(the point estimates are 128 KB against 256 KB natively, but the flat regions overlap, so "finer"
is not shown), and the browsers' penalty is on the coarse side.

### 5. The adaptive split is near the best at 8192^2, not at 1024^2

The adaptive split (the code of every earlier campaign) is within 1 % of the best grain at
8192^2 everywhere (0.995 to 1.010). At 1024^2 it is 1.04 (Chrome and native hist-local) to 1.18
(native filter) times the best: on a 50 to 120 us region, Rayon's adaptive splitting creates
more tasks than the one per thread that wins there. This is consistent with ADR 0065: the cutoff
campaign's small sizes include this splitting cost, the same in all three environments' code.

### 6. The filter's step between 8 and 16 rows at 8192^2

From 8 to 16 rows per task the filter's time rises by 5 to 11 % in all three environments
(native 1.00 to 1.05, Chrome 1.01 to 1.12, Firefox 1.01 to 1.03) and stays there up to 1024
rows. Load imbalance does not explain it (16 rows is 512 tasks of about 50 us for 8 threads).
The step appears natively too, so it belongs to the machine or the code, not to the browsers. A
16-row block of the 8192-wide grey image is 128 KB of output; a cache or prefetcher effect is a
hypothesis, not verified.

## Consequences

- **The answer.** The U exists at a large size. Its minimum is a few rows (filter) or 64 to
  256 KB (hist-local) in all three environments, and the browsers do not need a coarser grain.
  The 100:1 rule finds the minimum when it is applied to the cost of one task rather than to the
  region's fork-join. What the browsers need is fewer parallel regions (ADR 0065), not fewer
  tasks per region.
- **Advice for web developers: two thresholds.** Per region, fork only above about 0.5 ms of
  sequential work at 8 threads (ADR 0065). Per task, keep tasks at least about a hundred times the measured
  cost per task (1.7 to 118 us here, 46 to 118 us for the local histogram) and give each thread several tasks, more so in the
  browser. Rayon's adaptive split already does this for large regions.
- **The earlier campaigns are not a grain artefact.** Their adaptive code is close to the best
  grain at 8192^2 (within 1 %), so their RQ1 and RQ2 numbers do not come from a badly chosen
  grain.
- **Reproduction.** `make grain-results` regenerates every number in this ADR from this build's
  `data/raw/grain-*`. Those runs are not in this repository; the tables are.

## Status

Accepted
