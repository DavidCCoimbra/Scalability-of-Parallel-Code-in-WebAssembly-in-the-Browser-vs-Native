# ADR 0031: Harness robustness: unique run ids, exact versions, loopback address, leftover processes

Date: 2026-10-17

## Context

Every run of the study leaves a result CSV (`<run>.csv`) and a context file with the machine and
build state (`<run>.json`), linked by the run id. A result is only trustworthy if the context
next to it belongs to the same run. The review of the harness code, done once the code was
complete and before the pilots, found five small ways in which the harness could store a wrong
or mixed result without noticing:

1. **A reused run id.** The browser launcher saw the CSV left by the earlier run with that id,
   reported success and merged the new context into the old metadata. The native wrapper
   crashed on the existing CSV instead.
2. **A pinned version compared as a substring.** Firefox `158.0.1` passed the check for the
   pinned `158.0` (ADR 0021), so a silently updated browser would have been accepted.
3. **A duplicate `POST /results`.** The results server (ADR 0019) replaced the stored JSON
   before the CSV link rejected the second request, so the stored run ended up with the
   context of the duplicate.
4. **A page URL on `localhost`** while the server binds `127.0.0.1`: the page did not use the
   address the server actually listens on.
5. **No check that the browser left no process behind** once its run was over.

## Decision

- **Run ids are never reused.** The launcher and the native wrapper refuse a run id that
  already has a `<run>.csv`, `<run>.json` or `<run>.error.json` (the failed-run record of
  ADR 0027), before anything is launched (`FileExistsError`).
- **Exact version match.** Strict validation (the check that rejects a run whose recorded
  context breaks the measurement conditions, ADR 0023) compares the last token of
  `browserVersion` with the pinned version exactly, not as a substring.
- **The metadata is written exclusively.** `ResultStore.save` links the metadata into place
  exclusively, as it already did for the CSV, so a duplicate POST gets HTTP 409 and leaves the
  stored run untouched.
- **No half-used run ids.** If the CSV link fails after the metadata was linked, the metadata
  this call linked is removed again.
- **The page URL uses `127.0.0.1`**, the address the server binds. A loopback IP address is a
  secure context in the browser, so cross-origin isolation (COOP/COEP, needed for
  `SharedArrayBuffer` and therefore for WASM threads) still works.
- **Leftover processes are killed and counted.** After a browser run, any process whose command
  line contains the run's profile path (`pgrep -f`) is killed, and the count is recorded as
  `leftoverProcesses` (0 for native runs). Strict validation rejects the value `unavailable`
  (the check did not run) but not a count above 0. The reason for accepting a count above 0:
  the leftover process belonged to the run being recorded, its measured work was already over,
  and it is gone before the next run starts, so it cannot disturb any measurement.

## Consequences

- A repeated run id is a harness error that stops the run, instead of producing a CSV with
  another run's context.
- A browser updated past the pinned version fails strict validation.
- A `leftoverProcesses` value above 0 shows that `killpg` (and the scope stop of ADR 0028)
  missed a process; the next run still starts clean.

## Status

Accepted; amends ADR 0019 (exclusive metadata), ADR 0022 (page URL, leftover check) and
ADR 0023 (exact version check, `leftoverProcesses`)
