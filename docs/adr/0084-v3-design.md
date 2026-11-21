# ADR 0084: The v3 build and its campaigns: what changes, what is asked and how the session runs

Date: 2026-11-21

## Context

The audits of 2026-11-20 found no reason to measure again: the campaigns of `measured/v2` are
valid for what they claim (ADR 0079), and what they cannot establish is declared (ADR 0080).
Some of those declared items are questions that a new build and a few more recorded facts would
answer instead of declaring:

- **The speedup has no sequential reference.** It is relative to a pool of one thread, not to
  code without Rayon (ADR 0080, ADR 0082).
- **The two histograms do not split their work the same way.** Only the local histogram goes
  through the grain control (`with_max_len`); the atomic one does not (ADR 0078, ADR 0080).
- **The slow runs at N = 1 have no established cause.** Five filter runs are 1.21 times their
  configuration's median, which fits the degraded core 6 (ADR 0052) running below 3.2 GHz, but
  no run records the frequency or the core it ran on (ADR 0077).
- **The measured compiler tier is unknown**, and in Chrome the first warm-up iteration of the
  atomic histogram is faster than every measured one (ADR 0072, ADR 0080).
- **The efficiency dip at N = 6 and 7** has two candidate causes, thread placement and Rayon's
  splitting in powers of two, and no data separates them (ADR 0080).
- **Memory is sampled before the warm-up and after the last iteration**, so the data cannot
  show that the first touch of the buffers ends inside the warm-up.

The paper is due on 2026-12-02. The decision is to build `measured/v3`, run every campaign again
on it and report only v3, so that the paper describes one build (ADR 0062).

The results of v2 are known. v3 is therefore a replication with corrections, not a blind
experiment, and the rules below are fixed before any v3 run exists so that no choice can follow
the numbers.

## Decision

### 1. The build `measured/v3`

Changes in `bench/`. None is an optimization. Each one goes in its own PR with the output of
`scripts/codegen_diff.sh measured/v2`, and ADR 0086 (the v3 build) will list the hot functions
that changed.

1. **Sequential workloads `filter-seq` and `hist-seq`.** The same kernels (`blur_row`,
   `Histogram::record`) called from a plain loop, with no Rayon call in `run`. `hist-seq`
   counts into one plain table, as one task of the local histogram does, with no atomic. They
   run at N = 1 only.
2. **The atomic histogram takes the grain.** `AtomicHistogram::with_grain` builds its tasks with
   `Grain::tasks`, as the local histogram and the filter do. With a fixed grain both histograms
   get the same tasks. With the adaptive grain it must split as in v2, because
   `with_max_len(usize::MAX)` is Rayon's default: a test counts the tasks with and without the
   call, and the codegen diff says whether the atomic loop changed. This touches the numerator
   of the RQ2 ratio, so ADR 0086 reports both checks; whatever they show, v3's ratios are never
   compared number by number with v2's (section 6).
3. **The memory size before the measured phase is written.** `MemoryTracker` already samples it
   for its growth check; it becomes a third recorded value, next to the two that exist. No new
   sample is taken, so nothing is added between iterations.
4. **`pitch` and `Palette::Consecutive` are removed.** No campaign used them. This is the last
   change and the one to drop if time is short: it buys no measurement, only less code.

Not changed: the timed region, the kernels' arithmetic, the checksums, the compiler, the flags,
the crates (`Cargo.lock`), the browsers' versions, the image size, the repetitions, the
iterations and the warm-up lengths, unless the gate of section 4 fails.

The calibration stays at 20 samples. More samples would not help where it is weak: Firefox's
20 us clock reads the warm fork-join as 0 at N <= 4 (ADR 0076), which is a resolution limit, not
a sample-size one. It stays declared.

### 2. What the harness records and controls (no effect on the build)

1. **Per run, for every measured CPU: its frequency before and after, and its busy time.** From
   `scaling_cur_freq` and the per-CPU lines of `/proc/stat`. The busy time says on which cores
   a run worked. The frequency is two point samples, not the frequency during the timed
   iterations: a core that slows down and recovers inside a run is not seen. The kernel's
   figure is the average over a CPU's last scheduler tick, so the sample after the run is
   recent for the cores that worked, and the sample before it, taken on idle cores, is old and
   is recorded only for completeness.
