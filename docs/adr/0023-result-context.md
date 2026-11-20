# ADR 0023: Context recorded with every result

Date: 2026-10-17

## Context

A measured time is only interpretable and reproducible together with the state it was measured in:
the code version, the machine state and the launch settings. The study's design also depends on
machine settings that are easy to lose silently (turbo off and governor `performance`, ADR 0002;
the pinned browser versions, ADR 0021). If those are not recorded with each result, a run taken in
the wrong state cannot be told apart from a good one afterwards.

## Decision

- **Two files per run.** Every run has `<run>.csv` (ADR 0016) and `<run>.json`. The JSON holds the
  page metadata for browser runs (ADR 0019) plus these keys, added by the harness after the run
  (module `harness.context`):
  - `commit` (with `-dirty` if tracked files changed);
  - `cpuModel`;
  - `governor` (one value, or `mixed:...` across the mask);
  - `turbo` (`on`/`off` from `intel_pstate/no_turbo` or `cpufreq/boost`);
  - `kernel`, `os`, `environment`;
  - `browserVersion`, read from the launched binary with `--version` (`native` for native runs);
  - `cpuMask`, `headless`, `launchFlags` (the exact command) and `orderSeed`.
- **Who writes it.** Browser runs are annotated by the launcher once the result exists. Native runs
  go through the native wrapper (module `harness.native`), which runs the native runner (with
  `taskset` when a mask is given) and writes the same pair of files.
- **Missing values are explicit.** A value that cannot be read is stored as `unavailable`, never
  omitted.
- **Two levels of validation.**
  - `validate` checks that every key is present.
  - `validate(strict=True)`, used for campaign data, also rejects `unavailable`, empty or missing
    values for commit, CPU, governor, turbo, kernel, browser version, CPU mask and order seed, and
    the conditions the ADRs forbid: a `-dirty` commit, a governor other than `performance`
    (ADR 0002), turbo not `off` (ADR 0002), and a browser version other than the pinned one
    (ADR 0021).
- **Guards on the native side.** The CPU mask is validated before launching. The native wrapper
  times out (1 h by default) and only accepts output that starts with the shared CSV header, which
  a test keeps equal to the Rust constant.
- Harness modules run as `python3 -m harness.<module>`.

## Consequences

- Runs on the development Mac pass the basic check but not the strict one (no governor, turbo or
  `taskset` on macOS), which keeps Mac numbers out of campaign data.
- The orchestrator (ADR 0034) passes the order seed and validates strictly.

## Status

Accepted; amended by ADR 0025 (SMT and mask topology keys), ADR 0027 (provenance and drift keys,
failed-run records), ADR 0028 (shield and foreign CPU time), ADR 0029 (start delay) and ADR 0031
(exact version, leftover processes)
