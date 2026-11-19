---
name: conventional-commits
description: Write every commit message and PR title in this repo as a Conventional Commit (v1.0.0). Use before any git commit, squash-merge title or PR title.
---

Every commit message and every PR title follows
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). PRs are
squash-merged, so the PR title becomes the commit on `main`: it follows the same rules.

## Format

```
<type>(<scope>)!: <description>

[optional body]

[optional footer(s)]
```

- `type` is required, `scope` is optional, `!` marks a breaking change.
- One blank line between the header and the body, and between the body and the footers.
- Footers use `Token: value` or `Token #value`. A breaking change is either `!` in the header
  or a `BREAKING CHANGE: <what breaks>` footer (both is fine).

## Types

| Type | When |
|---|---|
| `feat` | New code that adds a capability (a workload, a runner, a harness step, an analysis) |
| `fix` | A bug fix |
| `refactor` | A code change that neither adds a capability nor fixes a bug |
| `perf` | A change made for speed. In `bench/` it needs an ADR (see CLAUDE.md) |
| `test` | Tests only |
| `docs` | README, ADRs, paper, comments only |
| `build` | Makefile, `make/`, Cargo, toolchain, dependencies |
| `ci` | `.github/workflows` |
| `data` | Measured runs and derived tables under `data/` (an extra type; the spec allows it) |
| `chore` | Anything else (repo setup, `.claude/`, `.gitignore`) |

## Scopes

`bench`, `harness`, `analysis`, `scripts`, `make`, `ci`, `data`, `paper`, `adr`. Leave the
scope out when a change spans several of them.

## Rules for this repo

- English, imperative mood, lower case after the colon, no full stop: `add`, not `Added` or
  `adds`.
- The header fits in 72 characters.
- The body says why, not what the diff already shows. Wrap it at 72 characters.
- Never the em dash: write a plain hyphen "-".
- No attribution lines: no `Co-Authored-By` for Claude or any AI, no "Generated with" line.
  AI use is declared in `AI_USE.md`, which the author writes.
- One logical change per commit.

## Examples

Good:

```
feat(bench): add the 3x3 Gaussian filter workload
```

```
fix(harness): wait for the page's POST before closing the browser

Firefox closed the tab before the result reached the server, so the
run was recorded as missing.
```

```
data: add the measured/v2 raw runs and tables
```

```
refactor(bench)!: rename the config key threads to workers

BREAKING CHANGE: campaign specs must use "workers" instead of "threads".
```

Bad, and why:

| Message | Problem |
|---|---|
| `Added gaussian filter.` | No type, past tense, full stop |
| `feat: Add filter` | Capital letter after the colon |
| `DAV-404: gaussian filter` | Ticket prefix instead of a type |
| `feat(bench): add filter` + em dash + `SIMD` | Em dash (use "-") |
| `update stuff` | No type, says nothing |
