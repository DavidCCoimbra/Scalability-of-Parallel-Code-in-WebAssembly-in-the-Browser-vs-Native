# ADR 0076: What differs below the shared source, and what the v2 calibration measured

Date: 2026-11-21

## Context

The study compares "the same code" natively and as WebAssembly. An audit of the final
repository checked how literally that holds, and what the fork-join calibration of ADR 0030
recorded in the campaigns of `measured/v2`. Four facts were true all along but written in no
record. They do not change any measured number; they change how the numbers may be described.

## Decision

The records state the following, and the README says "same source, compiler and release
profile" instead of "same source, compiler and flags".

- **What is the same.** The crate source, the compiler (one `rustc` string in every recorded
  run) and the release profile (`lto = "fat"`, `codegen-units = 1`, `panic = "abort"`, ADR 0009).
- **What differs below the crate.**
  - *Flags.* The target features and link arguments of ADR 0009 exist only for WASM; a native
    run records empty `rustflags`.
  - *Standard library.* Native links the prebuilt `std`; WASM rebuilds it with
    `-Z build-std` under the project's profile.
  - *Locks inside Rayon.* `wasm-bindgen-rayon` 1.3.0 enables Rayon's `web_spin_lock` feature,
    which replaces rayon-core's `Mutex` and `Condvar` with the `wasm_sync` crate, on WASM only.
  - *Idle threads.* On wasm32 with atomics `std::thread::yield_now` does nothing (the `std`
    thread layer for that target uses the "unsupported" implementation), so the 32 yield rounds
    of rayon-core 1.13.0's idle loop spin without giving up the CPU, where native calls
    `sched_yield`. To sleep, a WASM worker waits in `memory.atomic.wait32`, which each engine
    implements; a native worker uses a futex.
  - *A second compiler.* The engines compile the WASM for the host CPU, so they may use
    instruction encodings newer than the SSE2 baseline the native build is limited to (ADR
    0004 fixes the vector width at 128 bits, not the instruction set). `scripts/check_simd.py`
    checks the compiler's output, not the engines' machine code.
- **The calibration of the v2 campaigns.** Every `*-v2.json` spec sets `calibration` to 20
  samples per probe, not the default of 200 of ADR 0030.
  - With 20 us of clock resolution, Firefox's warm fork-join reads 0 us at N <= 4, and its
    60 us at N = 8 is a median over values that are multiples of 20 us.
  - Warm medians at N = 8 in the main campaign (per run the median of its warm broadcast
    samples, per environment the median over runs): native 8.8 us, Chrome 110 us, Firefox 60 us.
  - Cold against warm depends on the workload of the run. Filter runs at N = 8: cold 205 us
    native, 460 us Chrome, 260 us Firefox, all above warm. Histogram runs: cold 34 to 37 us
    native, 64 to 65 us Chrome, 80 to 90 us Firefox, so Chrome's cold call is cheaper than its
    warm one there. The cause is not established; it is a property of what ran before the
    calibration in each run, not of the pool alone.
- **Fork-join numbers in the records.** The costs quoted across the records differ (native 7.5,
  10.6, 10.7 or 47 us; Chrome 105, 107.5, 110 or 163 us) because they come from different
  builds, campaigns and statistics. Each record now names its source, and
  `docs/adr/README.md` says so once.

## Consequences

- The idle and wake path is inside every timed iteration of a parallel region, so it is part
  of what the environments are compared on. It is the leading candidate for the browsers'
  larger fork-join cost, and is declared as such; no experiment here isolates it.
- "Same code" is claimed for the crate, not for the layers below it. Those layers are the
  environment under study.
- A 200-sample calibration would resolve Firefox's warm fork-join better; the v2 data cannot.
- Nothing is re-measured.

## Status

Accepted; amends ADR 0009 and ADR 0030
