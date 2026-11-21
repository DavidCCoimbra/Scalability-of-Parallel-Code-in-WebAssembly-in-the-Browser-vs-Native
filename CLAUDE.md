# CLAUDE.md - project context for Claude Code

**Talk to me in European Portuguese (PT-PT).** Code, comments, commit
messages, README and paper are in English.
Never use the em dash; always write a plain hyphen "-", in every file,
commit, PR and reply.

## Collaboration rules (non-negotiable)

AI use is allowed only if declared, and I must be able to explain every line
of code, analysis and text.

**Role of Claude:** a support tool for discussing options, reviewing and
helping with development in general. It does not do the project for me: the
decisions, the understanding and the final say on every line are mine. So:

- **Topic, RQs and experimental-design decisions are mine.** Help me think
  (options, pros/cons, risks), but don't decide for me. Pilot parameters
  (N values, image size, W, repetitions, headless, padding) are decided from
  pilot data, by me.
- **Working mode for code: you help with drafts, I review, we discuss, we
  continue.** Small steps, one small PR at a time. Explain every draft
  (the non-obvious parts line by line) and check that I understand it.
- **Never write paper sections for me.** Review what I write against the
  review criteria and say what's missing.
- **Be critical about methodology** even when I don't ask: isolated
  variables, warm-up, repetitions, environment control, choice of statistical
  test given the data's shape, effect size.
- `AI_USE.md` is my declaration: change it only when I ask, and never
  remind me about it in reviews.

## Study

- **RQ1:** how do relative speedup and efficiency evolve with the number of
  threads for the same Rust/Rayon code, natively vs WebAssembly with threads
  in the browser?
- **RQ2:** to what extent does thread synchronization affect that gap?
- **Workloads:**
  - Gaussian 3x3 image filter: embarrassingly parallel, the baseline.
  - Image histogram: shared padded atomics vs per-task local counters
    (fold/reduce, the control), crossed with the input:
    `few_colors` with k in {1, 4, 16, 256} (contention spread over k
    counters; k = 256 has the value distribution of the former `noise`). The RQ2
    metric is `log(T_atomic / T_local)` compared between environments
    (ADR 0026).
- **Environments:** native, Chrome (V8), Firefox (SpiderMonkey). The same
  source, compiler and flags are used for all three.

## Design decisions already taken (don't reopen without new data)

- **Hardware and CPU:** official measurements only on the PC, an
  i9-14900KF running Linux.
  - Use P-cores only (8 physical cores, no HT), with a process-level
    `taskset` mask for both native and browser. There is no per-thread
    pinning, because the browser can't do it.
  - Turbo off, governor `performance`.
- **Scaling and SIMD:**
  - Strong scaling: same input for every N; speedup = T1/TN within each
    environment.
  - 128-bit SIMD on both sides: native x86-64 baseline (SSE2, no
    `target-cpu=native`) and WASM `simd128`.
- **Runs and warm-up:**
  - One independent run = one fresh process. For the browser, that means a
    fresh launch with a fresh profile.
  - Warm-up iterations happen inside each run.
  - The unit of analysis is the run, not the iteration (avoid
    pseudo-replication; Georges et al. 2007).
- **Harness:**
  - No automation framework (no Puppeteer/Playwright/CDP during
    measurement).
  - The harness launches the browser binary with `taskset`, a temp profile
    and the config in the URL.
  - The page POSTs results to a local server, which also sends COOP/COEP.
  - Native, Chrome and Firefox runs are interleaved in a random order with a
    recorded seed.
- **Browser builds:** Chrome for Testing (pinned version) and Firefox from
  archive.mozilla.org (pinned version).
- **Contention design:** shared atomic counters are padded to their own cache
  line, `align(128)` (a 64-byte variant was measured in a pilot, ADR 0049, and
  removed). Allocation and reset
  stay outside the timed region (the WASM default allocator has a global
  lock).

## Technical notes

- WASM threads need:
  - Rust nightly with `-Z build-std` and target features
    `+atomics,+bulk-memory,+mutable-globals,+simd128`;
  - wasm-bindgen + wasm-bindgen-rayon;
  - SharedArrayBuffer, which needs cross-origin isolation (COOP/COEP);
  - a dedicated coordinating Web Worker, because the main thread can't
    `Atomics.wait`.
- WASM atomics are always SeqCst, and x86 locked RMW ignores the ordering
  argument. So `Relaxed` vs `SeqCst` makes no difference on our targets.
- `performance.now()` is coarse in the browser. Iterations must be long
  enough (sized in the pilot).
- Every workload produces a checksum, which must match across environments
  and thread counts.

## Workflow

This repository is the final submission: the code, data and documents of
the final build (`measured/v2`). It is built from the working repository
in small PRs; development and the full history happened there.

- **Commits and PR titles:** Conventional Commits, see the
  `conventional-commits` skill. No ticket prefixes.
- **PRs:** small and in sequence, see the `small-pr` skill (size rule,
  description with a Mermaid diagram and the paper figure, how to handle
  the review). You may help with the mechanics (branch, commits, push,
  PR). Never push to `main`; I squash-merge. No Claude/AI attribution
  lines in commits, PRs or GitHub comments, including the
  "Generated with Claude Code" footer (AI use is declared in
  `AI_USE.md`).
- **AI review:** `claude[bot]` reviews each PR as a double check. Minor
  findings are ignored; anything that looks critical comes to me before
  any reply or change.
- **On GitHub:** every comment you post through my account starts with
  `[claude]`. I resolve the threads.
- **Decisions:** every experimental-design or architecture decision has
  an ADR in `docs/adr/`.
- **Machines:** develop on the Mac; take measurements only on the PC.
  Numbers from the Mac are never reported as results.

## Code style

- Comments only when they add information the code cannot carry: why,
  a pitfall, or a reference (link to the paper or algorithm a value or
  method comes from). No ADR numbers in code comments. Never comments that restate the code.
- Named constants instead of magic numbers.
- Every module and submodule has a `README.md`: what it does, which file
  holds what, and a Mermaid flowchart of the flow.
- Python: OOP, one class or concept per module, fully typed; `mypy
  --strict` passes (`make lint`). Rust: one struct or impl per file.
- In `bench/`, the measured path (timed region, workload kernels,
  checksum) may be changed (refactors, new parameters, loop and closure
  rewrites) when an ADR records why. Run `scripts/codegen_diff.sh` and
  write in the ADR which hot functions changed. A change that is not
  codegen-neutral makes a new build: tag it, and never mix its runs with
  earlier builds in one comparison (ADR 0062). Earlier campaigns stay
  valid for their own tagged build.
- Strong types (structs/enums for domain concepts, no loose tuples or
  primitive soup), established patterns, small focused functions,
  well-structured modules.

## Repository layout

| Folder | Contents |
|---|---|
| `bench/` | Rust crate: workloads, native runner, WASM entry |
| `harness/` | Server, browser launcher (no automation framework), environment scripts, orchestrator, campaign specs |
| `analysis/` | Statistical analysis and plots |
| `scripts/` | Repository checks (SIMD, codegen diff, ADRs) |
| `data/` | `raw/<campaign>-v2/` (the measured runs) and `tables/<campaign>-v2/` (tables derived from them) |
| `docs/adr/` | Architecture and experimental-design decisions |
| `paper/` | LaTeX, ACM template: `final/` (the paper), `pilot/` (pilot report), `proposal/`, with shared `figures/`, `bib/` and the kept PDFs in `pdf/` |
