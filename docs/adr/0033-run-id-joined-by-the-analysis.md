# ADR 0033: The run id is joined by the analysis, not stored in the CSV

Date: 2026-10-17

## Context

Each run leaves two files: `<run>.csv` with one row per timed iteration (ADR 0016) and
`<run>.json` with the context of the run (machine state, build, versions; ADR 0023). The CSV
rows carry the configuration (environment, workload, input, k, threads, and so on) but not the
run id, which exists only in the file names. Since the run is the unit of analysis (ADR 0005),
the analysis must know which rows belong to which run. The review of the code before the
pilots asked whether the run id should become a CSV column or be added by the analysis.

## Decision

- **The CSV schema stays as it is.** The analysis loads each run as the pair `<run>.csv` and
  `<run>.json` and, while loading, adds the run id (the shared file stem) and the context it
  needs as columns. This keeps the schema shared by the Rust runner and the WASM page
  unchanged.
- **Pairs must be complete.** A CSV without its JSON (or the reverse) stops the loader with an
  error.
- **Failed runs are counted, never mixed in.** A failed run (`<run>.error.json`, ADR 0027) is
  never joined into the measurement table; the loader counts failed runs per environment and
  configuration and reports them.
- **Raw data is never edited by hand.** Raw files in `data/raw/` are never renamed or
  concatenated by hand; combined tables are produced only by the analysis code.

## Consequences

- No change to the Rust runner, the WASM page, the harness or the CI cases; the run id stays
  validated and unique (ADR 0019, ADR 0031).
- A CSV taken out of its directory or renamed loses its link to its context; the rule on raw
  files and the analysis loader are what prevent it.

## Status

Accepted