2. **Engine arms.** A spec may list named arms, each a set of Chrome `--js-flags` and Firefox
   preferences. Arms are a dimension of the plan, so they interleave like everything else, and
   every run records its arm. The default arm sets nothing; every campaign but the tier one
   uses only it.
3. **`MEASURED`.** The make targets read `data/raw/*-$(MEASURED)` and write
   `data/tables/*-$(MEASURED)`. `make tables-check MEASURED=v2` must still reproduce the
   committed v2 tables after this refactor, which shows the targets only changed names.
4. **Specs `*-v3.json`**, new files next to the v2 ones.

### 3. The campaigns

The analysis plan of ADR 0037 is unchanged: the same ten primary contrasts, exclusions (D7),
Holm and Bonferroni corrections, bootstrap and seed. Everything new is descriptive or
exploratory and is labelled as such.

| Campaign | Change from v2 | Kind |
|---|---|---|
| main | plus `filter-seq` and `hist-seq` at k in {1, 4, 16, 256}, N = 1 | primary; the sequential cells are descriptive |
| tier (new) | three arms per browser: default, baseline compiler only, optimizing compiler only; the filter and both histograms at k = 1, at N = 1 and 8, so that each arm gives the filter's speedup and the RQ2 ratio at k = 1 (first written with the local histogram at k = 256, which gave no ratio with the atomic one at k = 1) | exploratory |
| grain | the atomic histogram added to the 8192x8192 sweep (the 1024x1024 one needs passes, which its counters do not allow); a separate campaign for the local histogram at k = 16, N = 1, 6, 7 and 8, with the adaptive split and two fixed grains | exploratory |
| perf counters | plus the filter and the local histogram at k = 256, N = 1 and 8, with cycles, instructions and two cache events per pixel (last-level and L2 misses; a third makes the P-cores multiplex) | exploratory |
| cutoff, extras, weak, SIMD, hybrid | same design as v2 | exploratory |

The exploratory campaigns run in this order, so that what is dropped for lack of time is dropped
from the end. Estimated machine time for all of them is 55 to 60 hours.

### 4. How the session runs

The make targets are the entry point of a runner with numbered, resumable steps: each step
writes its log and a done mark in a session folder, a failed step stops the session, and the
next call continues from it. The steps:

1. **Host state**, captured before anything is changed (ADR 0083).
2. **Environment** set up and checked; tests; `make quick`.
3. **Per-core check.** The native filter at N = 1, pinned to one P-core at a time, 10 runs per
   core, with the checksum and the core's frequency read in every run. Its runs are never
   results. It also tests the frequency sample itself: each run is pinned, so the core that
   worked is known, and its sample after the run must read near 3.2 GHz on the cores that give
   normal times. If it reads as idle instead, the sample is not usable, the frequency filter
   of section 6 is dropped, and the split of the one-thread times by core, which needs only
   the busy time, is the check that remains.
4. **Build**, with the digests stored, and the tag `measured/v3`.
5. **Gate.** The cells whose code changed (both histograms at k = 1 and 256, the sequential
   workloads) and the filter as control, at N = 1 and 8, three environments, 3 runs, real
   sizes, strict validation. Its runs are never results. It passes when, in every cell:
   - the checksums agree across the three environments and both N;
   - every timed sample is at least 100 times the recorded clock resolution (the clock factor
     of ADR 0041);
   - the median of the first three measured iterations is within 5 % of the median of the last
     three (the measure of `analysis.iteration_drift`).

   Three runs per cell only catch a gross failure, such as a warm-up that no longer covers the
   compiler's tier change. The finer check is the data check of the main campaign (ADR 0051),
   whose findings are reported and never used to change a parameter after the campaign started.
