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

Decisions about the topic, research questions and experimental design are the
author's. Keep this table updated as the project progresses.
