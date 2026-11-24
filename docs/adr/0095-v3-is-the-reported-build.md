# ADR 0095: measured/v3 is the reported build

Date: 2026-11-24

## Context

ADR 0084 fixed, before any v3 run, when the paper reports `measured/v3` and not `measured/v2`:
by 2026-11-27 the main campaign has every planned run, no checksum conflict, and every
configuration of the primary contrasts keeps at least 10 runs after the exclusions of ADR 0037
and ADR 0051. The criteria read counts of runs, never a result.

## Decision

`measured/v3` is the build the paper reports. The criteria were met on 2026-11-22:

| Criterion | `campaign-v3` |
|---|---|
| Planned runs done | 5310 of 5310, none failed or missing |
| Checksum conflicts | 0 |
| Runs excluded (replaced, strict validation, foreign CPU time) | 0, so every configuration keeps its 30 runs |

- **No conclusion of the primary contrasts differs from v2.** The ten contrasts of ADR 0037
  are rejected or not rejected as in v2: Chrome against native on the filter is not rejected in
  both (0.996 in v3, 0.990 in v2), Firefox at k = 1 on the atomic histogram is not rejected in
  both (1.010, 0.994), and the other eight are rejected in both, with effects of the same sign.
  The tables are `data/tables/campaign-v3`.
- **Every campaign of v2 has its twin on v3**, on the tagged binaries (digests recorded by each
  campaign): cutoff, grain sweeps, counters, SIMD variants, weak scaling, extras and hybrid.
  v3 adds the sequential references, the engine arms, the grain by threads and the counters of
  the loop alone. The records of what they show are ADR 0089 and ADR 0091 to 0094.
- **`MEASURED` is `v3` by default**, so every `make` target and the `tables` job of CI read and
  regenerate the v3 tables, the v3-only ones included (`make all-results` now runs
  `v3-results`).
- **The v2 data and specs leave the repository**, as ADR 0084 said, in the pull request after
  this one. They stay at the tag `data/v2`, with the code that reads them. No table, figure or
  comparison of the paper combines the two builds (ADR 0062).

## Consequences

- A number quoted from ADR 0079 or from an earlier result record is a v2 number or older. The
  paper takes its numbers from `data/tables/*-v3` and the records of v3.
- The gate of the build failed on one cell and the campaign went ahead with that declared
  (ADR 0087). That cell, Firefox on the local histogram at k = 1 with eight threads, is the
  control of one primary contrast; ADR 0087 measured its effect on the run value at about 0.1 %.
- The tables of v3 were written on the measuring PC. From this change on CI regenerates each of
  them on another machine and compares it with the committed one.

## Status

Accepted
