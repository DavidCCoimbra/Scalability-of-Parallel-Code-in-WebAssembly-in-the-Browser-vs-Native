# ADR 0075: The pad64 feature is removed from the bench

Date: 2026-11-21

## Context

ADR 0008 padded every shared atomic counter to its own 128-byte cache line and added a cargo
feature, `pad64`, that padded to 64 bytes instead, so that the two paddings could be compared.
ADR 0049 ran that comparison in a pilot (10 runs per cell, pad64 against pad128) and kept 128
bytes; no difference beyond drift was detected. No campaign of the final build, `measured/v2`,
was built with `pad64`: every recorded run has an empty `build.features` list.

The feature still cost a second clippy, test and WASM build in CI, a second line in
`make test-rust`, two build variants in `scripts/codegen_diff.sh`, and `cfg` branches in the
counter type and in the build information. Code that no measured configuration exercises is
dead weight in a repository whose point is to hold what the data came from.

Removing it changes `bench/`, the measured crate, so ADR 0062 applies: the change is allowed
only if the machine code of the hot functions is unchanged, and the check is recorded here.

## Decision

- `PaddedCounter` is `repr(align(128))` unconditionally and `CACHE_LINE_BYTES` is 128; the
  `pad64` feature, its CI steps, its `make test-rust` line and its `codegen_diff.sh` variants are
  removed.
- `BuildInfo.features` stays, always empty, so the `build` block of a run keeps the shape of the
  recorded campaigns (`"features": []`).
- Codegen check against `main` before the change (`scripts/codegen_diff.sh main`, 2026-11-21):
  - WASM default: 1514 of 1514 functions identical (87 of 87 hot);
  - WASM scalar: 1513 of 1514 identical, the one difference being `__wasm_init_memory`, which
    writes the data segment and is not timed (87 of 87 hot identical);
  - native default, avx2 and scalar: 88 of 88 hot functions identical (compared on an arm64
    host with addresses normalized by hand, because the script's normalization covers x86-64;
    the x86-64 run on the measuring PC is pending, see the final map).

## Consequences

- The data of `measured/v2` stays valid for this code: the hot functions compile to the same
  machine code.
- The 64-byte comparison of ADR 0049 can no longer be rebuilt from this repository; its record
  and numbers stay in ADR 0049, and the pilot data in `data/earlier/pilot`.
- `pitch` and `Palette::Consecutive`, the other options no campaign uses, are decided
  separately: `pitch` stays, because the filter kernel chunks by `pitch()` and its removal is
  not certainly codegen-neutral.

## Status

Accepted; amends ADR 0008 and ADR 0049
