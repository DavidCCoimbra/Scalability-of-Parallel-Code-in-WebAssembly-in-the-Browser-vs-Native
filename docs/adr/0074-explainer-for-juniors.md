# ADR 0074: The explainer is written for juniors first, in two layers

Date: 2026-11-13

## Context

ADR 0073 made a multi-page explainer the documentation of the study. Its first version was
accurate but written in the paper's register:

- it assumed the reader knew what a core, a thread, a cache, a median or a JIT compiler is;
- it stated decisions as bare consequences ("turbo off, or frequency would mix with scaling");
- it put tables before the ideas they measure.

A junior joining the project could not read past the second paragraph of most pages, and
nothing told a new contributor how to run, change or debug the project, or how the workflow of
PRs, ADRs and review goes.

The goal set for the documentation: someone with no background can follow it, it still serves
someone from the field, and it explains the reason behind every decision.

## Decision

- **Juniors first.** Every page opens in plain words: why, then what, then the number. No term
  is used before it is explained, on the page, on a Foundations page or in a glossary pop-up.
- **Two layers on one page.** Formulas, big tables, flags and the ADR-by-ADR detail live in
  folded `<details class="deeper">` blocks ("If you already know this"). A junior skips them;
  an expert opens them. There is one source of truth, not a second track of documents.
- **Every decision carries its failure story.** A "why" box gives the junior's question and what
  would go wrong without the decision, then points to the ADR.
- **Foundations pages**, with no project numbers: programs, processes, threads and cores; memory
  and caches; from source to machine code; measuring time; ratios and the log scale; four ways a
  study fools itself.
- **Working-on-it pages** for a new contributor: how the pieces talk, your first day, changing
  something safely, debugging a run, the workflow (tickets, PRs, CI, the automated review, ADRs,
  what is off limits).
- **The glossary teaches.** Each term has a plain one-sentence definition for the pop-up and a
  paragraph with a project example on the glossary page.
- **A written contract.** These rules are written down in the explainer's own README.

## Consequences

- **More pages.** 42 pages instead of 31. Each is longer, but the plain layer is short and the
  rest is folded.
- **More effort per page.** Writing a page costs more: a why box per decision, an analogy per
  hard idea, a figure per spatial idea.
- **A validator.** The validator checks ids, links, sources, code keys and glossary terms across
  every page.
- **Where it lives.** The explainer is not part of this repository.

## Status

Accepted; the two-layer design is superseded by ADR 0096. Juniors first stays, as a rule of writing. The explainer is part of this repository since ADR 0096.
