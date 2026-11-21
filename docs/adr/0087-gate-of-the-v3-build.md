# ADR 0087: The gate of the v3 build: one cell fails the drift criterion twice, and what it is

Date: 2026-11-21

## Context

ADR 0084 put a gate before the v3 campaigns: the cells whose code changed and the filter, three
runs each at the real size, checked on four criteria. It also fixed how a failure is read: the
gate is run once more, whole, with another seed, and the same cell failing twice stops the
session for a decision recorded before the main campaign starts.

The gate ran on 2026-11-21 on `measured/v3` (commit `ac65af6a`, the binaries of
`data/sessions/v3/build/digests.txt`), and then a second time. The runs are in
`data/checks/gate-v3` and `data/checks/gate2-v3`. They are never results.

## Decision

**What the two gates found.**

| Criterion | gate-v3 | gate2-v3 |
|---|---|---|
| Runs done, failed, excluded | 135, 0, 0 | 135, 0, 0 |
| Outputs across environments, thread counts and each sequential reference with its parallel workloads | agree | agree |
| Every timed sample at least 100 times the clock resolution | yes | yes |
| First three measured iterations within 5 % of the last three | 44 of 45 cells | 44 of 45 cells |

The cell that fails is the same both times: Firefox, local histogram, k = 1, N = 8, with a ratio
of 1.052 and then 1.077.

**What that cell does.** In every one of its six runs, one or two of the measured iterations 0
to 2 take 21 to 22 ms and the others 19.7 ms. The 71 warm-up iterations before them show nothing
of the kind. This is not new in v3. In the main campaign of `measured/v2`, the same cell has a
measured iteration more than 5 % above the run's median at index 1 in 16 of its 30 runs and at
index 2 in 20 of them, and none in the warm-up; its ratio over 30 runs is 1.03, under the gate's
limit only because 30 runs dilute it. No other cell of that campaign reaches 1.03. Chrome and
native show nothing at those indices in this cell. The filter in Firefox at N = 8 has a weaker
form of it (index 1 and 2 in 7 and 6 of 30 runs, index 9 in 15).

So it is a property of Firefox on this cell, at a fixed place in the run and not at the end of a
warm-up that was too short: a longer warm-up of the same kind would not remove it, since 71
iterations do not.

**What it does to the value that is analysed.** The unit of analysis is the run, summarized by
the median of its ten measured iterations (ADR 0037). One or two slow iterations out of ten do
not move a median: in the six gate runs the run value is 1.000 to 1.0015 times the value taken
from iterations 3 to 9 alone, and over the 30 runs of v2 it is 1.001 times.

**What is decided.**

1. **The campaigns start with the parameters as they are.** No warm-up length, iteration count
   or criterion changes. The cell is declared with what was measured here: one or two slow
   iterations among the first three measured ones in Firefox, an effect of about 0.1 % on the
   run value. The alternatives were to look for the cause first, which costs hours and does not
   change the effect, and to change the measurement (drop the first iterations, lengthen the
   measured phase), which would alter the analysis plan after seeing data.
2. **The gate is recorded as failed on one criterion in one cell, twice.** It is not turned
   into a pass. What lets the session go on is this record, written before the main campaign
   starts, as ADR 0084 asks.
3. **The assistant is kept running during the v3 campaigns** (`QUIET_KEEP_CLAUDE=1`, the option
   of ADR 0070), where the v2 campaigns and the two gates stopped it. Stopping it also freezes
   every terminal it runs in for the whole campaign, 14 hours for the main one. The reason ADR
   0070 gave for stopping it stands, so the rule that replaces the stop is: while a campaign
   runs, no command is started on the PC, by the assistant or by hand; the assistant only waits
   for the campaign to end. Every run still records the CPU time that other processes used on
   the measured cores, and the plan's threshold excludes a run that was disturbed (ADR 0051).
   What that record cannot see is work on the other cores that shares the cache, which is why
   the rule is needed.

## Consequences

- The gate did its work: it stopped the session on a cell worth looking at, and the look showed
  a behaviour that v2 already had and nobody had seen.
- The gate's drift criterion compares medians of three iterations, which one slow iteration in
  three runs can move. The data check of a campaign uses the same ratio over 30 runs. Both are
  kept as they are; the criterion is not changed after seeing the data.
- Why Firefox does this at those iterations is not established.

## Status

Accepted; amends ADR 0070 for the v3 campaigns (the assistant is kept running, under a no-command rule)
