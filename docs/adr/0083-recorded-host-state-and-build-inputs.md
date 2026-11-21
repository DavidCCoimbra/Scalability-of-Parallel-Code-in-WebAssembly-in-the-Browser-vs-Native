# ADR 0083: The host state and the build inputs that were not recorded are recorded from now on

Date: 2026-11-21

## Context

The audits of 2026-11-20 found facts about a campaign that no file of the campaign states
(ADR 0080 lists them as not established):

- **Host.** The mode of transparent huge pages, the kernel command line, the CPU vulnerability
  mitigations, the idle states, the amount of memory, the firmware version and the default IRQ
  affinity. `sysinfo` recorded the CPU, the frequencies, the shield and the quiet mode, which
  are the settings `make env-setup` controls, and nothing of what it leaves as found.
- **Build.** A run records the digest of the WASM module and of the native binary, but not of
  the JavaScript glue that wasm-bindgen writes next to the module, and not the versions of the
  crates between the workloads and the threads (rayon, rayon-core, wasm-bindgen,
  wasm-bindgen-rayon). They are in `Cargo.lock` at the campaign's commit, but the builds did not
  pass `--locked`, so a build could in principle have resolved other versions.
- **Browser settings.** Chrome's flags are in every run (`launchFlags`). Firefox's are written
  to the profile as preferences and were only in the harness source at the campaign's commit.

None of this changes a measured number. It decides what a later reader can check.

## Decision

- **`sysinfo.hostState`** (new, `harness/environment/host_state.py`) records, as found and
  without judging: `transparentHugepage` (`enabled`, `defrag`), `kernelCmdline`, `mitigations`,
  `cpuIdle` (driver and the idle states of the first measured CPU, with their `disable` flag),
  `memTotalKb`, `firmware` (BIOS vendor, version, date and board) and `defaultIrqAffinity`.
  Every campaign writes `sysinfo` before its first run, and `make env-check` writes it on its
  own.
- **`campaign.json` build identity** gains `wasmGlueSha256` (one digest over every JavaScript
  file of `www/pkg`: the bindings and the worker start-up snippets of wasm-bindgen-rayon),
  `crates` (the four versions, read from `bench/Cargo.lock`) and, when Firefox runs,
  `firefoxPrefs` (the preferences written to the profile).
- **`--locked`** on every cargo build, test and clippy of the make targets, of the `build-wasm`
  alias and of CI: a build that would need other dependency versions than the lock file's now
  fails.

## Consequences

- The campaigns of `measured/v2` are not changed and still lack these fields. Their host state
  is captured after the fact with `make env-check` on the same machine, which is evidence only
  of the state at that later date; ADR 0080 keeps the items as not established for the stored
  campaigns until then, and as recorded-after for them afterwards.
- `--locked` changes no build of this repository: the native and WASM builds pass with it
  without touching `Cargo.lock`, so the dependency versions are the ones already resolved.
- A campaign started before this change cannot be resumed after it, because the build identity
  is compared whole on resume and now has more keys. No campaign is in progress.
- Not recorded still: the engines' own defaults (tiers, flags compiled in) for a given browser
  version, and the DIMM layout, which needs root.

## Status

Accepted
