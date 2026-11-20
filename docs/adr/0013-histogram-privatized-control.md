# ADR 0013: Histogram control with per-task privatization over 64 KiB chunks

Date: 2026-10-17

## Context

RQ2 asks how much thread synchronisation contributes to the native-vs-WASM gap. It compares a
histogram with shared atomic counters (ADR 0014) against a control that needs no
synchronisation while counting. For the comparison to isolate synchronisation, the two variants
must differ only in how the counts are combined; the work split must be the same.

## Decision

- Control variant (privatisation): Rayon `fold` builds a private `[u64; 256]` histogram per task,
  then `reduce` merges them. Privatisation is per Rayon task, not per thread: Rayon creates as
  many fold accumulators as it splits the work into, and a thread may run several tasks.
- Both histogram variants split the pixels into 64 KiB chunks (`par_chunks(CHUNK_BYTES)`), so
  they share the same minimum granularity and only the synchronisation differs.
- Checksum: FNV-1a over the 256 counts as little-endian `u64`, the same for both variants,
  computed outside the timed region. It replaces the formula `sum((i + 1) * count[i])` first
  planned, which collides when counts move between bins in opposite directions (two different
  histograms can give the same value).

## Consequences

- The control measures parallel counting plus a reduction of 256 counters per task, with no
  shared writes.
- Creating and merging the per-task histograms is part of the timed work: it is intrinsic to the
  privatisation approach, not setup.
- The chunk size fixes the number of chunks, not the number of tasks. Rayon splits adaptively,
  so one fold accumulator may cover several chunks, and the number of private histograms and
  merges varies with the thread count. That variation is part of the measured cost. The pilot
  image must give well over 8 chunks.

## Status

Accepted
