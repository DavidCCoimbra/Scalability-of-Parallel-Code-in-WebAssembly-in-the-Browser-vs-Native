# ADR 0015: Shared measurement loop with an injected clock

Date: 2026-10-17

## Context

Native and WASM must time exactly the same work in the same way, otherwise a difference between
them could come from the measurement code. Only the computation may be inside the timed
interval. The browser has a different clock from native (`performance.now()` instead of the
operating system's monotonic clock). The raw per-iteration data must be kept, because the unit
of analysis is the run, summarised from its iterations (ADR 0005).

## Decision

- One function, `measure(workload, clock, plan)`, used by both the native runner and the WASM
  entry. `MeasurementPlan` holds W warm-up and K measured iterations (K at least 1); both are set
  from pilot data.
- Each iteration: `prepare()` (untimed), then the clock is read just before and just after
  `run()`, then `checksum()` (untimed). Warm-up iterations follow the same steps, including
  `prepare`.
- The clock is injected as a `Clock` trait, so the loop is the same code on both sides:
  `NativeClock` (monotonic `Instant`) natively, a `performance.now()` clock in the WASM entry
  (ADR 0018).
- The Rayon thread pool is set up by the caller before calling `measure`, so pool creation is
  never timed. As first written: natively `ThreadPool::install`, in WASM the global pool of
  wasm-bindgen-rayon. Since ADR 0018 both sides use a global pool (see Status).
- The checksum of every iteration must equal the first one; otherwise `measure` returns
  `InconsistentChecksum`. Warm-up and measured times are both returned, raw, in nanoseconds.

## Consequences

- Inside the timed interval: only `run()` and two clock reads. Outside: allocation (in the
  constructors), input generation, counter reset, checksums, pool creation and I/O.
- A workload that forgets to reset its state (for example, a missing `prepare`) is caught at run
  time by the checksum check.
- Warm-up times are kept so that W can be chosen from data (ADR 0043).

## Status

Accepted; amended by ADR 0018 and ADR 0032 (global pool, no `install`) and ADR 0030
(fork-join calibration before the warm-up)
