# ADR 0010: Development workflow: PRs with CI and AI review, ADRs mirrored to Notion

Date: 2026-10-17

## Context

The project's rules allow AI tools only if their use is declared, and the author must be able
to explain every line of code, analysis and text. Claude Code, an AI coding assistant, is used
as a support tool (discussion, review, help with development), not as the author of the project.
Decisions must be easy to justify in the paper, and results must be reproducible.

## Decision

- Every change goes through a tracked task, a branch and a pull request (PR) with CI and an AI
  review; the author reviews and merges.
- Decisions are recorded as ADRs in `docs/adr/`. The repository copy is the canonical one; it was
  mirrored to a Notion database after each merge.

## Consequences

- There is written evidence of understanding (review threads, the author's explanations of the
  changes).
- Each change carries some overhead.
- `AI_USE.md`, the declaration of AI use, is written by the author, never by the tool.
- GitHub Free offers no branch protection for this repository, so the rules are kept by agreement
  and a pre-merge checklist.

## Status

Accepted; Notion part superseded by ADR 0063
