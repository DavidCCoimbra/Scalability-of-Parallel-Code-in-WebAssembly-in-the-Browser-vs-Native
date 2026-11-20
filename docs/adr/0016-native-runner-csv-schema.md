# ADR 0016: Native runner and the shared CSV result schema

Date: 2026-10-17

## Context

The study compares the same code in three environments (native, Chrome, Firefox), so their results
must end up in one table with one schema; otherwise the analysis would need per-environment
adapters, and a column that means something slightly different in one environment could go
unnoticed.

Two further needs shape the native runner:

- It must measure with exactly N threads. Speedup is T1/TN (ADR 0003), so a run recorded under N
  that actually used a different number of threads would corrupt every speedup it enters.
- The number of warm-up iterations W is chosen from data (ADR 0015), so warm-up times must be
  kept, not discarded.

## Decision

- **Binary.** `native` (`bench/src/bin/native/`) takes
  `--workload filter|hist-atomic|hist-local --input noise|few [--k K] --threads N --width W
  --height H [--seed S] --warmup W --iters K`.
  - `--k` is required for `few` and must be in 1..=256.
  - Threads, width and height must be at least 1. For threads this matters: Rayon reads 0 threads
    as "use the default", so a 0 would be measured with a thread count that is not the one recorded.
  - A repeated option is an error, and the seed defaults to `0x5EED`.
  - The parser is hand-written: the crate is also built for WASM, and it takes no CLI dependency.
- **Exactly N threads.** An explicit `rayon::ThreadPool` with N threads is built before measuring,
  and `measure` runs inside `ThreadPool::install`, so pool creation is not timed and the work runs
  on that pool. (Later replaced by a global pool, see Status.)
- **CSV on stdout**, one row per iteration, with the header
  `env,workload,input,k,width,height,seed,threads,phase,iter,ns,checksum`.
  - Compared with the first plan for this runner, `k`, `width`, `height` and `seed` were added so
    that each row fully identifies its workload configuration (`k` is empty for `noise`).
  - `phase` (`warmup` or `measured`) keeps the warm-up rows in the same file instead of dropping
    them; `iter` counts from the start of each phase.
  - The checksum is printed as 16 hex digits.
- **Shared types.** `Environment`, `WorkloadKind`, `InputKind`, `Record` and `RunContext` live in
  the library, not in the native binary, so the WASM entry produces exactly the same rows.

## Consequences

- One schema for all environments; the analysis filters `phase = measured`.
- Run context beyond these columns (commit, CPU, governor, turbo, kernel, browser version) is not
  in the CSV; it is added in a separate file by ADR 0023.
- A run that exits non-zero is invalid and must be logged by the harness, never dropped silently
  (implemented by the failed-run records of ADR 0027 and the orchestrator of ADR 0034).

## Status

Accepted; amended by ADR 0018 and ADR 0032 (global pool, no `install`), ADR 0027 (input
fingerprint column) and ADR 0030 (calibration phases)
