# ADR 0073: Documentation as a multi-page explainer

Date: 2026-11-13

## Context

The study was documented in three places that overlapped:

- a reading guide (six Markdown files);
- a single-page interactive explainer;
- a long `README.md`.

Numbers were copied into each by hand, so they could drift from the data. Another project by
the same author had replaced its Markdown documentation with a multi-page HTML explainer whose
numbers come from the measured reports, and the same model was chosen here.

## Decision

- **One explainer.** A single explainer holds the documentation, as offline HTML pages in
  reading order: begin, the study, concepts, method, results, running it, the code.
- **The old documents go.** The reading guide and the single-page explainer are removed, and
  their content moves into the pages. The README keeps only setup, how to run and the layout.
- **No typed numbers.** The pages contain no number typed by hand. A script
  (`scripts/explainer_data.py`) writes a data file (`assets/data.js`) from the `measured/v2`
  tables and raw runs, and the pages read from it. Each widget shows its source CSV.
- **Excerpts follow the code.** Code excerpts are keyed by file and by a substring of their
  first line, so they move with the code. The script fails when an excerpt no longer resolves.
  Its `--check` mode runs in `make lint` and CI.
- **Kept as they are.** The ADRs, the analysis plan, the paper material and the module READMEs.
  The pages link to them.

## Consequences

- **The data and the pages stay in step.** A change in the data or in an excerpted file needs
  `make explainer`, or CI fails.
- **Pointers updated.** Code comments that pointed at the reading guide now point at the
  matching explainer page.
- **Older ADRs.** ADRs keep their old references to the reading guide, as records of their time.
- **Where it lives.** The explainer, its data script and the documents it replaced are not
  part of this repository, which keeps the ADRs and the module READMEs.

## Status

Accepted. The explainer is part of this repository since ADR 0096, which also replaces its structure (six groups, one job per page).
