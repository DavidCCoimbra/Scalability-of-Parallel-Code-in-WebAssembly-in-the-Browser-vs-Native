# ADR 0049: 128-byte padding kept, and why Chrome's atomics behave differently

Date: 2026-11-07

## Context

The atomic histogram (`hist-atomic`) is meant to measure true sharing: threads contending for
the same counter. It must not also measure false sharing, where threads update different
counters that happen to sit in the same cache line, so the line still bounces between cores.
ADR 0008 therefore pads every shared atomic counter to its own 128-byte line (`align(128)`; a
`pad64` feature gives 64 bytes). 128 rather than 64 bytes was chosen because Intel's
adjacent-line prefetcher fetches 64-byte lines in pairs, so two counters in neighbouring
64-byte lines could still interfere.

Three questions were open:

1. Would 64 bytes do as well? (left to the pilot by ADR 0008)
2. Does the padding hold inside WASM linear memory (the single flat memory a WASM module
   addresses)? (left to the pilot by ADR 0008)
3. Why does `hist-atomic` at k = 256 scale in Chrome (speedup 2.00 at N = 8) and not natively
   (0.89)? This came up in the thread count pilot (ADR 0044).

### Padding pilot

The pilot (`harness/campaigns/pilot-pad{128,64}.json`, 2026-11-07; in the working repository)
ran native `hist-atomic` at k = 1, 4, 16 and 256, at 8192x8192, N = 1 and 8, 10 runs each,
once with the default build and once with `--features pad64`. Each run records
`build.features` and `artifactSha256`, so the build of each run is known.

Ratio pad64 / pad128 of geometric means (`analysis/compare.py`, 95 % bootstrap interval):

- every N = 1 cell is within 0.6 %;
- at N = 8: k = 1: 1.017 [0.947, 1.090], k = 4: 0.991 [0.970, 1.011], k = 16: 1.012 [1.001,
  1.022], k = 256: 1.011 [1.009, 1.014].

The two builds ran as separate campaigns one after the other, so a difference of about 1 % is
within drift: no difference was detected. With 10 runs the resolution is limited, most at
k = 1, N = 8, where the interval spans about 7 % either way; a difference below that cannot be
ruled out there.

### Hardware counters (exploratory)

`perf stat` was run on the P-cores (`data/raw/pilot-perf`, in the working repository), one run
per row, for `hist-atomic` k = 256 at N = 8. The values are per atomic operation, counted with
`mem_inst_retired.lock_loads` (about 1.0e9 per run in every environment).

The rows are not like for like. Native counts only the runner process. The browsers count the
8 P-cores system-wide during a one-run campaign, which adds the browser's start-up, its other
processes and the input generation. Because those extra phases perform few atomic operations,
they weigh little in the per-operation values.

| Environment | RFO HITM / op | read HITM / op | cycles / op |
|---|---|---|---|
| native | 0.89 | 0.0001 | 163 |
| Firefox | 0.84 | 0.004 | 131 |
| Chrome (two runs) | 0.35, 0.35 | 0.75 (second run only) | 85, 85 |

HITM means that the requested line was found in another core's cache in modified state, so it
had to be taken from that core. RFO (read for ownership) is a request for the line in order to
write it (`ocr.demand_rfo.l3_hit.snoop_hitm`); read is a request only to read it
(`ocr.demand_data_rd.l3_hit.snoop_hitm`).

At N = 1 there are almost no HITMs anywhere, and the cycles per operation are native 19, Chrome
26 and Firefox 33. The browsers' single-thread code is slower: about 28 instructions per
operation in Chrome and 39 in Firefox (system-wide), against 10 natively. So part of Chrome's
speedup of 2.00 at N = 8 comes from a slower T1, as the absolute time ratios of ADR 0039 show.

### Placement in WASM memory

`perf c2c` (a tool that reports which cache lines are contended between cores, and at which
offsets) during a Chrome `hist-atomic` k = 16 run at N = 8 shows 16 contended cache lines, each
with about 6 % of the HITMs, 0x800 bytes apart (the 16 values of the spread palette are 16 bins apart and every bin is
  128 bytes, so 16 x 128 = 0x800; in the palette's
order). Each line is accessed at a single offset (0x0): every counter is alone in its line
inside WASM memory.

## Decision

Decided on 2026-11-07; the option recommended from the data above was applied:

- **The padding stays at 128 bytes (ADR 0008).** No difference was detected at 64 bytes (to
  within about 7 % at k = 1, N = 8), and 128 is the safer choice against the adjacent-line
  prefetcher.
- **The padding holds in WASM, as far as checked.** In the one Chrome `perf c2c` run (k = 16,
  N = 8) the alignment of `PaddedCounter` is kept in linear memory (the c2c offsets above), so
  that run shows no false sharing. Firefox was not checked this way.
- **Chrome's `hist-atomic` k = 256 advantage at N = 8 is consistent with different machine code
  for the same atomic add.** Native (LLVM) and Firefox show the pattern of a locked add, where
  almost every operation takes the line from another core for writing. Chrome instead shows
  reads of the line (0.75 read HITMs per operation), only a third of its operations still
  needing the line for writing, and fewer cycles per operation when the contention is spread
  over 256 counters. One explanation is a load followed by a compare-and-swap loop. But V8
  usually lowers a 64-bit atomic add on x64 to `lock xadd`, and the extra reads could come from
  elsewhere in the hot loop. The code was not inspected here. Inspecting it (for example with
  `perf record` and V8's `--perf-prof` jitdump) is left open, and the finding is reported as a
  hypothesis in RQ2.

## Consequences

- The campaign keeps the default build (`align(128)`).
- RQ2 results are read with this in mind: the same source does not give the same
  synchronisation code in every environment, and when contention is spread over many counters
  that can favour the browser.
- Threat to validity: the browser counters are system-wide on the P-cores and include the
  browser's start-up and input generation. They are normalised per atomic operation, of which
  those phases have few.

## Status

Accepted; amends ADR 0008
