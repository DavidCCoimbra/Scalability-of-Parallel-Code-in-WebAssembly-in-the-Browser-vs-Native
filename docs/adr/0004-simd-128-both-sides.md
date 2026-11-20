# ADR 0004: 128-bit SIMD on both sides

Date: 2026-10-17

## Context

SIMD (single instruction, multiple data) instructions process several values at once; their
width is how many bits one instruction handles. Natively, x86-64 could use AVX2 (256-bit) by
compiling with `target-cpu=native`, while WebAssembly only has 128-bit SIMD (`simd128`). If the
native build used wider vectors, part of the native-vs-WASM gap would come from the vector
width, not from the runtime, and the two effects could not be separated.

## Decision

- Native builds use the default x86-64 baseline (SSE2, 128-bit), with no `target-cpu=native`.
- WASM builds use `simd128`.
- Both sides therefore vectorise at 128 bits.

## Consequences

- The gap measures the runtime, not the width of the instruction set.
- Native performance is below what the PC can reach. A "best of each" SIMD experiment (each side
  with its widest SIMD, and both without SIMD) was planned as an optional extra (later run,
  ADR 0057).
- Choosing the flags does not prove that the compiler vectorises the code on both targets;
  ADR 0017 checks that on the built binaries.

## Status

Accepted
