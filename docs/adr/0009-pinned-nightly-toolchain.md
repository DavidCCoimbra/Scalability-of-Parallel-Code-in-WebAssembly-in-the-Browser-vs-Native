# ADR 0009: Pinned nightly Rust toolchain with `-Z build-std` for WASM threads

Date: 2026-10-17

## Context

WebAssembly threads need the Rust standard library (`std`) compiled with the `+atomics` target
feature, so that its synchronisation primitives use real atomic instructions on shared memory.
The prebuilt `std` that Rust ships for wasm32 is not compiled that way. Rebuilding it needs the
`-Z build-std` option, which only exists on the nightly toolchain, and nightly changes every day.

The study also requires that native and WASM are built by the same compiler, so that a
difference between them is not a compiler-version difference.

## Decision

- Pin `nightly-2026-10-03` in `bench/rust-toolchain.toml`, with `rust-src` (needed to rebuild
  `std`) and the wasm32 target.
- WASM builds use the target features `+atomics,+bulk-memory,+mutable-globals,+simd128`, shared
  imported memory with a 4 GiB maximum and the TLS (thread-local storage) exports, and rebuild
  `std` with `-Z build-std=panic_abort,std`.
- Both targets share one release profile (`lto = "fat"`, `codegen-units = 1`,
  `panic = "abort"`).

## Consequences

- rustc, `std` and LLVM are identical on the Mac (development) and the PC (measurements), for
  native and WASM, for the whole study.
- Nightly features may break; the pinned date avoids surprises but also freezes bug fixes.
- If a browser refuses to reserve 4 GiB of shared memory, the maximum is the first thing to
  change.

## Status

Accepted
