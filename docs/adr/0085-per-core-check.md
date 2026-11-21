# ADR 0085: The per-core check: the degraded core is sound with turbo off, and what follows

Date: 2026-11-21

## Context

One P-core of the measuring PC is degraded (ADR 0002, ADR 0052). ADR 0084 planned a check of
every P-core before the v3 build, and fixed its rule in advance: the eight P-cores stay whatever
times the check shows, and a core leaves the mask only on a wrong checksum or a crash.

The check ran on 2026-11-21 on commit `cb4e02dc`. Its data are in `data/checks/core-check/`.

## Decision

**What was found.**

- **Which core.** The degraded core is the seventh P-core (`core_id` 24): logical CPUs 12 and
  13 with SMT on, CPU 12 of the measured mask. "Core 6" in ADR 0052 is its index among the
  P-cores, not CPU 6.
- **With turbo on it fails.** As the PC was found (turbo on, SMT on), the analysis tests crashed
  with a segmentation fault in 17 of 18 runs pinned to CPUs 12 and 13, and in 0 of 28 runs
  pinned elsewhere. The kernel placed every crash on CPU 12 or 13.
- **With turbo off it does not.** After `make env-setup` the same tests passed 30 of 30 times on
  CPU 12.
- **With turbo off it is as fast as the others.** The native filter at one thread, 8192x8192,
  pinned to one P-core at a time, 10 runs per core in rotating order:

  | CPU | Median (ms) | Against all runs |
  |---|---|---|
  | 0 | 22.53 | 1.004 |
  | 2 | 22.41 | 0.999 |
  | 4 | 22.43 | 0.999 |
  | 6 | 22.42 | 0.999 |
  | 8 | 22.42 | 0.999 |
  | 10 | 22.53 | 1.004 |
  | 12 | 22.44 | 1.000 |
  | 14 | 22.44 | 1.000 |

  All 80 runs gave the checksum of the v2 campaign for this input, and the slowest of the 800
  measured iterations took 22.9 ms.

**What is decided.**

1. **CPU 12 stays in the mask**, by the rule of ADR 0084: no wrong checksum and no crash at the
   measuring conditions.
2. **The frequency filter of ADR 0084 is dropped.** The sample taken after a run read between
   1154 and 3201 MHz on cores that had just run at full speed, so it does not tell a slow core
   from one that was read while going idle. The busy time per core works (3.03 s on the pinned
   core in every run) and is what the exploratory split of the one-thread times uses. `khzBefore`
   and `khzAfter` stay recorded and are not used.
3. **The measured build is made with turbo off, and twice.** With turbo on, any process that is
   not pinned can land on the failing core, the compiler included, and a failing core can
   compute wrongly without crashing. Three builds from scratch of this commit gave the same
   digests for the native runner, the WASM module and the JavaScript glue, so the build is
   reproducible: `measured/v3` is built twice from scratch and tagged only if the digests agree.
4. **Tests and analysis on this PC run after `make env-setup`**, for the same reason.

## Consequences

- **The reading of the slow runs in ADR 0077 loses its support.** Five filter runs of the v2
  campaign at one thread are 1.21 times their configuration's median: the three native ones
  took 27.2 to 27.3 ms against a median of 22.57 ms. ADR 0077 and ADR 0080 note that this fits the degraded core running at about
  2.6 GHz. Pinned to that core, the filter took 22.44 ms, and no iteration on any core passed
  22.9 ms. The slow runs are therefore not explained by a core that is slow by itself. What
  differs in a campaign is that the process may use all eight cores and the kernel may move it
  during a run; whether the slow runs are the ones that moved is what the busy time per core
  of the v3 runs can show. It stays open until then.
- The v2 campaigns ran with turbo off and passed their checksum and validation checks (ADR 0079),
  which agrees with what was found here. That the v2 binaries were built with turbo off was not
  recorded; their digests cannot be rebuilt (ADR 0080).
- The kernel is `7.0.0-43`, one update after the `7.0.0-42` of the v2 campaigns. The other host
  facts that `make env-setup` leaves alone are the same before and after it, and are now on file
  (`host-as-found.json`, `host-prepared.json`). The v3 campaigns must all run on one kernel.
- The check says the core is sound for these workloads on this day. A core that degrades further
  would show as a crash or a checksum conflict, which every campaign already stops on or reports.

## Status

Accepted; amends ADR 0084 (the frequency filter, the build) and the reading of the slow runs in
ADR 0077 and ADR 0080
