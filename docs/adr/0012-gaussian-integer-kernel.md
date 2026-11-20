# ADR 0012: Gaussian 3x3 filter with an integer kernel, row-parallel

Date: 2026-10-17

## Context

The Gaussian 3x3 filter is the embarrassingly parallel baseline: every output pixel depends only
on the input, so threads never need to coordinate and any loss of speedup comes from the
environment, not from synchronisation. Its output must be bit-identical on native and WASM and
for every thread count, so its checksum can be compared. The measured region must contain only
the filter work.

## Decision

- Kernel `[1 2 1; 2 4 2; 1 2 1] / 16` in `u32` integer arithmetic with rounding
  (`(sum + 8) >> 4`), no floating point.
- Borders use clamp: pixels outside the image take the value of the nearest edge pixel.
- Parallelism: Rayon's `par_chunks_mut` over output rows. Each task writes only its own row and
  reads the shared, immutable source, so no synchronisation is needed.
- The hot loop over interior pixels slides 3-pixel windows over the three source rows with no
  clamping or bounds checks, so the compiler can vectorise it; only the two border columns use
  the clamped path.
- Workloads implement `Workload { run, checksum }`: `run` is the timed work; `checksum` (FNV-1a of
  the output, a simple hash that depends on the position of every byte) is computed outside the
  timed region.
- The output buffer is allocated in the constructor, outside the timed region (allocation in
  WASM takes a global lock, ADR 0008).

## Consequences

- Integer arithmetic gives the same result on every target and thread count. Floating point
  could differ with SIMD or fused multiply-add operations.
- Rayon splits the rows into tasks, so the number of rows must be well above the thread count
  (the image size is set in the pilot, ADR 0041).
- To verify in the pilot: whether the interior loop vectorises on both targets (SSE2 and
  `simd128`, ADR 0004), and an image width that is a multiple of 64 so that row boundaries do
  not share cache lines between tasks.
- Every later workload follows the same `Workload` interface, which the measurement loop
  (ADR 0015) times.
- ADR 0017 moved the interior loop to `u16` arithmetic in a separate function with a shared
  kernel table, so that its vectorisation can be checked on the built binaries; results are
  unchanged.

## Status

Accepted; amended by ADR 0017 (interior loop in `u16`, shared kernel table)
