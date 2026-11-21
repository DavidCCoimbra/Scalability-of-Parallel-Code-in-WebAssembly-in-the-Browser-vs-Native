# ADR 0071: Firefox cannot update itself, and a campaign checks the pinned browser versions first

Date: 2026-11-12

## Context

The browsers are pinned (ADR 0021): Chrome for Testing 155.0.8059.84 and Firefox 158.0 from
archive.mozilla.org. Pinning matters because browser engines change every few weeks, and the
results must be reproducible later with the same engine (ADR 0007). This was an
urgent fix between campaigns, decided on 2026-11-12.

On 2026-11-10 at 20:54 UTC the Firefox install in `harness/browsers/firefox-158.0` updated
itself to 160.0 with a partial update (`updates/last-update.log`, `updates.xml`).

- **Why the profile setting did not stop it.** The profile pref `app.update.auto = false`
  (ADR 0022) does not stop this: the download and the update on the next start still happen.
  Only the enterprise policy `DisableAppUpdate` stops them.
- **Why it was found late.** The harness checked the version only per run, in the strict
  validation. So the whole extras campaign on `measured/v2` (weak, simd-scalar, extras, hybrid)
  ran Firefox 160.0. All 2640 of its Firefox runs fail strict validation. Native and Chrome are
  fine.
- **What is not affected.** The main, grain and cutoff campaigns on `measured/v2` ran before
  the update. All their Firefox runs report 158.0.

## Decision

- **Updates off.** The browser installer writes `firefox/distribution/policies.json` with
  `DisableAppUpdate: true`. It writes it on every call, so installs made before this ADR get it
  too.
- **Version read from the install.** The installer reads `Version` from Firefox's
  `application.ini`. An install that updated itself in place keeps its install marker, so the
  marker alone would not reveal the update; the install is reinstalled when the version is not
  the pinned one.
- **Check before the first run.** A strict campaign refuses to start when a browser's
  `--version` is not the pinned version, or when it reported no version. Like the machine
  checks, this runs on every resume.
- **Reinstall.** Firefox 158.0 is reinstalled from the archive, with its SHA256SUMS checked.
- **Only the affected runs are repeated.** Only the Firefox runs of the extras campaigns are
  repeated:
  - the 160.0 runs move to `excluded/` in each campaign folder, and are kept;
  - `build.browsers.firefox` in `campaign.json` is set back to 158.0, and the change is recorded
    in the same file;
  - the campaign resumes from tag `measured/v2` with the same spec and seed, so each repeated
    run keeps its planned position and parameters.

## Consequences

- **Firefox runs as a block.** The repeated Firefox runs keep their random order among
  themselves, but they run as one block after the native and Chrome runs, not interleaved with
  them. So the time of measurement (thermal state, background load) is confounded with the
  environment in comparisons between environments. Speedups are computed within an environment
  (T1/TN), and T1 and TN of Firefox sit in the same block, so a drift that is slow and linear
  over the block cancels to first order; a non-linear drift does not.
- **The policy file is new too.** It is also new relative to the Firefox runs of the main, grain
  and cutoff campaigns. It only turns off the update service, which runs at startup and in the
  background, outside the timed region.
- **A control for both effects.** Both effects are checked with a control that the specs
  already contain. The extras campaign repeats four cells of the main campaign with the same
  settings (hist-local and hist-atomic at k = 1 and k = 256, 8192 x 8192, N in {1, 2, 4, 6, 7, 8}). Their
  Firefox medians in the repeated block are compared with the main campaign's Firefox 158.0
  medians, which were measured interleaved and without the policy. The same comparison for
  native and Chrome, both interleaved in both campaigns, gives the usual variation between two
  campaigns. The hybrid campaign is not a control, because its CPU mask differs. The 160.0 runs
  in `excluded/` also give the size of the version change itself.
- **Result of the control.** On `data/tables/*-v2`, the Firefox medians of the four repeated
  cells in the extras block are within -4.9 % to +3.3 % of the main campaign's (24 cells, median
  ratio 1.000); for native and Chrome, interleaved in both campaigns, the same ratios span
  -2.4 % to +4.5 %. The block's spread is the usual variation between two campaigns, so no
  Firefox result of the extras is corrected. Absolute Firefox-versus-native comparisons inside
  the extras campaign are still not interleaved and are read with that caveat.
- **Earlier detection.** A browser that changes version between campaigns now stops the campaign
  before its first run, instead of being found in the analysis.
- **Chrome.** Chrome for Testing has no updater, so it needs no policy.
- **Checksum pinned later (2026-11-21).** The sha256 of the 158.0 archive, as listed in
  Mozilla's `SHA256SUMS`, is now pinned in `harness/browsers.json` like Chrome's, so an install
  no longer trusts whatever that file says at download time. The campaigns of `measured/v2`
  installed 158.0 before the pin, verified against the same file.

## Status

Accepted
