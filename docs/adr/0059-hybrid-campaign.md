# ADR 0059: Hybrid P+E campaign

Date: 2026-11-08

## Context

The i9-14900KF is a hybrid CPU. The study measures on its 8 P-cores (performance cores) only
(ADR 0045). It also has 16 E-cores (efficiency cores, CPUs 16 to 31), which run at 2.4 GHz with
turbo off, against 3.2 GHz for the P-cores.

This extra asks how Rayon's work stealing copes with heterogeneous cores, natively and in the
browsers. In work stealing, an idle thread takes pending tasks from another thread's queue. With
more threads than P-cores, some threads run on slower cores; a fixed split of the work would
make everyone wait for them, while work stealing can move work to the faster cores. The P
versus P+E pilot of ADR 0045 only compared the two masks at N = 8, so it does not answer this.
ADR 0052 had first set this extra aside as adding little after that pilot; this ADR runs it
after all, as its own campaign.

## Decision

Decided on 2026-11-08:

- **Mask.** Every P-core plus 12 E-cores: `0,2,4,6,8,10,12,14,16-27` (20 CPUs, one per
  physical core). The harness, the server and the rest of the system stay on the last E-core
  cluster, `28-31`, so the shield of ADR 0045 still keeps them off the measured CPUs. Placement
  of the threads inside the mask is left to the kernel, as in the main campaign.
- **Spec field `hybrid`.** Strict validation normally refuses CPUs that are not P-cores. A
  campaign with `"hybrid": true` skips that check (in the run context and in the environment
  check) and requires instead that the mask holds every physical P-core. Every other strict
  check (turbo, governor, SMT, shield, pinned browsers, clean commit, escaped processes) is
  unchanged. `analysis.datacheck` reads the flag from `campaign.json`.
- **Workloads and N.** The filter (W = 15) and the local histogram at k = 1 (W = 71), the two
  workloads of the weak scaling campaign, at 8192^2 and N in {1, 8, 12, 16, 20}. N = 8 compares
  with the P-only main campaign; 12, 16 and 20 add 4, 8 and 12 E-core threads. 30 runs, 10
  measured iterations, 3 s start delay, quiet mode, discarded first launches, seed 20261112:
  900 runs.
- **Analysis.**
  - speedup T1 / TN within the campaign (T1 may run on either core type, as the kernel
    decides);
  - the time at N > 8 over the P-only time at N = 8 of the main campaign;
  - the browser / native ratio per N.

  The ideal speedup is not N. If an E-core did 0.75 of a P-core's work per second (an estimate
  from the clocks only, 2.4 / 3.2 GHz, not measured), the most that E extra threads could gain
  over N = 8 is about (8 + 0.75 x E) / 8.

## Consequences

- The result is exploratory (ADR 0052). It says whether the browsers' thread pools use the
  E-cores as well as native Rayon does, not why.
- The baseline at N = 8 comes from another campaign; ADR 0058 states the same caveat for SIMD.
- The iteration drift check of ADR 0056 is run on this campaign too.

## Status

Accepted