6. **Main campaign**, then the exploratory ones, one per step.
7. **Engine code.** The machine code that each engine runs for `blur_interior` and for the
   atomic loop, captured once per browser on the v3 build (V8's jitdump, read by
   `analysis/extras/jitdump.py`; SpiderMonkey's if the pinned build exposes it). It is evidence
   for the discussion, not a measurement.
8. **Results:** every table and figure, then `make tables-check`.

There is no pilot: the parameters it would size are already decided. If the gate fails, the
session stops, and a parameter changes only through an ADR written before the main campaign
starts.

### 5. The open questions and what answers each

| Question left open | Since | What v3 brings | Expected |
|---|---|---|---|
| Is the speedup inflated by a slow one-thread pool? | ADR 0080 | the sequential workloads | answered |
| Do the histograms differ in more than their counters? | ADR 0078 | the same grain control in both | removed by construction |
| Are the slow N = 1 runs those of core 6? | ADR 0077 | frequency and busy time per core and run, the per-core check | answered |
| Which compiler tier is measured, and why is Chrome's first atomic iteration the fastest? | ADR 0072 | the tier campaign | answered |
| Is the dip at N = 6 and 7 placement or splitting? | ADR 0080 | fixed grains at N = 6, 7 and 8 | supported or not: a fixed grain also changes the number of tasks and their balance, so a dip that goes away supports splitting without isolating it |
| Does the first touch of the buffers end in the warm-up? | ADR 0080 | the memory size before the measured phase | answered |
| Why is the Firefox filter 1.33 times the native one at N = 1, and the scalar WASM further still? | ADR 0079, ADR 0058 | instructions and cycles per pixel, the engine code | where the time goes (more instructions or slower ones); the cause inside the compiler may stay open |
| Why is the local histogram superlinear in Firefox at k = 256 (8.47 at N = 8)? | ADR 0079 | cache misses per pixel at N = 1 and 8 | supported or not; not proven |
| Why does Chrome's atomic histogram at k = 1, N = 8 drift along a campaign (17 % from the first runs to the last)? | the v2 data check, noted in the working repository | whether it repeats, with the frequencies per run | observed again or not; the two frequency samples per run can suggest a cause, not establish one |
| Why does the filter step up between grains of 8 and 16 rows? | ADR 0067 | nothing new | stays declared |

### 6. Rules fixed before the data

- **Core 6.** The main campaign keeps the eight P-cores whatever times the per-core check shows,
  so that the design and the primary contrasts at N = 8 are those of ADR 0037. A core leaves the
  mask only if it gives a wrong checksum or crashes; that would change the largest N and needs
  its own ADR. A slower core is reported with its measured number. One exploratory check
  follows from what each run records: the one-thread times split by the core that did the
  work (the core with the most busy time in the run), and the filter's primary contrast with
  T1 taken only from runs whose core was, in the sample after the run, within 5 % of the
  3.2 GHz that the P-cores run at with turbo off. It says nothing at N = 8, where every run uses all eight
  cores: if core 6 is slow, it is slow in every N = 8 run of every environment, and that is
  declared, not corrected.
- **v3 or v2.** v3 is reported if, by 2026-11-27, the main campaign has every planned run, no
  checksum conflict, and every configuration of the primary contrasts keeps at least the 10
  runs the bootstrap needs (ADR 0037) after the exclusions, whose rules and thresholds are
  those of ADR 0037 and ADR 0051, unchanged. Otherwise the paper reports v2 and v3 is not used.
  These criteria read counts of runs, never a time, a speedup or a contrast, so the choice
  cannot follow the results. If v3 is reported and a conclusion differs from v2's, the paper
  says so.
- **No mixing.** No table, figure or comparison combines v2 and v3 runs (ADR 0062).

## Consequences

- The paper describes one build. The v2 data and specs leave this repository when v3 is adopted
  and stay in its history and in the working repository.
- The sequential cells add 450 runs to the main campaign (5 cells, 3 environments, 30 runs).
- The CSV gains one column, so the reader accepts v2 files without it for as long as v2 is kept.
- A campaign started on v2 cannot be continued on v3, and the reverse.
- The per-core check and the per-run frequencies settle whether the slow runs belong to core 6.
  They do not repair the core: runs at N = 8 use it in both builds.
- Still declared after v3: the idle and wake paths below the crate, that the inputs are uniform
  and larger than the caches, and the rows of section 5 that are not expected to be answered.
  Each exploratory answer is reported as exploratory: it supports an explanation, and no
  primary conclusion rests on it.
- The schedule has no slack for a failed main campaign: a second attempt takes the place of the
  first exploratory night.

## Status

Accepted; amended by ADR 0085 (the frequency filter is dropped, the build is made twice, and
"core 6" is CPU 12 of the mask)
