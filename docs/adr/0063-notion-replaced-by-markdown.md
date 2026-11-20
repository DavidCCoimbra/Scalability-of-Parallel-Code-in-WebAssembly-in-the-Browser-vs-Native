# ADR 0063: Notion replaced by Markdown files in the repository

Date: 2026-11-08

## Context

ADR 0010 made the ADRs canonical in `docs/adr/` and mirrored them to a Notion database
("PPC · ADRs") after each merge. The workflow also kept the raw material for the paper
(decisions, pilot numbers, problems and references per ticket) in a second Notion database
("PPC · Material do relatório", 54 rows in Portuguese). This had three costs:

- two copies of the ADRs had to be kept in sync by hand;
- the paper material lived outside the repository, so it was not versioned or reviewed with the
  code;
- the post-merge step of the workflow depended on the Notion connector.

It also broke the rule that all project documents are in English.

## Decision

Decided on 2026-11-08: Notion is no longer part of the workflow.

- **Paper material.** It moves to `docs/paper-material/`, translated to English: one file per
  paper section (method, setup, results, threats to validity, related work), each entry under
  its first section and linked from the others, with an index in
  `docs/paper-material/README.md`. That folder is in the working repository, not in the final
  one.
- **ADRs.** They stay only in `docs/adr/` and are no longer mirrored.
- **Post-merge step.** After a merge, the workflow adds the ticket's paper material to
  `docs/paper-material/` (updating an entry with the same title, or adding it) on a small branch
  with its own PR, following the usual PR rules, and confirms that the ticket is closed.

This supersedes the Notion part of ADR 0010. Its PR workflow (ticket, branch, PR with CI and
automated review) is unchanged.

## Consequences

- **One source of truth.** The repository holds the ADRs, the paper material and the data,
  versioned and reviewed like the code.
- **An extra PR.** Each merge that has paper material adds a small extra PR.
- **The old databases.** The Notion databases stay as they are until they are switched off.
  They are not updated any more and are not cited.
- **Older documents.** The workflow spec and plan of 2026-10-17 keep their original text, with a
  dated note pointing to this ADR.

## Status

Accepted; supersedes the Notion part of ADR 0010
