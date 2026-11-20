# ADR 0024: Browser correctness checked in CI against native

Date: 2026-10-17

## Context

Every workload must give the same checksum natively and in both browsers, for every thread count
(ADR 0011, ADR 0015). A time is only comparable across environments if the same work was done; a
checksum mismatch means a bug, not a result. Checking this only by hand on the development Mac
would let a regression reach the measurement PC unnoticed.

## Decision

- **The check.** The browser check (module `harness.browser_check`) runs 27 cases natively and in
  headless Chrome for Testing and Firefox at the pinned versions (ADR 0021), and fails on any
  difference:
  - the cases: filter on noise, and `hist-atomic` and `hist-local` on k in {1, 4, 16, 256}
    (ADR 0026), each for N = 1, 2, 4;
  - 1024x1024 pixels, i.e. 16 histogram chunks, more than any N tested, so every thread gets work;
  - one warm-up and two measured iterations;
  - it goes through the same server, launcher and native wrapper as the campaign;
  - a timeout or crash is reported with its status.
- **CI job `browser`** runs it whenever `bench/` or `harness/` change, with the same build steps as
  the measured artifacts (default features, `build-wasm.sh`). Browser archives are verified against
  the pinned hashes and cached by `browsers.json`.
- In CI only, Chrome gets `--no-sandbox` (the runner's Ubuntu restricts the user namespaces
  Chrome's sandbox needs). Measurement runs never use it.
- CI checks correctness only; its timings are never used.

## Consequences

- A change that breaks equality in any environment or thread count fails the PR.
- The Chrome archive hash was obtained from the first CI download and is now pinned
  (`cf0f0498...bafcbc`).
- CI runners have few cores, so N above 4 is not checked there; the end-to-end smoke test on the
  measurement PC covers N up to 8.

## Status

Accepted; amended by ADR 0032 (input fingerprints compared too)
