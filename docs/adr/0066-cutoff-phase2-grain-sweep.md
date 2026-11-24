# ADR 0066: Cutoff phase 2, a grain-size sweep (U-curve)

Date: 2026-11-09

## Context

ADR 0065 measured where parallelizing a whole region stops paying (the size cutoff). The other
half of the question is inside one parallel region: how small may a task be before forking it
costs more than it saves? The size of a task is its grain.

The usual way to answer it is empirical: make the threshold a parameter, sweep it, plot the time
against the threshold and pick the minimum. The curve is expected to be U-shaped: too fine a
grain pays the fork-join cost per task, too coarse a grain leaves cores idle and the load
unbalanced. The common rule of thumb is sequential work per task at least 100 times the fork
cost.

Today the grain is fixed in the code. The filter hands Rayon one row per item, and Rayon's
adaptive splitting decides the task size; hist-local uses 64 KB chunks (`CHUNK_BYTES`). Neither
was chosen per environment. ADR 0065 suggests the best grain may differ, because the browsers'
fork-join costs 6 to 10 times native's (the calibration of the cutoff campaigns, ADR 0065
section 3).

## Decision

Phase 2 was approved on 2026-11-09. The same day the project's code-style rule on the measured
path was relaxed: the measured path may change when an ADR records why, checked with
`scripts/codegen_diff.sh`, as a new tagged build that no comparison mixes with older builds
(ADR 0062).

1. **Parameter.** A `grain` option, the same in all three environments: query string, native
   `--grain`, `WorkloadSpec` key `grain`, recorded in each run's context JSON as `grain`
   (`null` when absent). It applies to the filter and the local histogram only
   (`WorkloadKind::takes_grain`, `GRAIN_WORKLOADS` in the harness) and is refused elsewhere.
   - Absent (`Grain::Adaptive`): the code of every earlier campaign. Rayon splits adaptively
     (one row per item for the filter, 64 KB chunks for hist-local).
   - `grain = g` (`Grain::Fixed`): every task is exactly g rows (filter) or g KB (hist-local).
     The items are blocks of that size, and `with_max_len(1)` stops Rayon from merging them, so
     the task size is the grain and not a lower bound. This is a sequential cutoff: below the
     grain the work runs sequentially inside one task. The first draft of this ADR used
     `with_min_len`, which only bounds Rayon's split from below and would not show the fine side
     of the U.

   Hist-local with a fixed grain creates one 2 KB partial histogram per task and merges them, a
   cost that grows as the grain shrinks; it is part of what the sweep measures.
2. **Sweep.** Powers of two, plus the adaptive split as a reference:
   - filter: grain 1 to side / N rows;
   - hist-local: grain 1 to side^2 / N / 1024 KB.

   Two campaigns, `harness/campaigns/grain-1024.json` (18 workload entries) and
   `grain-8192.json` (27), each randomized on its own (seeds 2026110911 and 2026110912). These
   v1 specs are in `data/earlier/v1/specs`; they were run again on v2 (ADR 0069) and on v3
   (`grain-1024-v3.json`, `grain-8192-v3.json`). Both use N = 8 only, native, Chrome
   and Firefox, 30 runs, K = (8192 / side)^2 passes as in ADR 0064, and the rest of the cutoff
   campaign's settings: 45 x 3 x 30 = 4050 runs, about 4 hours.
3. **Codegen.** `scripts/codegen_diff.sh main` (2026-11-09):
   - The atomic, private, packed and sort kernels are identical, so the main campaign's RQ2
     numbers still describe the code in the repository.
   - The filter's and hist-local's Rayon helpers change (new fixed-grain monomorphs, that is,
     new compiled copies of the generic code). The adaptive filter helper shrinks from 1257 to
     555 bytes because `blur_row` is no longer inlined into it, and `bench::run` changes (2912
     to 2929 bytes). `blur_interior`, the SIMD kernel, is identical.
   - So the adaptive points of this campaign are not the main campaign's code: every point of
     the sweep, the adaptive one included, is measured on the new build (tag `measured/grain`).
   - Inside the build, the two arms run the same per-element code. In the native binary both
     filter helpers (adaptive and fixed) call the same out-of-line `blur_row`, which calls the
     same `blur_interior`. Hist-local's adaptive helper has the main build's size (1328 bytes),
     and the fixed one adds the `MaxLen` bookkeeping (1351). The U-curve therefore compares task
     sizes, not two codegens of the kernel.
   - The analysis refuses grain campaigns of different builds (`analysis/grain.py`,
     `same_build`).
4. **Analysis.** Per environment, workload and size:
   - the geometric mean of the run medians of the time per pass against the grain, with a 95 %
     bootstrap interval (the U-curve);
   - the grain at the minimum;
   - the flat region (grains whose interval overlaps the minimum's);
   - the adaptive split's time relative to the best grain.

   The question for the paper: is the best grain coarser in the browsers than natively, and by
   about the ratio of their fork-join costs? The 100:1 rule gives the prediction (sequential
   work per task at least 100 F).

## Consequences

- **What it answers.** It answers the threshold question with the standard empirical method,
  per environment, and gives web developers a concrete number (the grain) instead of a rule of
  thumb.
- **A new build.** It touches the measured path (`bench/`) of two workloads. The earlier
  campaigns stay valid for their own tagged builds, and the paper cites the tags.
- **Exploratory.** It is exploratory (ADR 0052), outside the 10 primary contrasts.
- **Results.** The results are in ADR 0067.
- **Fallback.** If time had run out before the paper, ADR 0065 would have stood on its own and
  this ADR would have been marked Rejected with the reason. It was carried out.

## Status

Accepted
