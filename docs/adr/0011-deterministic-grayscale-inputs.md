# ADR 0011: Deterministic grayscale inputs with a fixed seed

Date: 2026-10-17

## Context

Every run, thread count and environment must process exactly the same input. Otherwise the
checksums (a hash of each workload's output, used to prove that every environment computed the
same result) cannot be compared, and timing differences could come from the data rather than
from the environment. The histogram also needs inputs that change how much the threads contend
for the same counters; at the time of this ADR that meant a low-contention and a high-contention
input.

## Decision

- Pixels are `u8` grayscale, one channel, row-major. The histogram has 256 bins and the 3x3
  filter works on one channel.
- Inputs come from SplitMix64, a small pseudo-random generator implemented in the crate (no
  external generator, so no dependency can change the sequence), seeded with the fixed constant
  `0x5EED`. `noise` takes the high byte of each 64-bit output; `few_colors` picks the palette
  index as the full output modulo `k`.
- `noise`: uniform values 0-255 (described here as low contention).
- `few_colors`: `k` values evenly spaced (`i * 256 / k`), and each pixel picks one uniformly
  (described here as high contention). The `k` used in the campaign is decided in the pilot.
- Inputs are generated outside the timed region.
- The seed and `k` are recorded with every result (ADR 0023).

## Consequences

- The pixels are the same on native and WASM (integer arithmetic only), so checksums must match
  across environments and thread counts.
- Threat to validity: one fixed seed and one image size per configuration, so the results
  describe one input each. Mitigation: the data is uniform, and the seed, `k` and image
  fingerprint are recorded with every result (ADR 0023).
- Assumption to verify in the pilot: with padded counters (ADR 0008), which `k` values are used
  does not change contention, only how many (compare two palettes with the same `k`).
- Native/WASM equality of the pixels is checked in the browser CI job (ADR 0024).

Later changes: ADR 0026 replaced the low/high contention wording, because with 256 counters most
updates still contend; inputs are now described by k ("contention spread over k counters"), the
histograms sweep `few_colors` with k in {1, 4, 16, 256}, and k = 256 takes the place of `noise`
for the histograms (the filter keeps `noise`). ADR 0027 and ADR 0032 record the input fingerprint
in every result and compare it with native in the browser CI job; the reference values are those
of the native run, not a list kept in the repository.

## Status

Accepted; amended by ADR 0026 (inputs described by k, not as low/high contention; histograms
sweep k in {1, 4, 16, 256}), ADR 0027 and ADR 0032 (input fingerprint recorded and compared in
the browser CI job)
