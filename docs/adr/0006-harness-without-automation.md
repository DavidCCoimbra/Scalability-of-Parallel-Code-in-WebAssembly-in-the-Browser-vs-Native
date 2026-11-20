# ADR 0006: Harness without a browser automation framework

Date: 2026-10-17

## Context

The harness is the code that starts each run and collects its result. Browser automation tools
(Puppeteer, Playwright, or the Chrome DevTools Protocol (CDP) and WebDriver BiDi that they use)
attach to the browser through a debugging channel. While attached, they could change the
browser's behaviour during the measurement, and they work differently in Chrome and Firefox, so
any effect would not be the same in both browsers.

## Decision

- The harness launches the browser binary directly: under `taskset` (ADR 0001), with a fresh
  temporary profile (ADR 0005) and with the run's configuration in the URL.
- The page POSTs its results to a local server. The same server also sends the COOP/COEP
  headers, which make the page cross-origin isolated; browsers only allow `SharedArrayBuffer`,
  and therefore WASM threads, on such pages.
- The harness then closes the browser.
- Native, Chrome and Firefox runs are interleaved in a random order with a recorded seed, so
  slow drift of the machine over a session does not fall on one environment.

## Consequences

- Chrome and Firefox are driven by the same mechanism, and the structure is the same as for the
  native runs (launch a process, collect its result).
- More harness code to write and debug. Plan B, if a browser misbehaved: Puppeteer for both
  browsers.
- Automation is allowed in CI for correctness checks only, never for measurement.

## Status

Accepted
