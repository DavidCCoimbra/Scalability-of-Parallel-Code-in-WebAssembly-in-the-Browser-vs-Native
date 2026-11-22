# ADR 0088: What explains the results: the open questions, what tests each, and what it would show

Date: 2026-11-22

## Context

The main campaign of `measured/v3` gives the decisions of `measured/v2` on the ten primary
contrasts (5310 runs, none failed or excluded). The numbers hold. Several of the explanations
given for them are hypotheses, and the two main findings rest on such explanations: that the
filter scales better in Firefox than natively (RQ1), and that Chrome's shared atomic counters
cost more than native ones at k = 1 and less at k = 256 (RQ2).

The exploratory campaigns and probes that remain are ordered to test those explanations. This
record is written before they run: for each question it states the hypothesis, what tests it and
what the test would show if the hypothesis holds and if it does not. Without that, any outcome
can be read as support.

Nothing here is a primary result. The primary conclusions are those of the analysis plan
(ADR 0037); what follows supports or weakens an explanation of them.

## Decision

### 1. The questions

Times are geometric means of the run values of the v3 main campaign, 8192x8192.

| # | What is seen | Hypothesis | Tested by | If it holds | If it does not |
|---|---|---|---|---|---|
| 1 | The filter reaches an efficiency of 0.87 at N = 8, natively and in Chrome | At eight threads the filter is bound by memory, not by the cores | counters; cutoff; SIMD | cycles per pixel rise from N = 1 to 8 while instructions per pixel do not, with more cache misses per pixel; the efficiency is higher on images that fit the caches; the scalar build scales better and the AVX2 one worse | cycles per pixel stay the same from N = 1 to 8; the efficiency does not depend on the image size |
| 2 | Firefox scales better (0.917; the one rejected RQ1 contrast) with a slower thread (30.8 ms against 22.6 ms at N = 1) | Slower code per thread asks less of the shared memory | the same three, read together | efficiency against one-thread throughput falls on one curve for the three native builds and the three environments | Firefox sits off the curve of the native builds |
| 3 | At N = 1 the filter takes 1.36 times the native time in Firefox and 1.17 in Chrome | The engines' code for the same WASM is longer or slower | counters; engine code | more instructions per pixel, or as many with more cycles | - |
| 4 | The local histogram's efficiency dips at N = 6 and 7 and recovers at 8 | Rayon splits in powers of two, which leaves six or seven threads unevenly loaded | grain by threads | with a fixed grain the dip is smaller | the dip is the same with a fixed grain: placement, or something else |
| 5 | The local histogram's speedup passes 8 in Firefox (8.26 at k = 16, 8.48 at k = 256) | One thread pays for cache misses that eight threads share out | counters on the local histogram at k = 256 | fewer misses per pixel at N = 8 than at N = 1 in Firefox, and not natively | the misses per pixel are the same: unexplained |
| 6 | With one thread, Chrome's atomic histogram depends on k (698, 589, 488, 412 ms for k = 1, 4, 16, 256); native and Firefox do not (380 ms) | V8's optimizing compiler emits a load and a compare-and-swap, a chain through memory when the same counter is hit again | tier; engine code; native probe | the baseline arm does not depend on k; the native probe with a compare-and-swap does | the baseline arm depends on k as the default one does |
| 7 | At k = 256 and N = 8 Chrome's atomic histogram takes 210 ms against 415 ms natively | The same code: a load before the locked write changes how eight cores contend for 256 lines | tier at k = 256; native probe; counters | the baseline arm loses the advantage over native; the native probe with a compare-and-swap gains it | the baseline arm keeps the advantage: the cause is elsewhere in the engine |
| 8 | Firefox's RQ2 ratio is under 1 at k = 16 and 256 | It comes from the denominator: the local histogram scales more in Firefox (question 5), while its atomic times are the native ones (548 against 544 ms, 393 against 415 ms) | the decomposition of ADR 0078 | already shown by the times; its cause is question 5 | - |
| 9 | The atomic cells at k = 1 have wide intervals: runs fall on several time levels | The levels are states of contention that differ from run to run | counters per run | a run's time follows its count of contended line transfers | no relation: unexplained |

Two more observations get a look for free. If the slow early iterations of Firefox (ADR 0087)
are a change of compiler, they should be absent from the tier arms that have one compiler. And
the tier campaign says which compiler the campaigns measure: the default arm should equal the
optimizing one after the warm-up.

### 2. What is already known

- **The pool of one thread is a fair baseline.** The sequential references of the main campaign
  give T1 over the sequential time between 0.93 and 1.05 in every environment, so the relative
  speedup is not inflated by a slow pool. Natively the sequential histogram and one task of the
  local histogram are the same loop (`data/probes/engine-code`).
- **The slow one-thread runs of v2 did not come back.** No native filter run at N = 1 is above
  1.05 times the median. At N = 1 the kernel puts the work on CPU 12 or 14; CPU 12, the degraded
  core (ADR 0085), took 9 of the 30 native runs, none of them slow.
- **The buffers are first touched in the warm-up.** The native filter's memory grows by exactly
  65 536 KiB in the warm-up and by nothing in the measured phase at N = 1 and 2; with more
  threads it grows by a few KiB there, which are stack pages.
- **Question 6 has its first evidence, from the code** (`data/probes/engine-code`): for one
  atomic increment LLVM emits `lock incq`, V8's optimizing compiler a load, an add and a
  `lock cmpxchg` retried until it succeeds, and V8's baseline compiler a `lock xadd`. The tier
  campaign and the native probe test whether that difference is what the times show.
- **The filter is not the same instructions either**: SSE2 in legacy encoding natively, the same
  128-bit operations in VEX encoding in both of V8's compilers.

### 3. The order of what remains

Tier (with k = 256), counters, SIMD, cutoff, grain by threads, the grain sweeps, weak scaling,
and the extras only if time is left. The first five answer the questions above. The tier spec
gains the two histograms at k = 256 for question 7 (2100 runs).

Two probes run between campaigns, never during one: the engines' code (done for native, WASM and
Chrome) and a native program that counts into the shared table once with LLVM's increment and
once with V8's compare-and-swap, at k = 1 and 256, with 1 and 8 threads. Its prediction is in
the table: the compare-and-swap is slower at k = 1 and faster at k = 256 with eight threads.

### 4. What these tests can and cannot show

- The native probe changes one thing, the instructions of the increment, and looks at the
  effect: it is the test that can show a cause. The tier campaign changes the whole compiler,
  so every instruction of the loop changes with the increment; it shows that the effect follows
  the compiler and supports the explanation without isolating the compare-and-swap. Both cover
  the atomic counters (RQ2) only.
- The counters, the cutoff and the SIMD builds give correlations. Three sources that agree
  support the explanation of RQ1; none of them is an intervention on what the filter asks of
  the memory.
- Why SpiderMonkey compiles the filter and the local histogram as it does stays out of reach if
  its code cannot be read (ADR 0060). Questions 3 and 5 can then be answered only as far as the
  counters go.

## Consequences

- Each question ends as answered, supported or open, with the number behind it, in the result
  record of the campaign that tested it.
- The paper states each main finding at its level: a measured result, a proposed explanation,
  and the evidence for it. The RQ2 explanation may reach a cause; the RQ1 one is support.
- The data of the probes are in `data/probes/`, their code in `bench/probes/` and `scripts/`.
  They are never results.

## Status

Accepted; amends ADR 0084 (the order of the exploratory campaigns, the cells of the tier
campaign)
