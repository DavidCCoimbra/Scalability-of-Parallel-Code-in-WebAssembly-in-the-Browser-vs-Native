# ADR 0064: Cutoff campaign, with K passes per timed sample

Date: 2026-11-09

## Context

A parallel region is fork-join: the work is split among threads (fork), and the caller waits
until all of them finish (join). Starting and ending a region has a fixed cost, the fork-join
cost, that does not shrink with the work. When the work per region is small, that cost can eat
the gain from parallelism.

ADR 0041 fixed the image at 8192x8192 and left out any sequential cutoff (a size below which the
code would fall back to one thread). RQ1 is answered at one size, where the work per parallel
region dominates the fork-join cost. The size pilot and the paper show that the gap between the
environments grows at smaller sizes: on a 2048^2 image Chrome's filter speedup at N = 8 was 3.45
against native's 4.91, and an empty `rayon::broadcast` (a region that does no work) at N = 8
costs 110 us in Chrome and 60 us in Firefox against 7.5 us natively (warm medians of the main
campaign of the earlier build; ADR 0030 designs the calibration that measures them).

The question of this exploratory study (2026-11-09): per environment (native, Chrome, Firefox)
and per N in {1, 2, 4, 8}, below which image size does parallelizing stop paying? That is the
empirical sequential cutoff for granularity, the value a library would use to fall back to one
thread.

ADR 0041 already named the obstacle. Every timed sample must last at least 100 times the
coarsest clock resolution (Firefox's `performance.now()` resolves 20 us, so 2 ms per timed
sample). Small sizes run far below that floor: a 512^2 filter at N = 8 takes about 15 us
natively, so one call cannot be timed in the browser. ADR 0041 also named the way out: repeat
the work several times inside each timed sample.

Applying the cutoff inside the workloads (phase 2) is a later decision (ADR 0066) and is not
part of this ADR.

## Decision

The design was chosen on 2026-11-09 among the options considered: K passes inside the timed
sample (option A), N in {1, 2, 4, 8}, run overnight. The K per size was confirmed by a native
mini-pilot the same day (table below).

- **Passes.** A new run option `passes`, K >= 1, default 1. It is set in the query string, by the
  native `--passes` flag, in `CampaignSpec` (key `passes`, with a per-workload override like
  `warmup`) and in the stored `campaign.json`. Inside each timed iteration `Workload::run` is
  called K times between the two clock reads; `prepare` stays outside, once per sample. K is
  recorded in each run's context JSON as `passes`.
- **Time per pass.** The CSV format does not change. The `ns` of a warm-up or measured row is
  the time per pass: the elapsed time of the sample divided by K, rounded to the nearest ns
  (half up). With K = 1 it is the elapsed time, as before. The analysis multiplies by K where it
  needs the length of the timed sample (the clock check).
- **Checksum.** More than one pass is accepted only for the filter and the local histogram
  (`WorkloadKind::repeats_identically`, mirrored by `REPEATABLE_WORKLOADS` in the harness). Both
  recompute the same output from the input on every pass, so their checksum does not depend on
  K; the golden checksums are pinned for 1, 2 and 5 passes. The other workloads are refused
  (`ConfigError::Unsupported`, and by the spec) rather than redefined:
  - the atomic histograms add into counters that `prepare` resets once per sample, so with K
    passes they would hold K times the counts. That is deterministic but different from the
    local histogram's result, which breaks the check that the atomic and local checksums are
    equal;
  - a sort's second pass sorts already sorted data, which is a different workload.
- **Default path and build.** With K = 1 the run does what it did before, but the machine code
  of `measure` changes, so this is a new tagged build, and no campaign mixes it with older
  binaries (ADR 0062). `scripts/codegen_diff.sh main` found no workload kernel changed. Natively
  only `native::main` (into which `measure` is inlined) differs among the hot functions, and in
  the WASM package only `bench::run`; the raw WASM kernels differ only by a shifted function
  type index, with identical bodies.
