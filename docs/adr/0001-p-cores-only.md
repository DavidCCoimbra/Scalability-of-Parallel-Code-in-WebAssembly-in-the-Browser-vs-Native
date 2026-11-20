# ADR 0001: Measure on P-cores only, with a process-level affinity mask

Date: 2026-10-17

## Context

The measurement machine has an Intel i9-14900KF, a hybrid CPU: 8 performance cores (P-cores,
fast cores with hyperthreading, that is, two hardware threads per core) and 16 efficiency cores
(E-cores, slower and smaller cores). The study measures how speedup changes with the number of
threads N. If threads can land on either kind of core, the speed of each thread changes with N
for reasons that have nothing to do with WebAssembly, and that would be read as a scalability
result.

The usual way to control placement is to pin each thread to a core. Browsers do not allow that:
a web page cannot choose which core a worker thread runs on. Whatever is done must therefore be
possible for a browser as well as for a native process.

## Decision

- Use only the 8 physical P-cores, without hyperthreading (one hardware thread per core).
- Apply the same process-level CPU affinity mask with `taskset` to the native process and to the
  browser process. A process-level mask restricts every thread of the process (and of the
  processes it starts) to the listed CPUs, but leaves the operating system free to place threads
  within that set.
- No per-thread pinning on either side, so native and WASM are placed by the same mechanism. Per-
  thread pinning natively would be a control the browser cannot have.

## Consequences

- The WASM effect is isolated from hardware heterogeneity, and the results describe a machine
  with identical cores, as prior work on parallel scaling does.
- The results do not directly describe hybrid laptops or phones. This is a threat to external
  validity; a P+E experiment was planned as an optional extra (later run, ADR 0059).
- The paper reports the mask and how it was applied.
- Nothing in this ADR alone enforces "no hyperthreading": ADR 0025 turns SMT off and fixes the
  mask to one CPU per physical P-core. ADR 0045 confirms the choice with pilot data (with P+E,
  runs at N = 8 were slower in 5 of 6 configurations and more variable) and makes sure every
  browser process stays inside the masked scope.

## Status

Accepted; amended by ADR 0045 (confirmed with pilot data)
