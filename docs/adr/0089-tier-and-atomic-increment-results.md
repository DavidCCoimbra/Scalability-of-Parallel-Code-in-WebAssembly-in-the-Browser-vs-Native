# ADR 0089: What the tier campaign and the atomic increment probe show (questions 6 and 7)

Date: 2026-11-22

## Context

ADR 0088 asked why Chrome's shared atomic histogram is slower than the native one at k = 1 and
faster at k = 256, and wrote down what two tests would show if the cause is the code V8's
optimizing compiler emits for one increment: the campaign `tier-v3` (each browser as shipped,
with its baseline compiler only and with its optimizing compiler only) and a native probe that
changes only the instructions of the increment. Both ran on 2026-11-22.

- `tier-v3`: 2100 runs on `measured/v3`, none failed, missing or excluded, no checksum conflict,
  no configuration trending with the execution order. Data: `data/raw/tier-v3`.
- The probe: `data/probes/atomic-increment`, with its own README.

Times below are geometric means of the run values (30 runs per cell), in ms, at 8192x8192. The
table with intervals comes with the analysis command for the engine arms; nothing here is a
primary result.

## Decision

### 1. The campaigns measure the optimizing compiler

In every cell of both browsers the arm as shipped and the optimizing-only arm give the same
time after the warm-up (Chrome's atomic histogram at k = 1 with one thread: 697.97 and
697.98 ms). The baseline-only arm differs everywhere.

### 2. Question 6: with one thread, Chrome's atomic time depends on k. Answered.

| Atomic histogram, one thread | k = 1 | k = 256 |
|---|---|---|
| native | 379.6 | 379.6 |
| Chrome, optimizing compiler | 698.0 | 411.9 |
| Chrome, baseline compiler | 419.1 | 402.7 |
| Firefox, optimizing compiler | 379.7 | 379.8 |
| Firefox, baseline compiler | 411.3 | 384.0 |
| native probe, `lock inc` | 379.9 | 379.8 |
| native probe, compare-and-swap | 677.1 | 408.2 |

- The dependence on k follows V8's optimizing compiler: with its baseline compiler the time is
  almost the same at k = 1 and 256, as predicted.
- The native probe, in which only the increment changes, gives Chrome's times with the
  compare-and-swap (677 and 408 ms against 698 and 412 ms) and the native times with the locked
  increment. The code is in `data/probes/engine-code`: a load, an add and a `lock cmpxchg` back
  to the load in V8's optimizing code, a `lock xadd` in its baseline code, a `lock inc` natively.
- The RQ2 effect at k = 1 (ADR 0026) follows: 2.17 with the optimizing compiler, 1.04 with the
  baseline one. With its baseline compiler Chrome pays for the shared counter at k = 1 what
  native code pays.

The tier arms change the whole compiler, so by themselves they show that the effect follows the
compiler. The probe isolates the increment. Together: the cost of Chrome's atomic histogram at
k = 1 is the compare-and-swap sequence of V8's optimizing compiler.

### 3. Question 7: at k = 256 with eight threads Chrome is faster than native. Answered for the sequence, not for the mechanism.

| Atomic histogram, k = 256, eight threads | Time |
|---|---|
| Chrome, optimizing compiler | 210.3 |
| native probe, compare-and-swap | 239.5 |
| Chrome, baseline compiler | 270.1 |
| Firefox, baseline compiler | 326.5 |
| native probe, `lock xadd` with the baseline compiler's checks | 348.8 |
| Firefox, optimizing compiler | 393.1 |
| native probe, `lock inc` with those checks | 401.6 |
| native | 414.1 |
| native probe, `lock inc` | 415.0 |
| native probe, `lock xadd` | 437.2 |

- **The probe's prediction held.** With the compare-and-swap the native program takes 240 ms
  where the locked increment takes 415 ms: the sequence is enough to produce Chrome's advantage
  on this CPU.
- **The tier campaign's prediction held only in part.** The baseline arm was expected to lose
  the advantage over native. It keeps most of it (270 ms), and Firefox's baseline compiler gains
  one that its optimizing compiler does not have (327 against 393 ms). The probe shows the same
  for the baseline sequence: the exchange-and-add behind an alignment and a bounds check takes
  349 ms, while the checks alone (402 ms) and the exchange-and-add alone (437 ms) do not gain.
- So at k = 256 with eight threads the time is not ordered by how fast one increment is: the
  sequences that do more around the locked write finish sooner. Why is not shown. The
  explanation offered, and not tested, is that eight cores hitting 256 lines at random spend
  their time moving lines between caches, and a sequence that reads the line first or does other
  work between two locked writes asks for exclusive ownership less often.

The RQ2 effect at k = 256 does not read this cleanly for the baseline arm (0.32 in Chrome, 0.40
in Firefox, against 0.42 and 0.80 with the optimizing compilers): the baseline compilers' local
histogram is much slower (7.0 against 4.2 ms in Chrome at eight threads), and the effect divides
by it. The times above are the reading.

### 4. What else the arms show

- **Chrome's first iteration.** In the arm as shipped, the first warm-up iteration of the atomic
  histogram at k = 1 is 0.949 times the steady value; with one compiler only it is 1.00 and
  1.01. A run as shipped starts in baseline code, which is the faster one for this loop.
- **Firefox's slow early iterations (ADR 0087)** are not a change of compiler. In the local
  histogram at k = 1 with eight threads they are in 27 of 30 runs as shipped, in 27 of 30 with
  the optimizing compiler only and in 1 of 30 with the baseline compiler only. They come with
  the optimizing compiler's code; what they are is still not known.
- **The filter scales slightly better with the slower compiler in both browsers** (speedup at
  eight threads: Chrome 7.09 with the baseline compiler against 6.83 with the optimizing one,
  Firefox 7.51 against 7.44), the direction that question 2 of ADR 0088 expects from slower code
  per thread. It is one observation among those that question needs.

## Consequences

- Question 6 of ADR 0088 is answered and question 7 is answered as far as the sequence goes:
  the paper can say that the RQ2 effect in Chrome, in both directions, is reproduced natively by
  the increment sequence of V8's optimizing compiler, and that the mechanism at k = 256 is a
  proposed one.
- The RQ2 finding is then about a compiler's choice of instructions for an atomic add, not
  about WebAssembly threads as such: with another sequence the same engine shows no penalty at
  k = 1.
- The prediction that failed in part is kept as such.

## Status

Accepted
