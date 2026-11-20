# ADR 0069: The v2 build: measurement corrections, refactor and new settings

Date: 2026-11-09

## Context

On 2026-11-09 the measured path was reviewed again, after reading the textbook (McCool, Robison
and Reinders 2012) and the cited papers in full. The review found asymmetries that the benchmark
code itself had introduced:

- **A bounds check only in the RQ2 numerator.** RQ2 compares `T_atomic / T_local` (ADR 0026).
  The shared-counter histograms (atomic, packed, private) indexed a `Box<[T]>`, whose length the
  compiler does not know, so every pixel paid a bounds check (a `cmp` and a `jbe`). The local
  control indexes a `[u64; 256]` and paid nothing. The ratio therefore included code that only
  the numerator runs, and that the browser engines may compile differently from LLVM.
- **Final work timed in some variants but not in others.** Local's reduce was inside the timed
  region. Private's merge of the per-thread tables and the read-back of the shared counters were
  outside it.
- **Settings that the record could not state.** The CSV could not record what the next
  campaigns needed: the passes per sample, the grain, the memory size and where the buffers lie.

The decision was to re-run every reported campaign on one new build, so that the final results
come from one tagged commit (ADR 0062). Optimizations are kept out of that build: only
corrections and refactors go in.

## Decision

**Build `measured/v2`.** It contains the following.

1. **Measurement corrections:**
   - **Fixed-size counter tables.** `Box<[C; 256]>` removes the per-pixel bounds check in
     atomic, packed and private. The source is still a plain `for_each` over `increment`;
     without the check, LLVM unrolls it by 8 by itself. Native disassembly of the atomic loop,
     before: `movzbl; cmp; jbe <panic>; shl $7; lock incq` per pixel; after:
     `movzbl; shl $7; lock incq (%rsi,%r9,1)` eight times per iteration, with no call. Packed
     uses `lock incq (%rsi,%r10,8)`. In WASM the histogram functions go from 4 to 1
     `panic_bounds_check` calls and keep `i64.atomic.rmw.add`. Private keeps one table-index
     check per chunk, not per pixel, and its `prepare` sizes the tables to exactly N + 1.
   - **Every histogram's `run` ends with the final histogram.** For local that is the reduce,
     for private the merge of N + 1 tables, and for atomic and packed the read-back of 256
     counters. All are now timed, so every variant times the same steps; `checksum()` only
     hashes the result.
   - **A streaming FNV-1a checksum**, over the same bytes in the same order. It no longer copies
     the output into a `Vec`, which evicted the L3 cache and set the length of the pause between
     iterations.
   - **`black_box` on the checksum that `pause_for` discards**. `black_box` hides a
     value from the optimizer, so the checksum cannot be optimized away.
2. **Refactor.** One generic `CounterTable`; one pool entry for both hosts; `Platform` (clock,
   memory, pause); phases with hooks in `measure.rs`; one grain helper; strong config types;
   test support; simpler JS; and capabilities per workload. Every iteration is still called
   from outside the pool, natively from the main thread and in WASM from the coordinator
   worker, as a web application calls a Rayon pool.
3. **New settings and records:**
   - **Memory size before the warm-up and after the last iteration.** A WASM run whose linear
     memory grows during the measured phase fails.
   - **Buffer addresses mod 4096 and mod 64** for the filter's input and output and the
     histogram's input, to test 4K aliasing (two addresses that agree in their low 12 bits,
     which the CPU can mistake for a dependency between a load and a store).
   - **`pitch`**, the filter's row stride, by default the width.
   - **`palette`**: `spread` (the default and the earlier values) or `consecutive` (values 0 to
     k-1).
   - **A second fork-join probe**, an empty `par_iter` region, next to the empty broadcast. The
     broadcast works as a barrier (every thread must run it); the `par_iter` region is ordinary
     optional parallelism.
   - **CSV schema 2** (schema, passes, grain, probe and the fields above). The readers upgrade
     schema-1 data.
   - **A blocking data check** for configurations that mix width, height, pitch, palette or
     passes (`analysis/quality/variants.py`).
4. **Left out of v2, as exploratory variants only:**
   - **Running the measured loop inside `pool.install`.** It would hide the per-iteration
     injection of work into the pool that a web application pays.
   - **A Rayon spin before sleeping.** On wasm32 with atomics, `std::thread::yield_now` is a
     no-op (the pinned std's `sys/thread`), so Rayon's 32 yield rounds pass at once. A native
     diagnostic with a no-op `sched_yield` (6 runs each) raised the warm broadcast from 4.2 to
     16.6 us and T8 of the filter by about 1 %.

**Codegen** (`scripts/codegen_diff.sh origin/main`):

- **`blur_interior`:** identical in the four native variants and in the WASM package.
- **The SIMD checker:** `check_simd.py` still finds 65 packed SIMD instructions on x86-64 and 43
  on wasm32.
- **What changed:** 17 hot functions in each native variant. These are the histograms' `run`,
  `prepare` and `checksum`, their Rayon helpers, the filter's and local's `run` (whose helper
  type gains the grain wrapper), and the checksums.
- **What is identical:** the sort kernels, `ParallelSort::run` and the filter's `prepare`.

**Checksums.** Every existing golden checksum is unchanged at 1, 3 and 8 threads and 1, 2 and 5
passes. The consecutive palette has new golden checksums, checked against an independent Python
computation. In the browser check, 114 of 114 Chrome and Firefox runs match the native
fingerprints and checksums.

**Native A/B, v1 (main) against v2.** 8192^2, N = 8 unless stated, 5 interleaved runs each,
median:

| Configuration | v2 / v1 |
|---|---|
| filter N = 1 | 1.000 |
| filter | 1.003 |
| hist-local k = 1 | 1.002 |
| hist-local k = 256 | 0.997 |
| hist-atomic k = 1 | 0.954 |
| hist-atomic k = 256 | 0.971 |
| private k = 1 | 0.974 (merge now timed) |
| packed k = 256 | 1.004 |

Nothing got slower. The atomic variants got faster because they lost the bounds check.

## Consequences

- **Re-runs.** The main, grain, cutoff and extras campaigns are re-run on `measured/v2`, and the
  paper's numbers come from them. No comparison mixes v1 and v2 runs. The v1 campaigns stay
  valid for their own tags.
- **RQ2 moves.** It moves slightly against v1: the numerator lost a bounds check, and private,
  atomic and packed now time their final read or merge. The v1 RQ2 numbers measured that
  asymmetry too.
- **Memory check.** It covers the end of the warm-up to the last iteration, including the
  untimed `prepare` and `checksum`. With `warmup=0` a first allocation would fail a WASM run;
  only the old pilot-warmup specs (in the working repository) use 0.
- **Settings outside `Configuration`.** Campaigns keep palette, pitch, passes and size in
  separate campaigns, and the data check blocks a mix.
- **Calibration takes longer.** The second probe adds about 0.4 s at 200 samples, and runs after
  the broadcast probe, before the warm-up.

## Status

Accepted
