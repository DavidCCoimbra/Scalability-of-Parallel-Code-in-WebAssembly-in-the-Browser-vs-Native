# ADR 0096: The documentation is part of the repository, in six groups with one job per page

Date: 2026-11-28

## Context

ADR 0073 made a multi-page explainer the documentation of the study, and ADR 0074 rewrote it
for juniors first, in two layers on every page. Both were written in the earlier repository.
When the final repository was assembled, the explainer stayed behind, and both records were
marked "not part of this repository".

That left the final repository with the decision records and one README per module, and
nothing a newcomer could read from start to end: what the study asks, what it found, how a
run is made, how to reproduce a table.

The earlier explainer was accurate, but it was not fit to be brought over as it was:

- **Its numbers were those of `measured/v2`.** The reported build is `measured/v3` (ADR 0095),
  which also adds what v2 could only declare: the sequential references, the engine arms, the
  atomic increment probe, the counters of the loop alone, the per-core check and the gate
  (ADR 0084 to ADR 0094).
- **It was scattered.** 44 loose pages in nine groups, several of them splitting one subject
  in two (the results of RQ2 and their cause, the plain statistics and the formal ones, the
  machine and the problems found on it).
- **It had too many kinds of boxes.** Why, analogy, definition, one-sentence summary, what to
  remember and callout, plus a second layer folded into most sections. A page read as a set
  of boxes more than as a text.
- **Some pages did two jobs.** Concept pages carried measured numbers, and one guide covered
  both adding a workload and changing the measured path.
- **It described tooling this repository does not have**: tickets, a second documentation
  folder, make targets and analysis commands of the pilots.

## Decision

**The documentation is part of this repository, at `docs/explainer/`.** It is a set of HTML
pages that open from `file://` with no build step, no CDN and no external font. The contract
for a page is `docs/explainer/README.md`; this record fixes its main points.

- **Six groups, in the order of the sidebar.** Getting started, Concepts, The study, Results,
  Guides and Reference.
- **One job per page.** A page teaches a concept, describes the design, reports results, walks
  through a task, or is looked up. A concept page has no measured numbers: it links to the
  Study or Results page that has them.
- **One page anatomy.** A title, one lead that says what the page gives the reader, sections
  with an id each, the advanced detail last (a section named "In depth" or a collapsed block,
  never before the plain explanation), and a source line under each table, chart or claim
  that rests on a file.
- **Three callouts only**: Note, Warning and Why. A Why gives the reason for a decision, what
  would go wrong without it, and its record. Everything else is prose.
- **One shell.** A sidebar with the groups, one reading column, an outline of the page on the
  right, previous and next links, a search over pages, sections and glossary terms, and a list
  at the end of each page of the tables, files and records it rests on.
- **The writing.** Second person where the reader does something, present tense, short
  paragraphs, a term explained at its first use or linked to the glossary, one name per
  concept. Each explanation is stated at its level: measured, tested by an intervention,
  supported by measurements that agree, or open.
- **Numbers only from `assets/data.js`.** `scripts/explainer_data.py` writes that file from the
  tables of `data/tables/*-v3`, the fork-join calibration of `data/raw/campaign-v3`, the
  per-core check, the atomic increment probe and the code excerpts the pages ask for. No
  measured number is typed into a page when a table has it. `make explainer` regenerates the
  file, and `python3 -m scripts.explainer_data --check` fails when it is out of date; `make
  lint` and the `python` job of CI run that check.
- **Juniors first stays, as a rule of writing.** The reader ADR 0074 wrote for is still the
  reader: someone with no background who has to join the project. What changes is the means:
  a term explained where it is first used and the detail at the end of the page, instead of
  two visual layers on every section.

## Consequences

- **A new page follows the contract.** It copies the head, the shell and the scripts of an
  existing page, belongs to one of the six groups, is added to `PAGES` in `assets/app.js`
  (which feeds the sidebar, the search and the previous and next links), and reads its numbers
  through `UI.row` and `UI.rows` with a source line.
- **What was merged.** 44 pages became 37. The cause of the RQ2 effect is on the RQ2 page; the
  formal statistics follow the plain ones on one page; the problems found while measuring sit
  next to the control each one broke (the machine, the run protocol, the environments); the
  repository tour holds the folders, how the programs talk and the two lookup tables; the
  cutoff and grain campaigns are with the other exploratory campaigns; contention and padding
  are with memory and caches; the vocabulary is with the research questions.
- **What was added.** A page on what explains the results (the nine questions of ADR 0088, the
  test of each and its outcome), a guide to the session of a build (ADR 0084 to ADR 0087), a
  guide to adding a workload, and a reference of the campaign spec format.
- **What was dropped.** The second layer as a visual device, the boxes other than the three
  callouts, the per-reader progress bar, the table for the grader on the first page, and every
  command, module, folder and workflow step that this repository does not have.
- **`data.js` has to be kept in step.** It is a generated file of about 1 MB, committed so
  that the pages open without a build. A change to a v3 table, or to a line of code that a
  page shows as an excerpt, makes it stale, and lint and CI fail until `make explainer` is
  run. An excerpt is found by the text of its first line, so it follows the code when lines
  move, and the generator stops when that text is gone or is on more than one line.
- **The statements of the pages follow the paper.** Where the paper states a claim at a given
  strength, the pages state it at that strength. The page on reproducing the tables recomputes
  the main numbers from `data.js` next to the values as stated, so a difference shows.
- **The prose is hand-written and can go stale.** Only the numbers and the excerpts are
  checked. A change of design needs its record and the pages that describe it.

## Status

Accepted; supersedes the "not part of this repository" notes of ADR 0073 and ADR 0074 and the
two-layer design of ADR 0074
