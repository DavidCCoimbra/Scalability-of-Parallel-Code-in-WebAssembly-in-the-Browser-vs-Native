# ADR 0008: Padded shared atomic counters, allocation outside the timed region

Date: 2026-10-17

## Context

RQ2 uses an atomic histogram: threads count pixel values by incrementing shared atomic counters.
It must measure true sharing, that is, contention when several threads update the same counter.

CPU caches move memory in cache lines (64 bytes on x86). If two different counters sit on the
same line, threads that update different counters still fight over that line. This is false
sharing: a cost that comes from the memory layout, not from the synchronisation the study wants
to measure. Intel CPUs also have an adjacent-line prefetcher that fetches 64-byte lines in pairs,
so two counters on neighbouring 64-byte lines can still interfere (ADR 0049).

Separately, the default WebAssembly allocator takes a global lock. Allocating inside the timed
region would add a synchronisation cost in WASM that native does not have.

## Decision

- Each shared atomic counter is padded to its own cache line: `align(128)` by default (one pair
  of 64-byte lines per counter), with a `pad64` feature that pads to 64 bytes instead.
- Allocation and counter reset happen outside the timed region.

## Consequences

- Contention results reflect true sharing. False sharing is an optional extra variant (later run
  as `hist-atomic-packed`, ADR 0052).
- With 256 counters, the 128-byte table is 32 KiB, the size of an E-core L1 data cache. Whether
  64 or 128 bytes makes a difference is checked in the pilot (ADR 0049: no measurable difference,
  128 kept).
- The paper's methodology states the padding.

## Status

Accepted; amended by ADR 0049
