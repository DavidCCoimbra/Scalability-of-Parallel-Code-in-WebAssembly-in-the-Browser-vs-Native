# ADR 0041: Image size 8192x8192 and a clock factor of 100

Date: 2026-11-06

## Context

The analysis plan (ADR 0037, amended by ADR 0039) flags a configuration whose median run value
is below a factor times the coarsest recorded clock resolution, because a browser clock that is
coarse compared with an iteration makes the measured time mostly quantisation error. The plan
leaves both the image size and the final factor to the pilot; it started with a factor of 1000.
The image size matters in two ways: a larger image makes each iteration longer compared with the
clock, but also makes the campaign longer, and it changes how much work each parallel region
has compared with the fixed cost of forking and joining threads.

### The size sweep

The size sweep on the PC (specs `data/earlier/pilot/specs/pilot-size-*.json`, runs `data/earlier/pilot/pilot-size-*`: the
filter, `hist-local` k = 16 and `hist-atomic` k = 1, at N = 1 and 8, 3 runs each, 2026-11-06)
gave:

- **Clock resolution**, measured in every browser run: 5 us in Chrome, 20 us in Firefox.
- **The fastest browser configuration at N = 8**, in multiples of the resolution:

  | Browser | 2048 | 4096 | 8192 | 10240 |
  |---|---|---|---|---|
  | Firefox | 24x | 68x | 213x | 322x |
  | Chrome | 69x | 248x | 802x | 1198x |

- **No cache effect.** The filter's time per megapixel at N = 1 is flat from 4 to 105 MP (about
  0.33 ms/MP natively): there is no step when the input leaves the 36 MB last-level cache (LLC),
  so the filter stays compute-bound at every size tried.
- **Filter speedup at N = 8** (native / Chrome / Firefox): the gap shrinks as the work per
  parallel region grows.

  | Image size | Native | Chrome | Firefox |
  |---|---|---|---|
  | 2048 | 4.91 | 3.45 | 4.13 |
  | 4096 | 6.14 | 5.15 | 5.83 |
  | 8192 | 6.68 | 6.61 | 7.17 |
  | 10240 | 6.78 | 6.78 | 7.37 |

- **The slowest configuration** (`hist-atomic` k = 1, N = 8, Chrome) takes 2.2 s per iteration at
  8192 and 2.8 s at 10240.

A factor of 1000 is out of reach at any usable size: Firefox would need images above
20000x20000, past Chrome's canvas limit of about 268 MP, with the slowest configuration above
10 s per iteration.

## Decision

Decided by the author on 2026-11-06, before any campaign data:

- **Image 8192x8192** (67 MP, the size of a current phone photo). It is the smallest size tried at
  which the configurations of the sweep clear a factor of 100 in both browsers, with a margin of
  2x in Firefox. The sweep covered the fastest configuration of the smoke test (`hist-local`
  k = 16) but not every k; the warm-up pilot (ADR 0043), which runs every campaign workload at
  8192, checks the rest, and a flagged configuration there reopens this decision. The
  alternative, 10240, adds clock margin for about 45 % more campaign time with the same
  speedups.
- **Clock factor 100** (`analysis/quality.py`, now the package `analysis/quality/`). It is a
  pragmatic bound, chosen after the sweep showed that 1000 is out of reach: it caps the
  quantisation error of a single sample at 1 % of an iteration. The median over iterations does
  not remove a systematic bias of a coarse clock, so the bound is not claimed to be tighter. It
  stays a warning; nothing is excluded for it.
- **Pilot values are not results.** The sweep's warm-up and iteration counts (2 and 5) are pilot
  values; the campaign's W comes from the warm-up pilot (ADR 0043). The sweep's speedups, from 3
  runs and without intervals, are not quoted as results.
- **The sweep is exploratory.** It is reported in the paper as exploratory (the gap against the
  work per parallel region), with the caveat that the smaller sizes are under the clock factor
  in Firefox.
- **Fixed granularity.** The granularity stays fixed (`CHUNK_BYTES` = 64 KB and the filter's own
  split), the same in every environment. There is no sequential cutoff (a size below which work
  is no longer split into parallel tasks), because the fork-join cost in the browser is part of
  what RQ1 measures.

## Consequences

- RQ1 is answered at one size where the work dominates the fork-join cost; where the gap
  disappears for smaller work is shown, not tested.
- Testing size as a factor would need repeated passes inside each timed sample, so that small
  sizes clear the clock; that is left out.
- The campaign time estimate uses 8192.

## Status

Accepted; amends ADR 0037 and ADR 0039
