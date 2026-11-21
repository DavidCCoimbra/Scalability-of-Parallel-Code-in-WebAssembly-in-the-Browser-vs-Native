# ADR 0030: Warm and cold fork-join calibration inside every run

Date: 2026-10-17

## Context

Each parallel region of a workload is a fork-join: the work is split into tasks that the pool's
worker threads run in parallel (fork), and the caller waits until all of them are done (join). The
fixed cost of starting and finishing that region is overhead that does not shrink with N.

Between measured iterations the checksum runs on one thread (ADR 0015), for milliseconds in the
filter. Meanwhile the Rayon workers have nothing to do and go to sleep, so every measured `run()`
starts by waking N threads: with a futex (the Linux wait/wake system call) natively, with emulated
`Atomics.wait`/`notify` in the browsers. That fixed cost grows with N, differs between
environments and is today counted as parallel work (finding R4 of the review of the benchmark code
once it was first complete). It is therefore a candidate explanation for part of the gap between
environments, and the design should be able to measure it.

Timing fork-joins back to back would not measure it: the workers would still be spinning (actively
waiting for new work) between them, which is not the state the measured iterations start from.

## Decision

- **Calibration inside every run.** Every run times empty `rayon::broadcast` calls (a fork-join
  that runs nothing on every worker) before the workload's warm-up, in the same process and pool,
  so no extra launches are needed. Two kinds:
  - **warm**: one untimed broadcast, then `calibration` broadcasts back to back;
  - **cold**: `calibration` broadcasts, each after a pause at least as long as the workload's
    checksum (timed once on the prepared workload) and never shorter than 1 ms, so the workers are
    asleep, as they are before a measured iteration.
- **What each measures.** The difference between cold and warm is the cost of waking the pool;
  warm alone is the fork-join cost with spinning workers.
- **CSV rows** with their own phases (ADR 0016): `calibration-pause` (one row, `ns` = the pause),
  `calibration-warm` and `calibration-cold` (`iter` = sample index). The checksum column repeats the
  run's checksum. The `ns` column means a different thing per phase, so the analysis always filters
  by phase first.
- **Option.** `calibration` is a run option (URL query and native flag), default 200 samples of
  each kind; 0 turns calibration off and is meant only for tests.
- **Use in the analysis.** The data is always collected. Whether it enters the analysis is decided
  later; if it does, it is descriptive (the wake-up cost per environment and N). Nothing is
  subtracted from the measured times or the speedup.

## Consequences

- Each run takes about 200 times the pause longer (0.2 s with the 1 ms floor), outside the timed
  region of the workload.
- In the browser a warm sample is close to the clock resolution (`performance.now()`, ADR 0018 and
  ADR 0020); the analysis uses the sum or the median over the 200 back-to-back samples, not single
  values.
- The pause floor of 1 ms is a design value; the pilot checks, per environment and N, that cold
  samples do not change with a longer pause.
- On wasm32 the pause is `std::thread::sleep` in the coordinating worker, which the atomics build
  of `std` implements with `memory.atomic.wait32` and a timeout; the browser job in CI (ADR 0024)
  runs it in every case.
- The calibration runs before the warm-up, so it also warms the thread pool itself, not the
  workload code.

## Status

Accepted; amends ADR 0015 (run layout) and ADR 0016 (phases in the CSV); amended by ADR 0076
(20 samples in the v2 campaigns)
