# ADR 0002: Turbo boost off and governor `performance`

Date: 2026-10-17

## Context

Speedup is T1/TN: the time with one thread divided by the time with N threads. With turbo boost
on, a single busy core runs near 6 GHz, while with all cores busy the CPU runs at a lower
frequency. T1 is then measured at a higher clock than TN, which deflates the speedup for a
reason that has nothing to do with parallelism. The CPU frequency governor (the Linux policy
that picks the clock frequency) can add the same kind of distortion if it changes frequency with
load.

## Decision

Disable turbo boost and set the CPU frequency governor to `performance` (always the highest
allowed frequency, so the clock does not depend on load) for every measurement.

## Consequences

- Speedup curves reflect parallel scaling, not frequency scaling.
- Absolute times are slower than with a production setting. An optional subset with turbo on
  was planned to show the distortion; it was not run, because one core of the PC is degraded at
  high frequencies (ADR 0052).
- The paper reports the base frequency, the governor and how turbo was disabled.
- Every result records the governor and the turbo state, and strict validation rejects runs that
  do not match this ADR (ADR 0023).

## Status

Accepted
