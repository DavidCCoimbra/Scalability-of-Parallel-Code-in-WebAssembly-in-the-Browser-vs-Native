# ADR 0029: Symmetric quiet browser settings and a recorded start delay

Date: 2026-10-17

## Context

With a fresh profile on every run (ADR 0005, ADR 0022), the page starts measuring while the
browser is still starting up.

The launcher settings of ADR 0022 were also asymmetric. Chrome had
`--disable-background-networking`, while Firefox kept Safe Browsing downloads, Remote Settings,
Normandy, push, GMP/OpenH264 updates and prefetching on.

That background work runs inside the same CPU mask as the measurement. At N = 1 it is absorbed by
the idle cores of the mask, but at N = 8 every core is measuring, so it would bias browser
efficiency down only at high N, where it would look like a scaling result (finding R3 of the
review of the benchmark code once it was first complete).

## Decision

- **Firefox prefs** (written to `user.js`) also turn off:
  - Safe Browsing (malware, phishing, downloads and remote lookups);
  - Remote Settings (`services.settings.server` points to a dummy `data:` URL, as in Mozilla's own
    test profiles);
  - Normandy and opt-out studies, push, GMP and OpenH264 downloads, system add-on updates and the
    add-on cache;
  - region lookup, the connectivity service, DNS prefetch, link prefetch and speculative
    connections.
- **Chrome flags** add `--disable-renderer-backgrounding`,
  `--disable-background-timer-throttling`, `--disable-backgrounding-occluded-windows`,
  `--disable-client-side-phishing-detection` (the Safe Browsing counterpart) and
  `--disable-domain-reliability`.
  - Firefox gets no counterpart to the anti-backgrounding flags: it throttles timers only in
    background tabs, and the measured page is the only, foreground tab, whose work runs in
    dedicated workers, which are not throttled. The warm-up pilot (ADR 0043) would show any
    throttling that remains.
- **Start delay**, so the measurement can begin after start-up work has settled:
  - The launcher takes `--start-delay-ms` (default 0) and passes it as the reserved `startDelayMs`
    URL parameter.
  - The page removes it from the run query and rejects a value that is not a plain decimal integer
    between 0 and 2^31 - 1 ms, the largest `setTimeout` delay (posted as a page error; the launcher
    checks the same range).
  - The page shows `waiting` and sleeps before it creates the coordinating worker, so module
    compilation and the thread pool start after the wait.
  - Every run records `startDelayMs` in its context (0 for native runs).
- The orchestrator (ADR 0034) uses one delay for every browser run of a campaign and checks it from
  the recorded `startDelayMs`.
- The duration of the delay is decided from pilot data (time per iteration against time since
  launch), not here; ADR 0048 fixes it.

## Consequences

- Both browsers start from the same "no background network work" baseline, so a difference between
  them is less likely to come from start-up services.
- The delay does not remove WASM tier-up (the engine first runs code compiled quickly by a baseline
  compiler and later swaps in code from its optimizing compiler): the optimizing compilers only run
  once the code runs. Tier-up is still handled by the warm-up iterations W (ADR 0005) inside each
  run.
- A pref or flag that a browser version ignores fails silently. The pinned versions (ADR 0021) keep
  the set stable, and the pilot (ADR 0043) shows whether any start-up activity remains.

## Status

Accepted; amends ADR 0022 (launcher settings) and ADR 0023 (context keys)
