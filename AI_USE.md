# Use of AI

AI tools were used in this project. Every use is disclosed here, and every part
must be explainable by the author.

The pull request descriptions of this repository (summary, Mermaid diagrams and
figure previews) are always written by AI (Claude Code) and reviewed by the
author.

| Date | Tool | What for |
|---|---|---|
| Nov 2026 | Claude | Implementing the SplitMix64 generator (`bench/src/input/split_mix64.rs`) from the published algorithm and its reference constants |
| Nov 2026 | Claude | Writing the Gaussian filter's interior loop (`blur_interior` in `bench/src/workloads/gaussian.rs`) so the compiler can drop the bounds checks and vectorize it |
| Nov 2026 | Claude | Help writing the fork-join calibration (`bench/src/calibration.rs`) and the measurement loop (`bench/src/measurement/measure.rs`) |
| Nov 2026 | Claude | Help with the WebAssembly threads setup: the build flags of `bench/build-wasm.sh`, the coordinating worker and the workers of `bench/www/`, and the cross-origin isolation headers of `harness/server.py` |
| Nov 2026 | Claude | Help writing the confinement of a run to the measured cores with systemd scopes and cgroups (`harness/shield/`, `harness/env/*.sh`) |
| Nov 2026 | Claude | Help writing the statistics from their published definitions: percentile bootstrap, Holm, Mann-Whitney U and Cliff's delta (`analysis/stats/`, `analysis/inference/robustness.py`) |
| Nov 2026 | Claude | Help writing the comparison of two builds' machine code, which normalizes addresses and data offsets in `objdump` listings (`scripts/codegen_diff.py`, `scripts/codegen_diff.sh`) |
| Nov 2026 | Claude | Help writing the capture of the code each engine runs: V8's jitdump (`scripts/capture_chrome.py`, `scripts/chrome_code.py`, `analysis/extras/jitdump.py`) and SpiderMonkey's compiled pages read from the memory of a sampled process (`scripts/capture_firefox.py`, `scripts/firefox_code.py`) |
| Nov 2026 | Claude | Help writing the native probes with hand-written increment sequences in inline assembly (`bench/probes/atomic_increment.c`, `bench/probes/rmw_chain.c`) |
| Nov 2026 | Claude | Help writing the counters of the loop alone, by the difference of two pass counts (`analysis/extras/perf_loop.py`, `scripts/perf-counters.sh`) |
| Nov 2026 | Claude | Running the measuring session of `measured/v3` on the PC: starting each campaign of `scripts/session.sh`, waiting for it and opening the pull request with its data |
| Nov 2026 | Claude | Drafting decision records in `docs/adr/` from the author's decisions and the measured data |
| Nov 2026 | Claude | Reviewing every pull request (`claude[bot]`, `.claude/agents/methodology-reviewer.md`) and the paper against the grading criteria (`.claude/agents/paper-reviewer.md`) |
| Nov 2026 | Claude | Writing the first full draft of the paper (`paper/final/paper.tex`) and of the extended report (`paper/extended/`) from the measured tables and the decision records, with every number checked against its table by a separate review; the author reviewed and edited both |
| Nov 2026 | Claude | Writing the presentation slides (`presentation/`) and the documentation (`docs/explainer/`), with the script that generates the documentation's numbers (`scripts/explainer_data.py`) |

Decisions about the topic, research questions and experimental design are the
author's. Keep this table updated as the project progresses.
