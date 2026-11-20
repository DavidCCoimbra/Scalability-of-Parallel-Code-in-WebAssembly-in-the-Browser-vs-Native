# ADR 0062: A readability refactor of the bench, limited to codegen-neutral changes

Date: 2026-11-08

## Context

A readability refactor of the whole repository was requested (PR #77): one type per file,
named constants with references to where their values come from, and a README with a Mermaid
flowchart per module.

`bench/` holds the measured code: the timed region, the workload kernels and the checksum. The
published numbers describe the machine code that this source compiled to. If a change alters
the machine code of the timed region or of the kernels ("codegen", the code the compiler
generates), measurements taken after it are no longer comparable with the campaigns already
reported, even if the source does the same thing. A refactor for readability must therefore not
change what is measured.

## Decision

- **Scope.** Only two classes of change are allowed:
  - (a) code outside the measured path;
  - (b) moves, renames and `const` names inside the measured path that leave the machine code
    unchanged.

  Rewriting loops, closures or generics in the measured path (class (c)) needs its own ADR and
  a new campaign.
- **Codegen check.** `scripts/codegen_diff.sh [BASE_REF]` builds the base and the head at the
  same path, so that paths embedded in the binary do not differ. It diffs the normalized
  instructions of the hot functions for the four native variants and the three WASM variants.
  For PR #77 it found 88/88 native and 89/89 WASM hot functions identical.
- **Golden checksums.** `bench/tests/golden_checksums.rs` pins the output checksum of every
  workload. They were computed on the code before the refactor, so the refactored code must
  produce the same outputs.
- **Layout.** Moving items into submodules changes the order in which rustc emits functions, so
  identical functions can land at different addresses. Native hot loops start 16 bytes lower
  modulo 64 (that is, at a different offset inside a 64-byte cache line); the avx2 variant is
  unchanged. To check that this does not change the times, an interleaved native A/B on the
  P-cores (`data/probes/refactor-ab.csv`, in the working repository) compared the old binary
  with the new one:
  - **Quiet session, 12 runs each:**
    - filter N = 8: new/old 0.996, 95 % CI [0.990, 1.001];
    - atomic histogram k = 1 N = 8: 1.025, CI [0.959, 1.094]. This CI is inconclusive at the
      scale of that configuration's run-to-run noise (770 to 965 ms in both binaries).
  - **First session, 6 runs each:** filter N = 1 and the local histogram at N = 1 and N = 8
    differ by 0.04 % or less, and the atomic histogram k = 256 N = 8 by 0.2 %.

## Consequences

- **No mixed builds.** No new campaign mixes binaries of the old layout with binaries of the new
  one. Every campaign is built from one commit and tagged, as before, so the published numbers
  stay reproducible from the `measured/*` tags.
- **A standing check.** Any later change in `bench/src` runs `scripts/codegen_diff.sh` against
  the last measured tag, and the PR says whether a hot function changed. ADR 0066 later relaxed
  the rule so that the measured path may change when an ADR records why, as a new tagged build.

## Status

Accepted
