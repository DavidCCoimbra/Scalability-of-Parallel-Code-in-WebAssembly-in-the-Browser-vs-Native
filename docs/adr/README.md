# Architecture and experimental-design decision records

Every architecture and experimental-design decision of the study is recorded here: the problem
it answered, what was decided and why, and what followed from it. A decision is changed only
by a later record that amends or supersedes it, so the records are read in order and the Status
of each says which later one changed it.

Records about the measuring environment, the harness and the analysis plan come first; the
pilot decisions, the extras and their results, the cutoff and grain campaigns and the final
build (`measured/v2`, ADR 0069) follow.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-p-cores-only.md) | Measure on P-cores only, with a process-level affinity mask | Accepted; amended by ADR 0045 |
| [0002](0002-turbo-off-performance-governor.md) | Turbo boost off and governor `performance` | Accepted |
| [0003](0003-strong-scaling.md) | Strong scaling with speedup T1/TN per environment | Accepted |
| [0004](0004-simd-128-both-sides.md) | 128-bit SIMD on both sides | Accepted |
| [0005](0005-fresh-process-per-run.md) | One fresh process per run, warm-up inside the run, run as unit of analysis | Accepted |
| [0006](0006-harness-without-automation.md) | Harness without a browser automation framework | Accepted |
| [0007](0007-pinned-browser-builds.md) | Pinned browser builds | Accepted; versions set by ADR 0021 |
| [0008](0008-padded-shared-atomics.md) | Padded shared atomic counters, allocation outside the timed region | Accepted; amended by ADR 0049 |
| [0009](0009-pinned-nightly-toolchain.md) | Pinned nightly Rust toolchain with `-Z build-std` for WASM threads | Accepted |
| [0010](0010-workflow-adrs-notion.md) | Development workflow: PRs with CI and AI review, ADRs mirrored to Notion | Accepted; Notion part superseded by ADR 0063 |
| [0011](0011-deterministic-grayscale-inputs.md) | Deterministic grayscale inputs with a fixed seed | Accepted |
| [0012](0012-gaussian-integer-kernel.md) | Gaussian 3x3 filter with an integer kernel, row-parallel | Accepted; amended by ADR 0017 |
| [0013](0013-histogram-privatized-control.md) | Histogram control with per-task privatization over 64 KiB chunks | Accepted |
| [0014](0014-atomic-histogram-prepare-relaxed.md) | Atomic histogram with a prepare step and Relaxed ordering | Accepted |
| [0015](0015-shared-measurement-loop.md) | Shared measurement loop with an injected clock | Accepted; amended by ADR 0018 and ADR 0032 and ADR 0030 |
| [0016](0016-native-runner-csv-schema.md) | Native runner and the shared CSV result schema | Accepted; amended by ADR 0018 and ADR 0032, ADR 0027 (input |
| [0017](0017-simd-parity-verification.md) | SIMD parity verified on the built artifacts | Accepted |
| [0018](0018-wasm-entry.md) | WASM entry configured by the URL query, with a shared config parser | Accepted |
| [0019](0019-local-results-server.md) | Local results server with cross-origin isolation | Accepted; amended by ADR 0027, ADR 0028, ADR 0031 and ADR 0032 |
| [0020](0020-benchmark-page-protocol.md) | Benchmark page protocol | Accepted |
| [0021](0021-browser-versions.md) | Browser versions pinned to Chrome for Testing 155.0.8059.84 and Firefox 158.0 | Accepted |
| [0022](0022-browser-launcher.md) | Browser launcher with a fresh profile, taskset and no automation | Accepted; amended by ADR 0029 and ADR 0031 (page URL, |
| [0023](0023-result-context.md) | Context recorded with every result | Accepted; amended by ADR 0025, ADR 0027 (provenance and drift keys, |
| [0024](0024-browser-correctness-ci.md) | Browser correctness checked in CI against native | Accepted; amended by ADR 0032 |
| [0025](0025-smt-off.md) | SMT off, one CPU per physical P-core, checked on every result | Accepted |
| [0026](0026-rq2-metric-and-contention-sweep.md) | RQ2 metric and contention sweep, fixed before the pilot | Accepted |
| [0027](0027-provenance-and-failed-runs.md) | Provenance, drift context and failed-run records | Accepted; amends ADR 0016, ADR 0019 and ADR 0023 |
| [0028](0028-shield-the-measured-cpus.md) | Shield the measured CPUs and record foreign CPU time | Accepted; amends ADR 0023 |
| [0029](0029-quiet-browsers-and-start-delay.md) | Symmetric quiet browser settings and a recorded start delay | Accepted; amends ADR 0022 and ADR 0023 |
| [0030](0030-fork-join-calibration.md) | Warm and cold fork-join calibration inside every run | Accepted; amends ADR 0015 and ADR 0016 |
| [0031](0031-harness-robustness.md) | Harness robustness: unique run ids, exact versions, loopback address, leftover processes | Accepted; amends ADR 0019, ADR 0022 and |
| [0032](0032-adr-consistency.md) | ADRs brought in line with the code | Accepted; amends ADR 0011, ADR 0015, ADR 0016, ADR 0019 and ADR 0024 |
| [0033](0033-run-id-joined-by-the-analysis.md) | The run id is joined by the analysis, not stored in the CSV | Accepted |
| [0034](0034-campaign-orchestrator.md) | Campaign orchestrator with a seeded interleaved order and resume | Accepted; amended by ADR 0040 |
| [0035](0035-environment-setup-and-check.md) | Environment setup and check before every session | Accepted; amended by ADR 0040 |
| [0036](0036-analysis-v0.md) | Analysis v0: one value per run, relative speedup with bootstrap intervals | Accepted; amended by ADR 0037 |
| [0037](0037-analysis-plan.md) | Analysis plan fixed before the campaign | Accepted |
| [0038](0038-inference-from-the-analysis-plan.md) | Inference implemented from the analysis plan | Accepted; amended by ADR 0039 |
| [0039](0039-absolute-times-and-clock-check.md) | Absolute time ratios and a clock resolution warning | Accepted; amends ADR 0037 and ADR 0038; amended by ADR 0041 |
| [0040](0040-campaign-enforces-the-environment.md) | The campaign enforces the environment check on every start | Accepted; amends ADR 0034 and ADR 0035 |
| [0041](0041-image-size-and-clock-factor.md) | Image size 8192x8192 and a clock factor of 100 | Accepted; amends ADR 0037 and ADR 0039 |
| [0042](0042-quiet-mode-before-measuring.md) | Quiet mode before measuring and no sleep during a campaign | Accepted |
| [0043](0043-warm-up-per-workload.md) | Warm-up W per workload, the same in every environment | Accepted |
| [0044](0044-thread-counts.md) | Thread counts N = 1, 2, 4, 6, 7, 8 | Accepted |
| [0045](0045-p-cores-confirmed-and-browser-scope.md) | P-cores only, confirmed by a pilot, and every browser process in the run scope | Accepted; amends ADR 0001 and ADR 0028; amended by ADR 0048 (the |
| [0046](0046-headless.md) | Headless browsers, with the difference to headful measured | Accepted |
| [0047](0047-runs-and-iterations.md) | 30 runs per configuration and 10 measured iterations per run | Accepted; sets the value left open by ADR 0037. Amended by ADR 0048 |
| [0048](0048-start-delay.md) | A 3 s start delay for every browser run | Accepted; amends ADR 0029, ADR 0043, ADR 0044, ADR 0045 and ADR 0047 |
| [0049](0049-padding-and-atomic-code.md) | 128-byte padding kept, and why Chrome's atomics behave differently | Accepted; amends ADR 0008 |
| [0050](0050-chrome-for-testing-matches-stable.md) | Chrome for Testing gives the same numbers as Chrome stable | Accepted |
| [0051](0051-foreign-cpu-threshold-and-data-check.md) | Foreign CPU threshold of 0.25 s and the data check before analysis | Accepted; sets the value left open by ADR 0037 |
| [0052](0052-extras-design.md) | Design of the extra experiments | Accepted |
| [0053](0053-extras-campaign-parameters.md) | Parameters of the extras campaign | Accepted |
| [0054](0054-extras-results.md) | Results of the extras campaign | Accepted |
| [0055](0055-weak-scaling-campaign.md) | Weak scaling campaign | Accepted |
| [0056](0056-weak-scaling-results.md) | Weak scaling results | Accepted |
| [0057](0057-simd-campaigns.md) | SIMD campaigns | Accepted |
| [0058](0058-simd-results.md) | SIMD results | Accepted |
| [0059](0059-hybrid-campaign.md) | Hybrid P+E campaign | Accepted |
| [0060](0060-local-histogram-k1-instruction-choice.md) | Why Chrome beats native on the local histogram at k = 1 | Accepted |
| [0061](0061-hybrid-results.md) | Results of the hybrid P+E campaign | Accepted |
| [0062](0062-bench-refactor-codegen-neutral.md) | A readability refactor of the bench, limited to codegen-neutral changes | Accepted |
| [0063](0063-notion-replaced-by-markdown.md) | Notion replaced by Markdown files in the repository | Accepted; supersedes the Notion part of ADR 0010 |
| [0064](0064-cutoff-campaign.md) | Cutoff campaign, with K passes per timed sample | Accepted |
| [0065](0065-cutoff-results.md) | Results of the cutoff campaign | Accepted |
| [0066](0066-cutoff-phase2-grain-sweep.md) | Cutoff phase 2, a grain-size sweep (U-curve) | Accepted |
| [0067](0067-grain-sweep-results.md) | Results of the grain sweep (U-curve) | Accepted |
| [0068](0068-perf-counters-for-diagnostics.md) | Hardware counters made readable for the diagnostics | Accepted |
| [0069](0069-v2-build.md) | The v2 build: measurement corrections, refactor and new settings | Accepted |
| [0070](0070-quiet-campaigns.md) | Campaigns run in quiet mode, with the coding assistant stopped | Accepted |
| [0071](0071-firefox-pin-guard.md) | Firefox cannot update itself, and a campaign checks the pinned browser versions first | Accepted |
| [0072](0072-perf-counters-v2.md) | Hardware counters of the atomic histogram on measured/v2 | Accepted |
| [0073](0073-explainer-documentation.md) | Documentation as a multi-page explainer | Accepted. The explainer lives in the working repository |
| [0074](0074-explainer-for-juniors.md) | The explainer is written for juniors first, in two layers | Accepted. The explainer lives in the working repository |
