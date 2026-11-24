# ADR 0093: The extras campaign on measured/v3

Date: 2026-11-24

## Context

The extras campaign (ADR 0052, ADR 0054: the private and the packed atomic histograms, the two
main histograms as references and Rayon's two parallel sorts) was run again on `measured/v3` on
2026-11-23 and 24, as ADR 0084 planned and after everything ADR 0088 needed: `extras-v3`, 5400
runs in 16 h 31 min, none failed, missing or excluded, no checksum conflict. One configuration
trends with the execution order (Chrome, private atomic histogram, k = 1, N = 2, rho = +0.52).
It is exploratory and answers none of the questions of ADR 0088.

Between v2 and v3 the private and the packed histograms changed in one thing: they build their
tasks through `Grain::Adaptive.tasks`, as the padded atomic histogram does (ADR 0086).

## Decision

The tables are `data/tables/extras-v3` (`make extras-workloads-results MEASURED=v3`).

- **The extras give the times of v2.** At eight threads every cell is within 1 % of its v2 time,
  except the shared counters at k = 1, which are within 3.4 % and are the cells that fall on
  several time levels from run to run (ADR 0091, question 9).
- **The change of ADR 0086 did not move the histograms it touched.** The private histogram is
  within 0.2 % of v2 in all six cells at eight threads (47.67 against 47.70 ms natively at
  k = 1), the packed one within 0.3 % at k = 256. Their counting loops were found identical to
  v2's in the machine code; this is the same statement in times.
- **The private histogram shows the cost of V8's increment without any contention.** Each thread
  has its own table, so no line is shared. At k = 1 Chrome takes 88.0 ms against 47.7 ms
  natively and 47.8 ms in Firefox, 1.85 times; at k = 256, 52.1 against 47.7 ms. That is the
  dependence on k of the compare-and-swap sequence with one thread (ADR 0089), now at eight
  threads that do not disturb each other: the chain through memory at k = 1 is in the sequence
  itself.

## Consequences

- The reading of the extras in ADR 0054 holds on v3.
- `make extras-results` is now four targets, one per campaign (`extras-workloads-results`,
  `weak-results`, `simd-results`, `hybrid-results`), so that the tables of one do not wait for
  the data of another. For v2 it runs the commands it ran.
- The hybrid campaign is the one campaign of v2 not yet run on v3. Its mask takes twelve E-cores
  into the measured set, so the machine has to be prepared again with the system on CPUs 28 to
  31 (`make env-setup` with other masks, which needs sudo).

## Status

Accepted
