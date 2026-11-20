# ADR 0027: Provenance, drift context and failed-run records

Date: 2026-10-17

## Context

The review of the benchmark code once it was first complete (finding R7) found that the context of
ADR 0023 leaves out what the analysis needs for two things:

- **Detecting drift**, a slow change of the machine over a campaign that could line up with one
  environment and look like an environment effect. That needs when each run happened, its position
  in the interleaved order, and the machine load around it.
- **Proving that every environment ran the same code on the same input.** That needs which artifact
  was measured, how it was compiled, and which input was processed.

Failed runs also left nothing on disk except a missing file, so they could not be counted or
explained. ADR 0016 requires that they are logged, never dropped.

## Decision

- **Input fingerprint.** The CSV gains an `input_fingerprint` column before `checksum`: FNV-1a (a
  simple non-cryptographic hash) of the input pixels, 16 hex digits, computed once before
  measuring, outside the timed region. The header is now
  `env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum`; the
  same input must give the same fingerprint in every environment.
- **Build info from the artifact.** The crate records at compile time the `rustc -V` string, the
  locked `wasm-bindgen` version, the effective `RUSTFLAGS` and the enabled features
  (`bench/build.rs`, `build_info.rs`).
  - The native runner prints them with `--build-info` (plus its clock resolution); the WASM module
    exports `buildInfo()`, which the page adds to its metadata.
  - Reading them from the artifact, not from the host toolchain, ties each result to the code that
    produced it. For example, a `pad64` build that overwrites `www/pkg` is visible in
    `build.features` and `artifactSha256` of every run it produced.
- **New context keys**, added to ADR 0023's list, all required:
  - `orderPosition`, `startedAt` and `finishedAt` (UTC, ISO 8601), `launchSeconds`;
  - `artifactSha256` (of `bench_bg.wasm` for browser runs, of the native executable for native
    runs) and `build`;
  - `loadavgBefore` and `loadavgAfter` (1, 5 and 15 minute load averages).
  - `validate(strict=True)` also rejects `unavailable` for `orderPosition`, `startedAt`,
    `finishedAt`, `artifactSha256` and `build`, and a `build` whose `rustc` or `wasmBindgen` is
    `unavailable`. Load averages are recorded for analysis, not enforced.
  - Package temperature and effective frequency, optional in the review, are not recorded: turbo is
    off and the governor is fixed (ADR 0002), and reading them needs root or extra tools.
- **Failed runs are records.** A failed run writes `<run>.error.json` with an `error` message and
  the same context keys, and never a CSV:
  - the page catches every error (including a page that is not cross-origin isolated) and sends
    `POST /errors?run=<id>` with `{"error": ..., "meta": {...}}`; the server writes the file
    exclusively (409 if it exists, the same run id rule as ADR 0019);
  - the launcher reports `error` (the page reported a failure), `timeout` or `exited`, writing the
    message itself for the last two;
  - the native wrapper writes it for a non-zero exit, a timeout or output without the CSV header.
- **Browser output.** Browser stdout and stderr go to `<run>.browser.log`, deleted when the run
  succeeds and kept otherwise.

## Consequences

- The analysis can plot time against order position or start time per environment to look for
  drift, and can exclude or explain every failed run instead of seeing gaps.
- Within one campaign, `artifactSha256` and `build` must be constant per target: one value for
  native, one for the WASM module shared by Chrome and Firefox. They differ between native and
  WASM by design. `input_fingerprint` and the checksum must match across all three environments.
  Any other mismatch is a harness error to investigate, not a result.
- `launchSeconds`, `startedAt` and `finishedAt` are seen from the wrapper: for browsers they
  include the 0.2 s result polling and the shutdown grace, for native they do not. They order runs
  in time for the drift analysis; they are not compared between environments (the measured times
  are the CSV `ns` column).
- The browser log is written by the browser process during the run, which native runs do not
  have. Its volume is small; the pilot checks that it does not change the variance, and it can
  move to a tmpfs (an in-memory file system) if it does.
- The orchestrator (ADR 0034) passes `--order-position` with the order seed.

## Status

Accepted; amends ADR 0016 (CSV header), ADR 0019 (`POST /errors`) and ADR 0023 (context keys)
