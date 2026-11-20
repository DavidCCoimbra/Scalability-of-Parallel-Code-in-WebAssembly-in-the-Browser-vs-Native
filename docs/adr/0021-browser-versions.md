# ADR 0021: Browser versions pinned to Chrome for Testing 155.0.8059.84 and Firefox 158.0

Date: 2026-10-17

## Context

ADR 0007 fixes where the browser builds come from (Chrome for Testing, Firefox from
archive.mozilla.org) and freezes their versions at the start of the pilot, so that the JavaScript
and WebAssembly engines cannot change in the middle of the study. The harness needs concrete
versions to download and test against now, and a way to make sure the downloaded binary is the
intended one.

## Decision

- **Versions.** Pin the stable versions of 2026-10-17: Chrome for Testing `155.0.8059.84` and
  Firefox `158.0` (decided by the author). If the pilot starts with other versions, a new ADR
  supersedes this one.
- **Download and verification.** Versions live in `harness/browsers.json`; `harness/browsers.py`
  downloads the Linux x64 builds into `harness/browsers/` (git-ignored).
  - It is idempotent: a marker per version plus the executable must exist, otherwise it downloads
    again.
  - It checks SHA-256 before extracting: Firefox against Mozilla's `SHA256SUMS`, Chrome against a
    hash pinned in `browsers.json`.
  - Chrome for Testing publishes no checksums, so an unpinned Chrome is refused. The first run on
    the measurement PC uses `--trust-on-first-use`, which prints the hash to pin; from then on the
    pin is enforced.
- **Limit of the check.** `SHA256SUMS` comes from the same host as the archive, so it detects
  corruption, not tampering (the `.asc` signature is not checked).

## Consequences

- The same engines for the whole study, and they can be downloaded again later to reproduce it.
- Check on the development Mac (not results): Firefox 158.0 for macOS (SHA-256 verified) runs the
  page headless with a temporary profile; checksums equal native and Chrome. The
  `performance.now()` resolution is 20 us in Firefox against 5 us in Chrome, which the pilot must
  account for when sizing iterations (ADR 0041).

## Status

Accepted
