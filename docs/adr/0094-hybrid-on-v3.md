# ADR 0094: The hybrid campaign on measured/v3, and analysis on this PC after the measurements

Date: 2026-11-24

## Context

The hybrid campaign (ADR 0059, ADR 0061: every P-core plus twelve E-cores, N up to 20) was the
last campaign of v2 without a twin on `measured/v3`. It ran on 2026-11-24 after the machine was
prepared for its mask (`make env-setup P_MASK=0,2,4,6,8,10,12,14,16-27 E_CPUS=28-31`):
`hybrid-v3`, 900 runs in 1 h 53 min, none failed, missing or excluded, no checksum conflict, no
order trend. It is exploratory and answers none of the questions of ADR 0088.

## Decision

The tables are `data/tables/hybrid-v3` (`make hybrid-results MEASURED=v3`).

- **The hybrid campaign gives the picture of v2.** The filter gains little from the E-cores: its
  speedup goes from 6.46 at eight threads to 8.01 at twenty natively (6.49 and 8.02 in v2), 6.55
  to 7.62 in Chrome and 7.02 to 8.62 in Firefox. The local histogram at k = 1 goes far beyond
  the thread count, as in v2 (25.5 natively, 29.5 in Chrome and 25.4 in Firefox at twenty
  threads), which ADR 0061 traced to the E-cores running that dependent chain faster than the
  P-cores do.
- **The cells with E-cores vary more between the two builds than the others.** The native local
  histogram is 13.39 against 12.97 at twelve threads, 19.43 against 18.05 at sixteen and 25.50
  against 23.52 at twenty, up to 8 % apart, where every cell on P-cores alone is within 1 %.
  Which threads the kernel puts on which kind of core is not controlled, and this campaign does
  not record it per thread.

**Analysis on this PC after `make env-restore`.** With the machine restored, turbo is on and a
process that is not pinned can run on the degraded core (ADR 0085). The first attempt to write
these tables stopped with a `TypeError` raised inside Python's own `statistics` module, on data
that the same command reads without error: a wrong computation, not a crash, and no entry in the
kernel log. The tables of this record were written with the commands pinned away from that core
(`taskset -c 0-11,14-31`). Every other v3 table was written while the machine was prepared.

## Consequences

- Every campaign of v2 now has its twin on `measured/v3`.
- On this PC, outside a prepared session, analysis and builds are run pinned away from CPUs 12
  and 13. A wrong result that does not crash is the case that pinning is for.
- When `MEASURED` becomes `v3`, the `tables` job of CI regenerates every v3 table on another
  machine and compares it with the committed one, which checks all of them independently of
  this PC.

## Status

Accepted
