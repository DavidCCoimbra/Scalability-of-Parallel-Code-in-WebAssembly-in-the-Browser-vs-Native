# ADR 0034: Campaign orchestrator with a seeded interleaved order and resume

Date: 2026-10-17

## Context

A campaign is the full set of runs behind one comparison. Native, Chrome and Firefox runs must
be interleaved in a random order with a recorded seed (a design decision of the study; ADR
0005, ADR 0006). The reason: running all runs of one environment first would let any slow
drift of the machine (thermal state, background activity, memory fragmentation) line up with
the environment, and the drift would then look like an environment effect. A campaign also
takes hours, so it must survive an interruption without repeating or losing runs.

## Decision

### Specification

- A campaign is a JSON spec (`harness/campaigns/*.json`) holding every parameter the pilot
  fixes: environments, workloads with their input and `k`, thread counts, repetitions, image
  size, warm-up, iterations, calibration samples, CPU masks, scope user, headless, start delay,
  timeout, the optional discarded first launch per browser, and whether validation is strict.
  Unknown keys are rejected, so a misspelt parameter cannot be silently ignored.

### Order and execution

- `python3 -m harness.campaign SPEC` builds every combination of environment, workload, thread
  count and repetition, shuffles the whole list once with `random.Random(orderSeed)` and runs
  it in that order. Each run is a fresh process (ADR 0005), started through the native wrapper
  or the browser launcher.
- The run id is `<name>-<position>-<environment>-<workload>-<input>-n<N>-r<repetition>`, and
  the position in the order is recorded as `orderPosition`.
- The orchestrator pins itself to `harnessCpus` and serves the page from a results server in
  its own process, so the server also stays off the measured CPUs (ADR 0019, ADR 0028).

### Records

- Results go to `<results>/<name>/`. `campaign.json` records the spec, the seed, the commit,
  the planned run ids and every resume time. `campaign.jsonl` gets one line per executed run
  with its configuration, query, status, duration, error message and validation problems.
- A failed run is logged and the campaign goes on (ADR 0016, ADR 0027).

### Resume and failed runs

- Rerunning the same spec resumes it: runs that already left files are skipped and the order is
  the same. A different spec, commit, native or WASM artifact hash, or browser version in the
  same directory is refused (`campaign.json` keeps them under `build`), so one campaign never
  mixes builds.
- A failed run is not retried on resume. The failure is itself data (the failure rate per
  environment), and retrying silently would hide it. The campaign exits non-zero while any
  planned run has failed. `--retry-failed` moves each `.error.json` into `failed/`, where it
  stays as the record, and runs that position again. Whether failed runs are retried is decided
  by the author per campaign, and the `failed/` directory shows it.

### Discarded first launch

- If `discardFirstLaunch` is set, each browser is launched once before the plan, into
  `discarded/`, and logged with `discarded: true`. Its purpose is a slow first launch: the first
  Firefox launch on a machine took about 8 s instead of 1 s. Whether to use it is decided in the
  pilot.

### Loader

- `python3 -m harness.collect <dir>` is the loader of ADR 0033. It produces one table with the
  run id and the drift context (`orderPosition`, `startedAt`, `foreignCpuSeconds`,
  `startDelayMs`) before the CSV columns. It counts failed runs per environment, reports planned
  runs without any file as missing, and reports as a conflict any workload and input whose
  checksum differs between environments or thread counts; missing runs and conflicts make it
  exit non-zero.

## Consequences

- With the order shuffled over the whole campaign, drift spreads over all environments and
  configurations instead of being confounded with one; `orderPosition` and `startedAt` let the
  analysis check for it.
- One seed reproduces the whole order; the spec and the commit in `campaign.json` reproduce the
  configuration.
- A development check on the Mac (not a result): a native-only spec with all 9 workloads, 4
  thread counts and 2 repetitions ran its 72 runs, a second invocation skipped all 72, and
  `collect` produced one table.

## Status

Accepted; amended by ADR 0040 (environment check enforced on every start)
