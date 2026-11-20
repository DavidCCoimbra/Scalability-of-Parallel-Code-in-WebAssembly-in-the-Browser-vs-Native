# ADR 0017: SIMD parity verified on the built artifacts

Date: 2026-10-17

## Context

ADR 0004 fixes 128-bit SIMD (single instruction, multiple data: one instruction operating on
several values packed in a 128-bit register) on both sides: the x86-64 SSE2 baseline natively and
WASM `simd128` in the browser. That decision only keeps the comparison fair if the compiler
actually vectorizes the Gaussian filter on both targets. If one side were vectorized and the other
not, the gap between environments would mostly measure the compiler, not the runtime.

Checking this is less simple than it looks. Inspecting the library's assembly is misleading here:
with `lto = "fat"` (whole-program link-time optimization), library code only goes through LLVM's
pre-link pipeline, which does not vectorize; vectorization happens at the final link. So the check
must look at the final artifacts.

## Decision

- **A stable, vectorizable interior loop.** The filter's interior loop is a separate function,
  `blur_interior(top, middle, bottom, out)`, marked `#[inline(never)]` so it keeps a stable symbol
  in the final binary.
  - It works on equal-length slices in `u16` arithmetic: the maximum sum, 16 x 255 = 4080, fits.
    This amends ADR 0012, which used `u32` per pixel; results are unchanged (tested against the
    sequential reference).
  - The three rows are separate parameters. Passed as an array, LLVM loses the aliasing
    information and does not vectorize.
  - One `u16` kernel table is used by the interior and the border paths; compile-time assertions
    check that it sums to 16 and that `16 * 255 + 8` fits in `u16`.
- **CI checks vectorization on every change** (`scripts/check_simd.py`) by requiring packed 16-bit
  arithmetic in `blur_interior` (a stray vector register use is not enough).
  - Native: `objdump` of the final x86-64 `native` binary (`paddw`, `pmullw`, `psllw`,
    `punpcklbw`, `packuswb`, ...).
  - WASM: the wasm32 assembly from the full optimization pipeline (LTO off, same optimizations as
    the LTO stage) (`i16x8.add`, `i16x8.shl`, `i16x8.extend_*`, `i8x16.narrow_i16x8_u`, ...).
- **No `target-cpu=native` anywhere.** That flag would let the native build use AVX2 (256-bit),
  which WASM does not have (ADR 0004); `.cargo/config.toml` sets target features for wasm32 only.

## Consequences

- SIMD parity is a tested property, not an assumption.
- One function call per row for the interior loop, which is negligible next to a row of pixels.
- Since the WASM entry exists (ADR 0018), the WASM check inspects the final `bench.wasm` (cdylib,
  fat LTO) with `wasm-objdump`, just as the native check inspects the final binary.
  - `#[inline(never)]` keeps `blur_interior` as a named function under LTO; the check fails if the
    name is missing.
  - The checked file is the cargo output before `wasm-bindgen`, which adds JS glue but does not
    rewrite function bodies (no `wasm-opt` is used).
  - Only the default build is checked: the `pad64` feature changes the histogram counters, not the
    filter.

## Status

Accepted
