# ADR 0007: Pinned browser builds

Date: 2026-10-17

## Context

Browser engines change every few weeks, and a new version can change WASM performance. The
results must be reproducible later with the same engine, and the engine must not change in the
middle of the study. A normal browser installation updates itself and old versions are hard to
obtain.

## Decision

- Chrome = Chrome for Testing at a fixed version. It is a build meant for testing, with the same
  V8 and Blink as Chrome stable of that version, and old versions stay downloadable.
- Firefox = the official release build from archive.mozilla.org at a fixed version.
- Versions are chosen at the start of the pilot and frozen until the end.

## Consequences

- The browser environment is reproducible.
- The study assumes that Chrome for Testing performs like Chrome stable of the same version. This
  is a threat to validity; an optional sanity check compares them (done in ADR 0050: within about
  1.3 % in the configurations tried).
- The paper states both versions.
- The versions are set by ADR 0021. ADR 0071 makes sure Firefox cannot update itself and that a
  campaign checks the pinned versions before it starts.

## Status

Accepted; versions set by ADR 0021
