# ADR 0052: Design of the extra experiments

Date: 2026-11-07

## Context

With the main campaign done, there was room for optional extra experiments. They are not part
of RQ1 or RQ2; they test explanations for what the main campaign showed and probe its limits.
From the planned list of extras, the author chose to run extras 1 to 6:

1. **private atomics**: atomic counters that no other thread touches;
2. **an inspection of Chrome's atomic code**, to test the hypothesis of ADR 0049;
3. **a parallel sort**, a workload that allocates memory;
4. **weak scaling**, where the input grows with N;
5. **false sharing**, with counters packed into shared cache lines;
6. **SIMD**, builds with wider or no vector instructions.

Three were not run:

- **Turbo on** is impossible: core 6 of the PC is degraded at high frequencies.
- **A P+E campaign** (P-cores plus E-cores, the slower efficiency cores) adds little after the
  P versus P+E pilot of ADR 0045. (ADR 0059 later ran it anyway.)
- **A replication on the Mac** would break the rule that numbers measured on the Mac are never
  reported as results.

## Decision

Agreed with the author on 2026-11-07: the design below, with 30 runs per configuration as in
the main campaign.

- **Status of the results.** The extras are exploratory: outside the family of 10 primary
  contrasts of the analysis plan (ADR 0037), reported with 95 % intervals (no multiple-testing
  correction), with 30 runs per configuration and the same machine state, quiet mode, start
  delay and warm-up rules as the main campaign.
- **New workloads.** They are selected at run time (not by separate builds), so that each can
  share one interleaved campaign with its controls:
  - `hist-atomic-private` (`bench/src/workloads/histogram/extras/private.rs`): every Rayon
    thread updates its own table of padded atomic counters, allocated in `prepare` outside the
    timed region and chosen by `rayon::current_thread_index`. The ladder local counters, private
    atomics, shared atomics at the same k separates the cost of the atomic instruction itself
    (private versus local) from the cost of contention (shared versus private).
  - `hist-atomic-packed` (`bench/src/workloads/histogram/extras/packed.rs`): the 256 counters
    are contiguous `AtomicU64` values, eight per 64-byte line. This is the false-sharing level
    next to the padded `hist-atomic`.
  - `sort` (`bench/src/workloads/extras/sort.rs`): Rayon's stable `par_sort` on the image's
    pixels read as little-endian `u32` keys. It is a recursive merge sort that allocates its
    buffer, which exercises WASM's default allocator and its global lock. The keys are restored
    in `prepare`, and the checksum is that of the sorted output. `sort-unstable`
    (`par_sort_unstable`, in place, no allocation) is its control: the gap between the two
    separates the allocator's cost from the sort's own synchronisation.
- **Weak scaling** gets its own campaign, because the analysis keys a configuration by workload
  and N, not by input size. A spec field `heightPerThread` sets the image height to that value
  times N: 8192 wide and 1024 rows per thread, which is the per-thread work of the main campaign
  at N = 8. T1 / TN is then the weak-scaling efficiency, ideally 1.
- **SIMD** needs different builds (native `target-cpu=native` with AVX2, native without SIMD,
  WASM without `simd128`), so it runs as separate campaigns of the filter, one per build, with
  the drift between them stated.
- **The inspection of Chrome's atomic code** records `perf` with V8's `--perf-prof` jitdump
  (a file in which V8 writes the machine code it generates) on a `hist-atomic` run and
  annotates the hot loop, to test the hypothesis of ADR 0049.
- The browser correctness check (`harness.browser_check`, ADR 0024) checks the new workloads in
  CI against native (108 browser runs match).

## Consequences

- Each extra gets its own result ADR with its data.
- The private and packed variants compute the same histogram as the others, so their checksums
  are checked against the local and shared variants in the unit tests.

## Status

Accepted
