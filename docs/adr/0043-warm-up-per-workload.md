# ADR 0043: Warm-up W per workload, the same in every environment

Date: 2026-11-07

## Context

Each run first executes W warm-up iterations that are not analysed, then the measured ones (ADR
0005). W must be large enough that the measured iterations are in a steady state: in the browser
the WASM code starts in a baseline compiler and a hot function is later recompiled by an
optimizing compiler ("tier-up"). W was left to a pilot.

### The warm-up pilot

The warm-up pilot (`harness/campaigns/pilot-warmup.json`, in the working repository, 2026-11-06)
ran every campaign workload at 8192x8192 with no warm-up and 100 measured iterations, at N = 1 and
8, 2 runs per environment (108 runs, 0 failed). The cell that sets the largest W (Firefox
`hist-local` k = 1, N = 8) got 10 more runs (`pilot-warmup-ff-k1.json`), because its tier-up time
varies from run to run.

- **The first iteration is the most expensive everywhere**, natively too: the filter's first
  iteration takes 5x the steady state at N = 8, likely the first write to the output buffer. Most
  configurations are steady after 2 or 3 iterations; every `hist-atomic` configuration after at
  most 2.
- **Late tier-up in Firefox.** Firefox `hist-local` k = 1 at N = 8 runs about 15 % slower for its
  first 26 to 47 iterations (12 runs; about 0.5 to 1 s), consistent with a later tier-up of the
  hot function.
- **Fast start, slower steady state.** Firefox `hist-local` k = 4, 16 and 256 at N = 1 run 5 to
  10 % faster for their first 10 to 20 iterations, then settle 5 to 10 % slower.
- **Noise, not a trend.** Firefox `hist-local` at N = 8 (5 to 20 ms per iteration) varies by 10 to
  40 % from iteration to iteration through the whole run.
- **The planned rule fails on noise.** The rule planned before this pilot (a rolling median
  within 2 % until the end of the run) reads that noise as warm-up: it gives W = 85 for the native
  filter, which has no JIT compiler at all.
- **Clock.** No configuration is under the clock factor (ADR 0041): the closest is the Firefox
  filter at N = 8, at 208 times the resolution.

## Decision

Decided on 2026-11-07, before any campaign data. The author chose one W per workload, the same in
every environment, over a single W for everything. The rule's two safeguards (a short
first-iteration spike, and a run that never settles) and the 10 extra runs came from the code
review and were applied as recommended.

### Observed W of one run

- The observed W of a run is the first iteration whose next window of 10 iterations has its median
  within a tolerance of the steady state (the median of the second half of the run).
- It is also at least one past any iteration of the first window that is slower than every
  steady-state iteration and more than 2 % above the steady state. This catches a short
  first-iteration spike, which a window median would hide.
- The tolerance is the larger of 2 % and 1.5 times the largest window deviation inside the steady
  state, so noise is not read as warm-up.
- A run whose steady state deviates by more than 25 %, or with no settled window, never settles
  and stops the choice (`analysis/warmup.py`); none did.

### W of a workload

- A workload's W is 1.5 times the largest observed W over environments, thread counts and runs,
  and at least 5.
- The same W is used in native, Chrome and Firefox, so the environments compared within a workload
  get the same procedure.
- The values: filter 15; `hist-atomic` 5 for every k; `hist-local` k = 1: 71, k = 4: 21,
  k = 16: 15, k = 256: 15.
- A campaign spec can give a workload its own `warmup`, which overrides the campaign's
  (`harness/campaign.py`).
- The warm-up curves are plotted by `analysis/plot_warmup.py` (the paper's figures
  `warmup-n1.pdf` and `warmup-n8.pdf`), run through `uv` with matplotlib, which the rest of the
  analysis does not need.

## Consequences

- The alternative, a single W (71 everywhere), would cost about 20 more hours of campaign time,
  spent on `hist-atomic` iterations of up to 1.9 s that show no warm-up.
- W comes from N = 1 and 8 only. The thread count pilot (ADR 0044) checks it at N = 2, 4, 6 and 7,
  with W = 56 for the filter and `hist-local` and 5 for `hist-atomic`.
- Firefox's noise at N = 8 on short iterations is a matter for the number of runs (ADR 0047), not
  for W.

## Status

Accepted; amended by ADR 0048 (the slow first iterations of Firefox `hist-local` k = 1 at N = 8
may be browser start-up work rather than tier-up; W stays)
