# ADR 0018: WASM entry configured by the URL query, with a shared config parser

Date: 2026-10-17

## Context

The browser runs receive their configuration in the URL, because no automation framework is
attached to the browser to pass it any other way (ADR 0006). They must produce the same rows as the
native runner (ADR 0016), measured with the same loop (ADR 0015), on a pool of exactly N threads.
Any difference in how the configuration is parsed, how the pool is set up or which thread reads the
clock would be a difference between environments that is not the one under study.

## Decision

- **Build.** The crate builds as `cdylib` + `rlib`. For wasm32 only it depends on `wasm-bindgen`
  (pinned to `=0.2.129`, the version of the CLI) and
  `wasm-bindgen-rayon` 1.3 with `no-bundler` (plain ES modules served by the local server, no
  bundler).
- **JS exports:**
  - `startThreadPool(N)`: records N, then calls wasm-bindgen-rayon's `initThreadPool`, which is
    also exported but must not be called directly;
  - `run(query)`, returning the CSV text;
  - `clockResolutionNs()` and `clockSmallestStepNs()`.
- **One config parser.** One typed `RunConfig` in the library is built from key-value pairs. The
  browser passes the URL query string (`env=chrome&workload=...`); the native runner turns its
  `--flags` into pairs (with `env` fixed to `native`). Both sides go through the same validation.
- **No measurement on the wrong pool.** `run` refuses to measure unless `startThreadPool` was
  called with the configured N. Otherwise a missing or mismatched pool could be recorded under the
  wrong N: asking Rayon for its pool would lazily build a default one instead of failing.
- **Same threading model on both sides.** A global Rayon pool of exactly N workers does the work,
  and the thread that runs `measure` and reads the clock is outside the pool and blocks while the
  work runs.
  - In the browser that thread is the coordinating Web Worker.
  - Natively the runner builds the global pool (`build_global`, one run per process) and calls
    `execute` from the main thread, without `ThreadPool::install`. This replaces the explicit pool
    of ADR 0016, so the two environments have the same structure.
- **Browser clock.** `performance.now()` (milliseconds as `f64`, turned into nanoseconds). Over
  100 000 consecutive readings, `clockResolutionNs()` reports the most common positive step (the
  granularity) and `clockSmallestStepNs()` the smallest one (lower with jitter); both are stored
  with the results.
- **Coordinating worker.** `run` blocks on Rayon (`Atomics.wait`), which the browser's main thread
  may not do, so it must be called from a dedicated coordinating Web Worker, never the main thread
  (the page protocol of ADR 0020).

## Consequences

- The page parses nothing itself: it forwards `location.search`.
- `performance.now()` is coarse and browser-dependent (measured with `clockResolutionNs()`), so
  iterations must be much longer than the resolution; the pilot sizes the image accordingly
  (ADR 0041).
- The wasm32 build is linted by clippy in CI, and its SIMD is checked on the final `bench.wasm`
  (ADR 0017).

## Status

Accepted
