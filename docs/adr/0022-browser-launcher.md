# ADR 0022: Browser launcher with a fresh profile, taskset and no automation

Date: 2026-10-17

## Context

Each browser run must be:

- a fresh launch, so that no state (JIT state, caches) carries over from an earlier run and
  every run is an independent sample (ADR 0005);
- free of any automation attached to the browser (ADR 0006);
- confined to the P-core mask with `taskset`, the process-level CPU affinity tool, like the native
  runs (ADR 0001);
- finished when its result file exists (ADR 0019, ADR 0020).

The launcher is the piece that does this for both browsers. It must also make sure that one run
cannot leak into the next: a browser is several processes (renderer or content processes besides
the main one), and any of them that survived would still be running when the next run starts.

## Decision

- **Launch and cleanup** (module `harness.launcher`):
  - build the command per browser, and prefix `taskset -c <cpus>` when a mask is given (Linux);
  - create a temporary profile;
  - start the browser in its own process group;
  - wait for `<run>.csv`;
  - then always signal the whole group: SIGTERM, up to 5 s for the leader to exit, then SIGKILL to
    the group, so no renderer or content process survives into the next run;
  - finally delete the profile.
- The query must not set `run` or `env`; the launcher sets both, so a run cannot be filed under the
  wrong id or environment.
- **Browser settings**, to keep background work out of the measurement:
  - Chrome: `--user-data-dir=<profile>`, no first run, no default-browser check, no background
    networking, no component updates, no default apps, no extensions, no sync, metrics recording
    only.
  - Firefox: `-no-remote -new-instance -profile <profile>` and a `user.js` that turns off updates,
    telemetry, health reports, the welcome page and the default-browser check.
- **Headless** is an option (`--headless`); headless against headful is decided in the pilot
  (ADR 0046).
- **Outcome per run:** `done`, `timeout` (no result within the timeout) or `exited` (the browser
  quit without a result, with its exit code).

## Consequences

- The orchestrator (ADR 0034) records `timeout` and `exited` runs as invalid and keeps their
  configuration, and stores the launch context with every result (browser version, CPU mask,
  headless flag, launch flags; ADR 0023).
- Check on the development Mac (not results): 10 consecutive headless launches of Chrome and of
  Firefox 158.0 all finished, left no processes or profiles behind, and gave the same checksum.
  The first Firefox launch after mounting the app took about 8 s, the rest about 1 s. The pilot
  decides whether a throwaway launch precedes the campaign, so that this slow first launch is not
  confounded with the random order (ADR 0034).

## Status

Accepted; amended by ADR 0029 (quiet browser settings, start delay) and ADR 0031 (page URL,
leftover check)
