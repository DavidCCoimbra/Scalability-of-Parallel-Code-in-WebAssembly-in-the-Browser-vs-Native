# ADR 0036: Analysis v0: one value per run, relative speedup with bootstrap intervals

Date: 2026-10-18

## Context

The pilots need speedup and efficiency per environment from campaign data, before the final
analysis exists. Three earlier decisions constrain how: the run is the unit of analysis (ADR
0005), speedup is T1/TN within each environment (ADR 0003), and the per-run summary is chosen in
the pilot (ADR 0005, ADR 0026). The statistical choices for the final analysis belong to the
analysis plan (ADR 0037), which did not exist yet. A first analysis was needed that follows the
fixed decisions and leaves the open ones as parameters.

## Decision

- **Loading.** `python3 -m analysis.v0 <campaign dir>` loads the runs with `harness.collect`
  (ADR 0033), so failed runs are excluded and counted. A checksum conflict stops it before any
  table is written, because the data is then wrong, not just incomplete. Planned runs without
  files are only reported, so a partial pilot campaign can still be looked at.
- **One value per run.** Only `measured` rows are used; warm-up and calibration rows are
  dropped. Each run becomes one value: the median (or the mean, with `--summary mean`) of its
  measured iterations. This avoids pseudo-replication: iterations of one process are not
  independent observations.
- **Speedup and efficiency.** For each configuration (environment, workload, input, k, N) the
  central value of its run values is taken (the median, or the mean with `--center mean`).
  Speedup is center(T1) / center(TN) of the same environment, workload and input; efficiency is
  speedup / N.
- **Intervals.** The 95 % interval is a percentile bootstrap (resampling with replacement to
  estimate how much the statistic would vary) that resamples runs, not iterations. The N = 1
  group and the N group are resampled independently, because they are different processes and
  so not paired. It uses 10 000 resamples with a fixed seed, so the same data always gives the
  same interval; the bounds are the order statistics nearest to the 2.5 % and 97.5 % positions.
  The table shows the run count of both groups (`runs`, `baseline_runs`), and `--output x.csv`
  also writes `x.json` with the options, the seed and the commit.
- **No dependencies.** Python standard library only, like the harness: nothing to install on
  the PC.
- **Provisional defaults.** The defaults (median per run, median across runs, percentile
  bootstrap) are provisional. The analysis plan fixes them before the full campaign; the code
  keeps them as parameters, so that the plan only changes defaults.

## Consequences

- One command turns a campaign directory into a scaling table for the pilots.
- With few runs per configuration the bootstrap interval is too narrow to trust (with 2 runs it
  has at most 3 distinct values); the number of runs comes from the run count pilot (ADR 0047).
- The RQ2 contrasts, the tests and the multiple-comparison handling come after the plan
  (ADR 0038).

## Status

Accepted; amended by ADR 0037 (defaults fixed by the analysis plan)
