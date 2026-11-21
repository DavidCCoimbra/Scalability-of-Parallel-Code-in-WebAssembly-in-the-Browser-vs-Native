# ADR 0081: Every analysis command reads a campaign through one loader

Date: 2026-11-21

## Context

The analysis plan (ADR 0037, D7) allows two predefined exclusions and no other: a run above the
foreign-CPU threshold (0.25 s, ADR 0051) and, in a strict campaign, a run that fails strict
validation. `analysis.results`, `robustness`, `rq2_decomposition` and `calibration` applied
them. `analysis.v0` (the scaling tables), `figures`, `distributions`, `cutoff`, `grain` and
`extras.build_variants` did not: each read the campaign with its own copy of the same steps
(collect, stop on a checksum conflict, report failed runs), and the copies had drifted. `grain`
did not report planned runs without a file, and only the contrasts' sidecar recorded how many
runs were excluded, failed or missing.

The tables agreed with each other only because no run was excluded. Counted on 2026-11-21 with
the threshold of 0.25 s, with and without strict validation, the exclusions are 0 runs in each
of the 16 campaign directories of `measured/v2` (21 450 runs in all). With one excluded run, the
scaling table and the figures would have described a different set of runs from the contrasts.

## Decision

- `analysis/loading.py` holds the one way to read a campaign: `load_campaign(directory, rule)`
  collects the runs, stops on a checksum conflict and removes the runs the rule excludes. Every
  command that writes a table or a figure calls it and takes the same `--strict`,
  `--foreign-cpu-threshold` and `--no-foreign-cpu-threshold` options.
- The make targets pass `--strict` to every such command, as they already did to `results`.
- The scaling sidecar (`<campaign>-scaling.json`) records the rule and the counts:
  `foreignCpuThreshold`, `strict`, `excluded`, `failed`, `missing`.
- `datacheck` and `iteration_drift` stay as they are: they describe the data as recorded, the
  excluded runs included, and `datacheck` is where the exclusions are counted by reason.

## Consequences

- No number changes: `make tables-check` regenerates every CSV of every campaign identical to
  the committed one. The 13 scaling sidecars gain the five keys above and are regenerated, so
  their `commit` is now a commit of this repository.
- A later campaign with an excluded run gets scaling tables, figures and contrasts over the
  same runs, with the count in each sidecar.
- A checksum conflict now stops `figures`, `distributions` and `extras.build_variants` too;
  before, they drew whatever was collected.

## Status

Accepted; implements D7 of ADR 0037 for the scaling tables and the figures