- **Campaigns.** Five specs, `harness/campaigns/cutoff-<side>.json`, one per side in {512, 1024,
  2048, 4096, 8192}. Each is its own randomized campaign (seeds 2026110901 to 2026110905), run
  one after another (`make cutoff-campaigns`). These v1 specs are in `data/earlier/v1/specs`;
  their re-runs are those of ADR 0069 (v2) and of `cutoff-<side>-v3.json`.
  - Workloads: the filter (W = 15 warm-up iterations) and the local histogram at k = 256
    (W = 15, the main campaign's). Not k = 1, whose single-counter chain is a microarchitecture
    artefact (ADR 0060).
  - N in {1, 2, 4, 8}, 30 runs, 10 measured iterations, calibration 20, the P-core mask and
    harness CPUs of the main campaign, strict validation, headless, 3 s start delay, discarded
    first launches.
  - 5 sides x 3 environments x 2 workloads x 4 N x 30 = 3600 runs, plus 2 native controls x 2
    workloads x 4 N x 30 = 480 runs.
- **Comparison across sizes.** Sizes are compared only through speedups within a size. T1 and TN
  of a size come from the same campaign and the same K, so K and the campaign's own conditions
  cancel in T1 / TN. Absolute times are not compared across the five campaigns.
- **The two cutoffs.** Per environment, workload and N > 1, computed on the speedup T1 / TN of
  each size (geometric mean of run medians, 95 % bootstrap interval, as in `v0`, ADR 0036):
  - break-even: the side where the speedup reaches 1 (parallel as fast as sequential);
  - worth it: the side where the efficiency reaches `WORTH_IT_EFFICIENCY` = 0.5, that is the
    speedup reaches N / 2.

  Both are interpolated linearly in log side between the two neighbouring sizes where the curve
  crosses, walking down from the largest size. A curve above the threshold at every size, or
  under it at the largest size, is reported as outside the range. The work per region at the
  crossing, T1 per pass in us, is interpolated log-log. A side interval comes from the curves of
  the interval bounds: pointwise intervals, a rough guide.
- **Prediction.** A model TN = W / N + F, with W the work of one region (T1 per pass) and F the
  fork-join cost at N = 8 measured by the runs' calibration (ADR 0030): per run the median of
  its warm calls, per environment the median over the N = 8 runs of the five campaigns (the
  rule behind the paper's 110 / 60 / 7.5 us). F is a share s of TN when W = N F (1 / s - 1).
  - Primary (`RULE_OF_THUMB_SHARE`, s = 1 %): the common rule of thumb that the sequential work
    of a task should exceed the fork overhead by more than 100:1. W = 99 N F, so each thread's
    share W / N is 99 F: 5.94 ms natively, 87.1 ms in Chrome and 47.5 ms in Firefox with the
    paper's F.
  - Secondary (`LOOSE_SHARE`, s = 5 %, the first version of this ADR): W = 19 N F, 1.14 ms
    natively, 16.7 ms in Chrome and 9.1 ms in Firefox.

  Each W is turned into a side by scaling the largest size's T1 by the pixel count. With the
  main campaign's 8192^2 T1 at N = 1 (filter: 22.7, 26.8 and 30.7 ms, in the order native,
  Chrome, Firefox) the 1 % rule gives a filter side of about 4200 natively, 10200 in Firefox and
  14800 in Chrome, the last two above the largest measured size; the 5 % reading gives about
  1800, 4500 and 6500. These are indicative until the cutoff campaigns' own T1 and F replace
  them. The model's own break-even (W = F N / (N - 1)) and worth-it (W = N F) are written next
  to them, to compare with the measured cutoffs.

  Where the 1 % side lies above 8192^2 (the browsers), it cannot be checked against a measured
  crossing. There the comparison is made at the largest measured size: the paper reports the
  fork-join share of TN measured at 8192^2 against the 1 % target, and says that by the 100:1
  rule the browsers would need a larger region than this study measured.
- **Amendment, 2026-11-09.** The primary share moved from 5 % to 1 % to follow the 100:1 rule
  of thumb, before any cutoff data were analysed. It was not motivated by data. The 5 % reading
  stays as a secondary column. The times are those of the first cutoff campaigns, on build
  `measured/cutoff`, whose tables are in `data/earlier/v1/tables/cutoff` and whose runs are not
  in this repository (the later re-run of ADR 0069 is of 2026-11-10): their first run has `startedAt`
  2026-11-09T02:24 UTC, the amendment was committed at 02:31 UTC, seven minutes into the
  seven campaigns, and the results were first analysed in the commit of 08:31 UTC.
- **Phase 2 method.** Applying a cutoff inside the workloads (a later decision, ADR 0066) will
  follow the usual empirical method for a sequential threshold: make the threshold a parameter,
  sweep it over a range, plot the time against the threshold (expected U-shaped: too fine pays
  the fork-join, too coarse leaves cores idle) and pick the minimum per environment.
- **Outputs.** `make cutoff-results` runs `datacheck` and `v0` per side, then
  `analysis.cutoff`: `data/tables/cutoff/cutoff-table.csv`,
  `data/tables/cutoff/cutoff-estimates.csv`, `data/tables/cutoff/cutoff-model.csv` and
  `paper/figures/cutoff-speedup.pdf` (in the final repository, the v2 tables are under
  `data/tables/cutoff-v2/`).

### K per size

The specs use K = (8192 / side)^2, so that each timed sample covers 8192^2 pixels, the work of
one pass of the main campaign. A native mini-pilot on 2026-11-09 (P-core mask, N = 8, 5 measured
iterations, the fastest configuration of each side) confirmed that every sample clears the 2 ms
floor (100 times Firefox's 20 us resolution, ADR 0041). The browsers are slower than native per
pass, so their samples are longer.

| Side | K | Filter per pass | Filter sample | Local k256 per pass | Local sample |
|---|---|---|---|---|---|
| 512 | 256 | 25.6 us | 6.54 ms | 36.3 us | 9.28 ms |
| 1024 | 64 | 57.7 us | 3.69 ms | 70.2 us | 4.49 ms |
| 2048 | 16 | 187.0 us | 2.99 ms | 227.7 us | 3.64 ms |
| 4096 | 4 | 723.1 us | 2.89 ms | 839.2 us | 3.36 ms |
| 8192 | 1 | 3248.8 us | 3.25 ms | 3404.9 us | 3.40 ms |

The per-pass times already show the cutoff's shape natively: at 512^2, N = 8 takes 25.6 us per
pass for 1/256 of the 8192^2 work (3.25 ms / 256 = 12.7 us), so about half of it is fork-join
and scheduling.

### Control: does K change the time per pass?

Size and K change together (K = 256 at 512^2, 1 at 8192^2). So a small side is also measured as
many warm, cache-resident passes back to back, and a large one as one cold pass. To bound that
confound, two native-only control campaigns (`cutoff-control-512` and `cutoff-control-2048`) run
the same design with K = 1. Native is the only environment whose clock resolves one pass at
these sizes. The ratio of the time per pass at K = 1 to that at K = 256 or 16 is reported next
to the cutoff estimates. If it is far from 1, the estimates describe the back-to-back regime
only, and the paper says so.

The fork-join model's side extrapolates T1 per pixel from the 8192^2 reference. Small,
cache-resident sides run faster per pixel, so the predicted side is biased small. It is a model,
read against the measured crossing.

### Duration estimate

From the main campaign's logged run times (2026-11-07) of the same configurations at 8192^2:
Chrome 8.0 s (filter) and 4.3 s (local), Firefox 8.7 s and 4.9 s, native 4.7 s and 0.8 s. With
the planned K every timed sample has the main campaign's work, so the 8192 campaign takes about
120 x 31.4 s, 1.05 h. The smaller sides generate a smaller input and should be shorter, while the
browser launch and the 3 s delay stay. The five campaigns should take about 4 h, at most about
5.5 h (five times the 8192 campaign) plus the discarded first launches: one night.

## Consequences

- **What one pass sees.** K back-to-back passes change the state each pass starts from. The
  first pass of a sample wakes parked workers (cold fork-join); the next K - 1 passes find them
  still spinning (warm fork-join, ADR 0030), and the input stays in the cache (a 512^2 image is
  256 KB). The per-pass time is therefore an average over one cold and K - 1 warm fork-joins on
  a warm cache: it describes a region called repeatedly, not a single cold call. It favours the
  environments whose cold fork-join exceeds the warm one the most (the calibration's warm and
  cold samples show which), and the cutoffs are read with that caveat.
- **K is part of the size effect.** K differs between sizes, so the share of cold fork-joins
  (1 / K) does too. This is part of the size effect being measured and cannot be separated from
  it without a K sweep at a fixed size.
- **Exploratory.** The result is exploratory (ADR 0052): estimates with rough intervals, no
  test. It does not change the main campaign's design or numbers.
- **No pooling.** The 8192 campaign with K = 1 repeats two configurations of the main campaign
  on a new build; it is not pooled with it (ADR 0062).
- **Older data.** Older runs have no `passes` key. The harness lists it under `LATER_KEYS` (not
  required), and the analysis reads a missing key as one pass. Campaign specs without `passes`
  are stored and resumed exactly as before.

## Status

Accepted
