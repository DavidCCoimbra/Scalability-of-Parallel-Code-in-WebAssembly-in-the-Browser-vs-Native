# ADR 0019: Local results server with cross-origin isolation

Date: 2026-10-17

## Context

Threads in WebAssembly share memory through a `SharedArrayBuffer`. Browsers only expose it to a
page that is cross-origin isolated, which the server enables with two response headers: COOP
(`Cross-Origin-Opener-Policy`) and COEP (`Cross-Origin-Embedder-Policy`). So the benchmark page
must be served by a server that sends them.

The harness also attaches no automation framework to the browser (ADR 0006), so it cannot read the
results out of the page. The page itself must deliver them, and something must write them to disk.
One local server does both.

## Decision

- **Serving.** `harness/server.py`, Python standard library only, binds `127.0.0.1` and serves
  `bench/www/` with `Cross-Origin-Opener-Policy: same-origin`,
  `Cross-Origin-Embedder-Policy: require-corp`, `Cross-Origin-Resource-Policy: same-origin` and
  `Cache-Control: no-store`, and the right content types for `.wasm` and `.js`.
- **Receiving.** `POST /results?run=<id>` takes JSON `{"csv": "...", "meta": {...}}` and writes
  `<id>.csv` (the shared schema, ADR 0016) and `<id>.json` under `data/raw/`.
  - `meta` must contain the fields only the page knows: `userAgent`, `clockResolutionNs`,
    `clockSmallestStepNs`.
  - Host-side fields (commit, CPU, governor, turbo, kernel, order seed) are merged into `<id>.json`
    later by the harness (ADR 0023, and the orchestrator of ADR 0034).
- **Complete or absent.** Both files are first written as temporary files in the same directory;
  the JSON is moved into place first and the CSV is linked last. So an existing CSV always means a
  complete run, and the harness can use the CSV's existence as the signal that a run finished.
- **Run ids.** The run id is assigned by the harness and must fully match `[A-Za-z0-9_-]{1,64}`
  (no path traversal, no trailing newline). An existing run is never overwritten (HTTP 409): a
  repeated run is a harness bug to see, not to hide.
- Bodies over 64 MiB are rejected.
- **Out of the way of the measurement.** The server is quiet by default (request logging only
  with `--verbose`), and the orchestrator runs it outside the P-core (performance core) `taskset`
  mask used for the measured process, so it cannot take a measured core.

## Consequences

- No dependencies to install on the measurement PC beyond Python.
- `no-store` keeps every fresh browser launch from reusing a cached module from an earlier build.
- The orchestrator (ADR 0034) creates the run ids and treats a missing result file after the
  browser exits as an invalid run.

## Status

Accepted; amended by ADR 0027, ADR 0028 (server on the E-cores), ADR 0031 and ADR 0032
