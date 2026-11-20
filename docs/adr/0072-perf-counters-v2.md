# ADR 0072: Hardware counters of the atomic histogram on measured/v2

Date: 2026-11-13

## Context

The paper's explanation for RQ2 (why shared atomic counters cost Chrome more) rests on two kinds
of evidence:

- **The machine code of the atomic add** (item A7 of the v2 bottleneck audit, on
  `measured/v2`):
  - V8 emits a load followed by a `lock cmpxchg` retry loop (a compare-and-swap that is retried
    if another core changed the value in between);
  - SpiderMonkey and LLVM emit a single `lock add`.
- **Hardware counters per atomic operation** (ADR 0049, `data/raw/pilot-perf`, in the working
  repository). They showed that Chrome reads the contended cache line before it writes it.

The counters had three problems:

- They come from a pilot on the earlier build. Since then v2 removed the per-pixel bounds check
  and let the loop unroll by 8 (ADR 0069), so they describe code that is no longer measured.
- They are one run per cell, and Chrome's read HITM (a read served from a line that another
  core has modified) appears in only one of its two runs.
- Whether V8's compare-and-swap actually retries under contention was never measured.

On 2026-11-13 it was decided that the paper uses only `measured/v2` data for its results;
pilot data only justifies design decisions.

## Decision

- **Campaign `perf-v2`** (`harness/campaigns/perf-v2.json`):
  - an ordinary randomized campaign on `measured/v2`, order seed 2026111301, quiet mode, 30 runs
    per configuration;
  - `hist-atomic` at k = 1 and 256, N = 1 and 8, in native, Chrome and Firefox, for 360 runs.
- **Counting** (`scripts/perf-counters-v2.sh`):
  - `perf stat` counts the eight P-cores system-wide in 100 ms intervals during the whole
    campaign, running itself as a transient system unit on the E-cores so that it stays off the
    measured cores;
  - events: cycles, instructions, `mem_inst_retired.lock_loads` (locked loads, one per locked
    read-modify-write attempt), `ocr.demand_rfo.l3_hit.snoop_hitm` (the line taken for writing
    from another core) and `ocr.demand_data_rd.l3_hit.snoop_hitm` (the line read from another
    core).
- **Per-run counts** (`analysis/extras/perf_counters.py`, run as
  `python3 -m analysis.extras.perf_counters`):
  - runs are sequential, so the intervals that end inside a run's `startedAt` to `finishedAt`
    window are that run's counts;
  - each run's counts are divided by its atomic operations, one per pixel per warm-up or
    measured iteration;
  - per configuration: the arithmetic mean over runs with a 95 % percentile bootstrap interval.
    Not the geometric mean, because a rate can be 0.
- **Retries.** Every compare-and-swap attempt is one locked load, so `lock_loads` per operation
  above the native value measures V8's retries. This turns the retry hypothesis into a
  measurement.
- **Not reported.** The run times of this campaign are not reported, because the counting
  session runs during it; only the counters are.

## Consequences

- **v2 only.** The paper's counter-based statements come from `measured/v2` with intervals, and
  the pilot counters leave the paper.
- **What a run window holds.** The counts are system-wide on the P-cores, so they include the
  browser's start-up and calibration in the run window. Those add few locked operations next to
  the 1.0e9 of the timed loop, and the per-run window keeps runs apart.
- **Same method for all.** Native is counted the same way as the browsers, system-wide. The
  pilot counted only the native process.
- **Cost.** About 1.5 h of machine time, with nothing else running on the PC meanwhile.

## Results

Campaign `perf-v2` on 2026-11-13: 360 runs, none failed, data check clean
(`data/tables/perf-v2/perf-v2-quality.md`). Per add at N = 8, means of 30 runs
(`data/tables/perf-v2/perf-v2-counters.csv`, `perf-v2-retries.csv`):

| k | Environment | locked loads above N = 1 [95 % CI] | RFO HITM | read HITM | cycles |
|---|---|---|---|---|---|
| 1 | native | 0.0013 [0.0009, 0.0019] | 0.24 | 0.0002 | 327 |
| 1 | Firefox | 0.0023 [0.0020, 0.0026] | 0.25 | 0.006 | 363 |
| 1 | Chrome | 0.2523 [0.2364, 0.2675] | 0.20 | 0.30 | 696 |
| 256 | native | 0.0009 [0.0003, 0.0016] | 1.04 | 0.0001 | 158 |
| 256 | Firefox | 0.0007 [0.0005, 0.0009] | 0.89 | 0.006 | 164 |
| 256 | Chrome | 0.0144 [0.0141, 0.0148] | 0.52 | 0.71 | 86 |

(RFO HITM: the line was requested for ownership, to write it, and found modified in another
core.)

- **V8's compare-and-swap retries** on one add in four at k = 1, and rarely at k = 256. Locked
  loads per add at N = 1 are 1.000 native, 1.016 Chrome and 1.037 Firefox, so 0.25 is a rate of
  extra attempts. The pool's own locked operations (work stealing, latches, wake-ups) also grow
  with N. The control is the excess of the other environments at the same k, above all
  Firefox, which runs the same WASM module and the same Rayon and wasm-bindgen-rayon code (0.002
  at k = 1).
- **Work outside the loop.** The run window also holds start-up, calibration and teardown (60
  to 105 intervals of 100 ms per run), whose locked operations are in the numerator only. Their
  size is the N = 1 baseline above native: 0.016 per add in Chrome and 0.037 in Firefox.
  Firefox's excess from N = 1 to N = 8 (0.002) bounds how much these phases change with N.
- **Chrome reads before it writes.** Chrome reads the contended line from another core before
  writing it; native and Firefox only take it for writing. At k = 1 this doubles Chrome's line
  transfers.
- **k = 256.** At k = 256 Chrome moves more lines than native in about half the time; why is not
  isolated.
- **Cycles as a check.** Cycles are the busy cycles of the eight cores, spinning and waiting
  included, so they track wall time x cores, not work. They match T_N of the main campaign (for
  example Chrome k = 1: 1848 ms x 8 cores x 3.2 GHz / 67 M pixels = 706 against 696 counted), a
  check that the per-run windows hold the right intervals.
- **The padding holds in WASM memory.** `perf c2c` during one k = 16, N = 8 run per browser on
  the same build (`data/raw/perf-v2/c2c/`) finds 16 contended lines 0x800 bytes apart, every
  access at offset 0, in Chrome and Firefox.

## Status

Accepted
