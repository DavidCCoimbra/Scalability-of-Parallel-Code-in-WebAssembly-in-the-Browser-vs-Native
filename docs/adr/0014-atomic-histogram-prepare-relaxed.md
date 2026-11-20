# ADR 0014: Atomic histogram with a prepare step and Relaxed ordering

Date: 2026-10-17

## Context

The atomic histogram is the synchronised variant of RQ2. It counts with shared `AtomicU64`
counters, one per cache line (ADR 0008), and is compared with the privatised control
(ADR 0013). Its counters must be zero before every timed iteration, and resetting them must not
be timed, because the reset is not part of the counting work.

Atomic operations in Rust take a memory ordering, which says how much the operation constrains
the order of other memory accesses. `Relaxed` makes the operation atomic but imposes no order;
`SeqCst` (sequentially consistent) is the strongest.

## Decision

- `Workload` gains `prepare()` (default: nothing), called before every timed `run()` and outside
  the timed region. `AtomicHistogram::prepare` resets the 256 counters through `get_mut`: no
  atomic operations are needed, since nothing else holds a reference at that point.
- The 256 `PaddedCounter`s are allocated once in the constructor (`repr(align(128))`, or
  `repr(align(64))` with the `pad64` feature).
- `run` uses the same `par_chunks(CHUNK_BYTES)` split as the control and
  `fetch_add(1, Ordering::Relaxed)`.
- CI runs the tests with and without `pad64`.

## Consequences

- `Relaxed` is enough for a counter whose value is read only after `run` returns: Rayon's join,
  which waits for every task, is the synchronisation point.
- The ordering makes no difference to the generated code on the study's targets: x86 locked
  read-modify-write instructions are full barriers whatever ordering is requested, and
  WebAssembly atomics are always sequentially consistent.
- The measurement loop (ADR 0015) must call `prepare` before each timed iteration.

## Status

Accepted
