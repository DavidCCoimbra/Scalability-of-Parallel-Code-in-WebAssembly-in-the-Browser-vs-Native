# ADR 0057: SIMD campaigns

Date: 2026-11-08

## Context

SIMD (single instruction, multiple data) instructions process several values at once in wide
registers. The study's baseline gives both sides 128-bit SIMD (ADR 0004): native x86-64 with
its SSE2 baseline, and WASM with `simd128`. The code has no explicit SIMD; the vector
instructions come only from the compiler's auto-vectorization.

This extra asks:

- how much of the filter's time, and of the browser / native gap, depends on that
  vectorization;
- what the 128-bit restriction costs native code, which on this CPU could use wider registers.

ADR 0052 planned it as separate builds of the filter: native with AVX2, native without SIMD and
WASM without `simd128`.

## Decision

Decided within the extras design agreed on 2026-11-07 (ADR 0052):

- **One build variant per campaign.** A spec field `build` (`baseline`, `avx2`, `scalar`)
  selects the variant. `make campaign` builds it, the harness runs the variant's native binary
  (`bench/target/<build>/release/native`), and every run records the variant with the commit
  and the binary and WASM hashes. The baseline is unchanged.
- **Variants** (same source, compiler and every other flag):
  - `avx2`: native with `-C target-cpu=native` (AVX2, FMA and BMI on the i9-14900KF; no
    AVX-512). WASM has no wider SIMD, so this variant is native only.
  - `scalar`: native with LLVM's loop and SLP vectorizers off
    (`-C llvm-args=-vectorize-loops=false -C llvm-args=-vectorize-slp=false`), and WASM without
    `simd128` (`-C target-feature=-simd128` appended to the WASM flags, with std rebuilt with
    it). SSE2 cannot be removed from x86-64, but without the vectorizers it is used only for
    scalar operations. This variant compares both sides without SIMD.
- **Checks before measuring**, to confirm that each build is what it claims:
  - the `avx2` binary has 2906 instructions on `ymm` (256-bit) registers, against 0 in the
    baseline;
  - the `scalar` binary has 21 packed integer instructions on `xmm` registers, against 455 in
    the baseline, and the scalar WASM has no SIMD opcode, against 902 in the baseline;
  - all three native builds give the same filter checksum, and rebuilding the baseline WASM
    gives the same hash.
- **Campaigns.** The filter only, because the histogram does not vectorize. They use the main
  campaign's parameters (8192^2, W = 15, N in {1, 2, 4, 6, 7, 8}, 30 runs, 10 iterations, 3 s
  start delay, quiet mode, strict validation):
  - `simd-scalar`: native, Chrome and Firefox, 540 runs, seed 20261110;
  - `simd-avx2`: native only, 180 runs, seed 20261111.

  They ran one after the other from one tagged commit.
- **Comparison with the baseline.** The baseline is the main campaign's filter. It cannot share
  an interleaved campaign with another WASM build, because the page loads one WASM package. The
  drift between campaigns is assumed small, not measured for these builds: the weak scaling
  campaign repeated the main campaign's baseline filter at N = 8 within 0.3 % (ADR 0056). The
  assumption is stated with the results.

## Consequences

- The variants share W = 15 with the baseline; the iteration drift check of ADR 0056 is run on
  both campaigns to confirm the warm-up.
- After `simd-scalar`, `bench/www/pkg` holds the scalar WASM until the next baseline build;
  `make campaign` always rebuilds the spec's variant, so a later campaign cannot use it by
  mistake.
- The results are exploratory (ADR 0052) and get their own ADR (ADR 0058).

## Status

Accepted
