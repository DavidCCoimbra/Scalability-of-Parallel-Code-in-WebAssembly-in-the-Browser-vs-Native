# ADR 0092: The grain sweeps and the weak scaling on measured/v3

Date: 2026-11-23

## Context

The grain sweeps (ADR 0066, ADR 0067) and the weak scaling campaign (ADR 0055, ADR 0056) were
run again on `measured/v3`, as ADR 0084 planned, on 2026-11-23: `grain-1024-v3` (1620 runs),
`grain-8192-v3` (3780) and `weak-v3` (1080), none failed, missing or excluded, no checksum
conflict and no order trend. They are exploratory and answer none of the questions of ADR 0088.
The one new thing is the atomic histogram in the 8192x8192 sweep, which v2 could not have: it
takes a grain since `measured/v3` (ADR 0086).

## Decision

The tables are `data/tables/grain-v3` (`make grain-results MEASURED=v3`) and
`data/tables/weak-v3` (`make weak-results MEASURED=v3`).

- **The sweeps give the best grains of v2.** At 8192x8192: 4 rows for the filter in the three
  environments, 128 KB for the local histogram natively and in Firefox and 64 KB in Chrome. At
  1024x1024: 128 rows and 128 KB, and 32 rows for the filter in Chrome. The same cells as in v2.
- **Rayon's adaptive split stays within 3 % of the best fixed grain at 8192x8192** (0.995 to
  1.027 times) and 3 to 18 % slower at 1024x1024, as in v2. The main campaign's use of the
  adaptive split costs it nothing at its size.
- **The atomic histogram does not depend on the grain.** At k = 256 with eight threads its time
  over the fifteen grains, from 1 KB to 8192 KB and the adaptive split, stays within 0.3 % of the
  best natively, 0.6 % in Chrome and 1.3 % in Firefox. Its time is the contention for the counters, which the size of
  a task does not change. So giving it the grain (ADR 0086) could not have moved its times, and
  the sweep is the measurement of that.
- **Weak scaling is that of v2**: with 1024 rows per thread the filter keeps 0.860 of its
  one-thread rate at eight threads natively, 0.851 in Chrome and 0.915 in Firefox (0.855, 0.852
  and 0.913 in v2), and the local histogram 0.993 to 0.997.

## Consequences

- The grain figure and the weak scaling figures of the paper can be drawn from v3 with the same
  reading as from v2.
- `make weak-results` is split out of `extras-results`, as `make simd-results` was, so that the
  weak tables do not wait for the extras and hybrid campaigns.

## Status

Accepted
