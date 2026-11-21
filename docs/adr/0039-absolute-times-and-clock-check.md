# ADR 0039: Absolute time ratios and a clock resolution warning

Date: 2026-10-19

## Context

A methodology review of the analysis plan (ADR 0037) on 2026-10-19 found two gaps.

- **Relative speedup hides a slow baseline.** Speedup is only ever computed within an
  environment (ADR 0003). If WASM is slower than native at N = 1, its relative speedup T1/TN
  can look better only because its baseline T1 is slow. Hoefler and Belli's rules for
  reporting parallel performance warn against reading a speedup without its baseline, and the
  plan reported no comparison of absolute times.
- **No check of the clock.** `performance.now()` in the browser is coarse, and nothing checked
  that iterations are long compared with the clock resolution. An iteration only a few clock
  ticks long is mostly quantisation error.

## Decision

Decided by the author on 2026-10-19, before any campaign data, as a dated amendment to the
analysis plan:

### Absolute time ratios

- The absolute time ratio `T(browser, N) / T(native, N)` is estimated for every browser,
  workload, input, k and N, as `log T(browser, N) - log T(native, N)` with a 95 % bootstrap
  interval, the two groups resampled independently (`analysis/inference.py`, question `ABS`).
- Every comparison of scaling is read next to this ratio.
- It is exploratory: no p-value, and not in the primary family, which stays at 10 contrasts.
- The ratios at N = 1 and at the maximum N are always reported. A browser configuration there
  without its native counterpart is warned about and listed in the sidecar JSON as
  `missingAbsolute`. Absolute time against N is plotted per environment.

### Clock resolution warning

- A configuration whose median run value is below 1000 times the coarsest `clockResolutionNs`
  of its runs is flagged as a warning by `analysis.v0` and `analysis.results` (printed and
  stored in the sidecar).
- Configurations without any recorded resolution are counted as unchecked (`clockUnchecked`), so
  "not flagged" and "not checked" stay apart.
- Nothing is excluded for it. The image size pilot sizes the image so that no configuration is
  flagged and sets the final factor (ADR 0041 later set it to 100, because 1000 is out of reach
  at any usable image size in Firefox).
- Note of 2026-11-21: `clockResolutionNs` is, on both sides, the most common step between two
  consecutive clock reads. In the browsers that is the resolution of `performance.now()` (5 or
  20 us). Natively the clock counts nanoseconds and the step (59 to 77 ns in the main campaign) is
  the time one read takes, so it is an upper bound of the resolution, not the resolution. The
  check is conservative with it and the name stays, because it is in every recorded run.

### Number of runs

- The number of runs stays a pilot decision (ADR 0047), checked against the stability of the
  99.5 % bounds of the primary contrasts.

## Consequences

- Relative speedup is never read without the baseline it is relative to.
- The 10-contrast family, Holm and the Bonferroni level are unchanged.
- A flagged configuration in a pilot means the image is too small for the browser clock.

## Status

Accepted; amends ADR 0037 and ADR 0038; amended by ADR 0041 (image size, clock factor of 100)
