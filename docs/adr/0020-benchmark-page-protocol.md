# ADR 0020: Benchmark page protocol

Date: 2026-10-17

## Context

Each browser run is a fresh browser launch on a URL (ADR 0005, ADR 0006). Nothing is attached to
the browser, so the URL is the only input and the results server (ADR 0019) is the only output.
The page must therefore run unattended from the URL alone and report either a result or a clear
failure.

There is also a threading constraint: Rayon's workers wait with `Atomics.wait`, and the browser's
main thread may not call `Atomics.wait`. The thread that drives the
measurement and blocks while the work runs must be a Web Worker.

## Decision

- **URL.** `index.html?run=<id>&<RunConfig query>` (ADR 0018). The page takes `run` out and
  forwards the rest unchanged.
- **Isolation check.** The page refuses to run unless `crossOriginIsolated` is true and shows a
  clear error, since without it there are no shared-memory threads (ADR 0019).
- **Coordinating worker.** The page starts one dedicated module Web Worker, the coordinator. The
  worker loads the module, calls `startThreadPool(N)`, measures the clock resolution, runs
  `run(query)` and sends back the CSV and metadata. The main thread never blocks.
- **Delivery.** The page POSTs `{csv, meta}` to `/results?run=<id>`, adding `navigator.userAgent`
  to the metadata; the worker adds `clockResolutionNs`, `clockSmallestStepNs` and
  `hardwareConcurrency`.
- **Progress** is shown in `document.title` and the page body: `pending`, `running`, `done` or
  `error`.

## Consequences

- The harness knows a run finished when `<id>.csv` exists. A run that shows `error` or never posts
  leaves no file and is treated as invalid after a timeout (by the launcher of ADR 0022 and the
  orchestrator of ADR 0034).
- The page has no build step: plain ES modules next to `pkg/`.
- Verified on the development Mac (not results): in the app's Chromium and in headless Chrome
  launched directly with a fresh profile, both `hist-atomic` and `filter` give the same checksum as
  the native runner, and the page aborts without COOP/COEP. Firefox was to be verified once the
  pinned build existed (ADR 0021).

## Status

Accepted
