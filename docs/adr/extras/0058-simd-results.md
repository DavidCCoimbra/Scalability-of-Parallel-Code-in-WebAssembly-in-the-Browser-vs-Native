# ADR 0058: SIMD results

Date: 2026-11-08

## Context

The SIMD campaigns of ADR 0057 ran from the commit tagged `measured/simd`:

- `simd-scalar`: 540 runs, native, Chrome and Firefox without SIMD;
- `simd-avx2`: 180 runs, native with `-C target-cpu=native`.

Both ran the filter at 8192^2, W = 15, N in {1, 2, 4, 6, 7, 8}, 30 runs per configuration.

Data, in the working repository: `data/raw/simd-scalar`, `data/raw/simd-avx2`,
`data/tables/simd/simd-*-quality.md`, `data/tables/simd/simd-*-scaling.csv`,
`data/tables/simd/simd-*-iteration-drift.csv`, and `data/tables/simd/simd-variants.csv` with
the figure `paper/figures/simd-efficiency.pdf`. The variants table comes from
`python3 -m analysis.extras.build_variants`, which puts the main campaign's filter as the
baseline next to both variants and adds the excess time TN - T1 / N. Both campaigns were later
re-run on the `measured/v2` build (ADR 0069), whose data are in `data/raw/simd-scalar-v2` and
`data/raw/simd-avx2-v2`; the numbers below are those of `measured/simd`.

## Decision

Record the following results (geometric means of run medians, 95 % bootstrap intervals on the
efficiency).

### Data quality and build identity

- No failed run, no checksum conflict, no run above the foreign CPU threshold, and no
  configuration under 100 times the clock resolution.
- One configuration trends with the execution order (scalar Firefox N = 7, rho = +0.60), but
  its run medians span 20.42 to 20.46 ms (0.2 %), so the trend is negligible.
- In every configuration the first three measured iterations are within 0.4 % of the last three
  (0.997 to 1.004), so the warm-up is complete.
- Every run records the variant, the commit and the artifact hash, and the hashes match the
  binaries of the variant: native scalar `41a3d673`, WASM scalar `c8fa533a` (its recorded WASM
  flags end in `-C target-feature=-simd128`), native avx2 `4fe5c32e`. All three builds give the
  main campaign's filter checksum. On resume the harness compares this identity with the
  campaign's, so a run from another build cannot join it.
- `discardFirstLaunch` is false in `simd-avx2`, because it only discards a browser's first
  launch and that campaign is native only.

### Vectorization accounts for most of the filter's speed, more in the browsers

Without SIMD the filter at N = 1 is 3.94 times slower natively, 4.86 times in Chrome and 4.59
times in Firefox (89.5, 130.5 and 140.9 ms against 22.7, 26.8 and 30.7 ms).

### Without SIMD the browser gap is larger

Browser time over native time (ratios of geometric means, no interval):

| Build | Chrome | Firefox |
|---|---|---|
| scalar (no SIMD) | 1.46 to 1.48, flat across N | 1.56 to 1.58, flat across N |
| baseline (`simd128`) | 1.17 to 1.19 | 1.27 to 1.35 |

So the baseline gap is not caused by the WASM SIMD path: the scalar WASM code is further from
native than the vectorized code is. Why the scalar code is slower in the browser (bounds and
index handling, or the JIT's register allocation or instruction selection) is not measured
here.

### Without SIMD the filter scales almost perfectly

Efficiency at N = 8: native 0.984 [0.981, 0.987], Chrome 0.969 [0.968, 0.970], Firefox 0.985
[0.984, 0.985], against 0.871, 0.871 and 0.928 for the baseline.

### AVX2 is faster but scales worse

Natively with AVX2 the filter is 1.47 times faster than the baseline at N = 1 (15.5 ms) but only
1.22 times faster at N = 8 (2.68 ms); its efficiency at N = 8 is 0.724 [0.721, 0.726]. So the
x86-64 baseline restriction (SSE2, 128-bit) costs native 32 % of its time at N = 1 and 18 % at
N = 8.

`target-cpu=native` changes more than the vector width: it also enables SSSE3 and SSE4.1, FMA
and BMI, and uses the CPU's scheduling model. Width and newer instructions are therefore not
separated; that would need an `x86-64-v2` build, which is not planned.

### Reading: the loss has a different shape natively and in the browsers

Efficiency alone cannot tell a shared resource from a fixed overhead. A fixed cost f per
iteration also gives faster code a lower efficiency, 1 / (1 + N f / T1). The excess time at
N = 8, T8 - T1 / 8 (`excess_ns` in `simd-variants.csv`), separates the two: it grows with the
code's speed if a shared resource is the limit, and stays constant if a fixed overhead is.

| Environment | scalar | baseline | avx2 |
|---|---|---|---|
| native | 178 us | 420 us | 739 us |
| Chrome | 515 us | 495 us | - |
| Firefox | 276 us | 298 us | - |

- **Native: a shared resource.** The excess grows with the code's speed, and with the memory
  traffic. The 64 MiB input and 64 MiB output do not fit in the 36 MB L3, so one iteration
  moves at least 128 MiB: 12 GB/s scalar, 41 GB/s baseline and 50 GB/s AVX2 at N = 8. That is
  the pattern of a resource shared by the cores: memory bandwidth or latency under load, the
  L3, the ring or uncore clock (not logged with turbo off), or per-core power (a possible
  confounder for AVX2 only). AVX2 moves more data than the baseline, so the baseline is not at
  a bandwidth ceiling; at most it sees gradual contention, not saturation.
- **Browsers: mostly a fixed overhead.** In Chrome and Firefox the excess stays about constant
  while the traffic grows about four times (Chrome 8 to 35 GB/s). That is the signature of a
  fixed overhead per iteration rather than of bandwidth. The one overhead measured, the warm
  fork-join (163 us in Chrome at N = 8, the figure of ADR 0056), is only about a third of the 495 to 515 us
  excess, so most of that fixed cost is not explained. The browser losses of ADR 0056 are
  therefore mostly a fixed overhead of unknown origin, and the native loss mostly a shared
  resource.
- **Exceptions.** The ranking has exceptions (native and Chrome baseline tie at 0.871; Firefox
  baseline improves from N = 7 to N = 8), so none of this is a measured cause: uncore counters
  and a frequency log would be needed.

## Consequences

- The paper reports SIMD as an exploratory result: vectorization narrows the browser gap rather
  than causing it; natively the filter's loss grows with the code's speed (a shared resource),
  while in the browsers it is a roughly constant overhead per iteration.
- The baseline comes from another campaign (ADR 0057). Drift between the main campaign
  (2026-11-07) and the SIMD campaigns (2026-11-08) was not measured: the 0.3 % bound of ADR 0056
  (main against weak, N = 8, baseline build) is an assumption carried over. No native baseline
  anchor was run inside these campaigns, though `simd-avx2` could have had one. The
  effects above (18 % and more) are far larger than plausible drift.
- Confirming the native shared resource would need uncore counters or a bandwidth benchmark
  (for example STREAM) on the PC; this is not planned.

## Status

Accepted
