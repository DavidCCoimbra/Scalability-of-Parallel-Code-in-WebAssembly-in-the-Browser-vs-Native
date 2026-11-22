# Architecture and experimental-design decision records

Every architecture and experimental-design decision of the study is recorded here: the problem
it answered, what was decided and why, and what followed from it. A decision is changed only
by a later record that amends or supersedes it, so the records are read in order and the Status
of each says which later one changed it.

Records about the measuring environment, the harness and the analysis plan come first; the
pilot decisions, the extras and their results, the cutoff and grain campaigns and the final
build (`measured/v2`, ADR 0069) follow.

The records of the extra experiments (0052 to 0059 and 0061: exploratory campaigns outside RQ1
and RQ2) are in [`extras/`](extras/README.md). They keep their numbers, so every reference
between records reads the same.

Some records cite evidence that stays in the working repository and is not part of this one:
the one-off probes under `data/probes/`, pilot and v1 data, and pull request numbers (`PR #77`).
Each record says so where it cites them; the measured data behind the paper is
`data/raw/*-v2`.

## Notation and sources

The records were written over several weeks, so a few symbols changed meaning:

- **K** is the number of measured iterations in ADR 0015 and ADR 0016, and the number of passes
  per timed sample from ADR 0064 on.
- **W** is the warm-up count, except in ADR 0016, where `--width W` is the image width, and in
  the fork-join model of ADR 0064 (TN = W / N + F), where it is the work of one region.
- **F**, the fork-join cost, is quoted with different values because the records took it from
  different builds, campaigns and statistics; each names its source, and ADR 0076 gives the
  values of the main campaign of `measured/v2`.
- ADR 0063, 0073 and 0074 record tooling of the working repository (Notion, the explainer),
  which is not part of this one.
- The result records 0054, 0056, 0058, 0061, 0065 and 0067 hold the numbers of the build they
  were first measured on and say so; the numbers of `measured/v2` are listed in ADR 0079, with
  their tables in `data/tables/*-v2`.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-p-cores-only.md) | Measure on P-cores only, with a process-level affinity mask | Accepted; amended by ADR 0045 (confirmed with pilot data) |
| [0002](0002-turbo-off-performance-governor.md) | Turbo boost off and governor `performance` | Accepted |
| [0003](0003-strong-scaling.md) | Strong scaling with speedup T1/TN per environment | Accepted |
| [0004](0004-simd-128-both-sides.md) | 128-bit SIMD on both sides | Accepted |
| [0005](0005-fresh-process-per-run.md) | One fresh process per run, warm-up inside the run, run as unit of analysis | Accepted |
| [0006](0006-harness-without-automation.md) | Harness without a browser automation framework | Accepted |
| [0007](0007-pinned-browser-builds.md) | Pinned browser builds | Accepted; versions set by ADR 0021 |
| [0008](0008-padded-shared-atomics.md) | Padded shared atomic counters, allocation outside the timed region | Accepted; amended by ADR 0049 and ADR 0075 (pad64 removed) |
| [0009](0009-pinned-nightly-toolchain.md) | Pinned nightly Rust toolchain with `-Z build-std` for WASM threads | Accepted; amended by ADR 0076 (what differs below the shared source) |
| [0010](0010-workflow-adrs-notion.md) | Development workflow: PRs with CI and AI review, ADRs mirrored to Notion | Accepted; Notion part superseded by ADR 0063 |
| [0011](0011-deterministic-grayscale-inputs.md) | Deterministic grayscale inputs with a fixed seed | Accepted; amended by ADR 0026 (inputs described by k, not as low/high contention; histograms sweep k in {1, 4, 16, 256}), ADR 0027 and ADR 0032 (input fingerprint recorded and compared in the browser CI job) |
| [0012](0012-gaussian-integer-kernel.md) | Gaussian 3x3 filter with an integer kernel, row-parallel | Accepted; amended by ADR 0017 (interior loop in `u16`, shared kernel table) |
| [0013](0013-histogram-privatized-control.md) | Histogram control with per-task privatization over 64 KiB chunks | Accepted |
| [0014](0014-atomic-histogram-prepare-relaxed.md) | Atomic histogram with a prepare step and Relaxed ordering | Accepted |
| [0015](0015-shared-measurement-loop.md) | Shared measurement loop with an injected clock | Accepted; amended by ADR 0018 and ADR 0032 (global pool, no `install`) and ADR 0030 (fork-join calibration before the warm-up) |
| [0016](0016-native-runner-csv-schema.md) | Native runner and the shared CSV result schema | Accepted; amended by ADR 0018 and ADR 0032 (global pool, no `install`), ADR 0027 (input fingerprint column) and ADR 0030 (calibration phases) |
| [0017](0017-simd-parity-verification.md) | SIMD parity verified on the built artifacts | Accepted |
| [0018](0018-wasm-entry.md) | WASM entry configured by the URL query, with a shared config parser | Accepted |
| [0019](0019-local-results-server.md) | Local results server with cross-origin isolation | Accepted; amended by ADR 0027, ADR 0028 (server on the E-cores), ADR 0031 and ADR 0032 |
| [0020](0020-benchmark-page-protocol.md) | Benchmark page protocol | Accepted |
| [0021](0021-browser-versions.md) | Browser versions pinned to Chrome for Testing 155.0.8059.84 and Firefox 158.0 | Accepted |
| [0022](0022-browser-launcher.md) | Browser launcher with a fresh profile, taskset and no automation | Accepted; amended by ADR 0029 (quiet browser settings, start delay) and ADR 0031 (page URL, leftover check) |
| [0023](0023-result-context.md) | Context recorded with every result | Accepted; amended by ADR 0025 (SMT and mask topology keys), ADR 0027 (provenance and drift keys, failed-run records), ADR 0028 (shield and foreign CPU time), ADR 0029 (start delay) and ADR 0031 (exact version, leftover processes) |
| [0024](0024-browser-correctness-ci.md) | Browser correctness checked in CI against native | Accepted; amended by ADR 0032 (input fingerprints compared too) |
| [0025](0025-smt-off.md) | SMT off, one CPU per physical P-core, checked on every result | Accepted |
| [0026](0026-rq2-metric-and-contention-sweep.md) | RQ2 metric and contention sweep, fixed before the pilot | Accepted; amended by ADR 0078 (the ratio is shown with its two factors) |
| [0027](0027-provenance-and-failed-runs.md) | Provenance, drift context and failed-run records | Accepted; amends ADR 0016 (CSV header), ADR 0019 (`POST /errors`) and ADR 0023 (context keys) |
| [0028](0028-shield-the-measured-cpus.md) | Shield the measured CPUs and record foreign CPU time | Accepted; amends ADR 0023 (context keys) |
| [0029](0029-quiet-browsers-and-start-delay.md) | Symmetric quiet browser settings and a recorded start delay | Accepted; amends ADR 0022 (launcher settings) and ADR 0023 (context keys) |
| [0030](0030-fork-join-calibration.md) | Warm and cold fork-join calibration inside every run | Accepted; amends ADR 0015 (run layout) and ADR 0016 (phases in the CSV); amended by ADR 0076 (20 samples in the v2 campaigns) |
| [0031](0031-harness-robustness.md) | Harness robustness: unique run ids, exact versions, loopback address, leftover processes | Accepted; amends ADR 0019 (exclusive metadata), ADR 0022 (page URL, leftover check) and ADR 0023 (exact version check, `leftoverProcesses`) |
| [0032](0032-adr-consistency.md) | ADRs brought in line with the code | Accepted; amends ADR 0011, ADR 0015, ADR 0016, ADR 0019 and ADR 0024 |
| [0033](0033-run-id-joined-by-the-analysis.md) | The run id is joined by the analysis, not stored in the CSV | Accepted |
| [0034](0034-campaign-orchestrator.md) | Campaign orchestrator with a seeded interleaved order and resume | Accepted; amended by ADR 0040 (environment check enforced on every start) |
| [0035](0035-environment-setup-and-check.md) | Environment setup and check before every session | Accepted; amended by ADR 0040 (environment check enforced on every start) |
| [0036](0036-analysis-v0.md) | Analysis v0: one value per run, relative speedup with bootstrap intervals | Accepted; amended by ADR 0037 (defaults fixed by the analysis plan) |
| [0037](0037-analysis-plan.md) | Analysis plan fixed before the campaign | Accepted; amends ADR 0036 (analysis defaults); amended by ADR 0039 (absolute time ratios, clock check) and ADR 0041 (clock factor, image size); amended by ADR 0077 (sensitivity checks run, RQ1 for Chrome not robust) |
| [0038](0038-inference-from-the-analysis-plan.md) | Inference implemented from the analysis plan | Accepted; amended by ADR 0039 (absolute time ratios, clock check); amended by ADR 0077 (sensitivity checks run, RQ1 for Chrome not robust) |
| [0039](0039-absolute-times-and-clock-check.md) | Absolute time ratios and a clock resolution warning | Accepted; amends ADR 0037 and ADR 0038; amended by ADR 0041 (image size, clock factor of 100) |
| [0040](0040-campaign-enforces-the-environment.md) | The campaign enforces the environment check on every start | Accepted; amends ADR 0034 (orchestrator) and ADR 0035 (environment check) |
| [0041](0041-image-size-and-clock-factor.md) | Image size 8192x8192 and a clock factor of 100 | Accepted; amends ADR 0037 and ADR 0039 |
| [0042](0042-quiet-mode-before-measuring.md) | Quiet mode before measuring and no sleep during a campaign | Accepted |
| [0043](0043-warm-up-per-workload.md) | Warm-up W per workload, the same in every environment | Accepted; amended by ADR 0048 (the slow first iterations of Firefox `hist-local` k = 1 at N = 8 may be browser start-up work rather than tier-up; W stays) |
| [0044](0044-thread-counts.md) | Thread counts N = 1, 2, 4, 6, 7, 8 | Accepted; amended by ADR 0048 (with a 3 s start delay no browser shows a knee; the knee most likely came from Firefox start-up work, and oversubscription stays a smaller possible threat) |
| [0045](0045-p-cores-confirmed-and-browser-scope.md) | P-cores only, confirmed by a pilot, and every browser process in the run scope | Accepted; amends ADR 0001 (confirms it with pilot data) and ADR 0028; amended by ADR 0048 (the Firefox `hist-local` k16 gain under P+E at N = 8 is most likely browser start-up work, which then had more cores) |
| [0046](0046-headless.md) | Headless browsers, with the difference to headful measured | Accepted |
| [0047](0047-runs-and-iterations.md) | 30 runs per configuration and 10 measured iterations per run | Accepted; sets the value left open by ADR 0037. Amended by ADR 0048. |
| [0048](0048-start-delay.md) | A 3 s start delay for every browser run | Accepted; amends ADR 0029, ADR 0043, ADR 0044, ADR 0045 and ADR 0047 |
| [0049](0049-padding-and-atomic-code.md) | 128-byte padding kept, and why Chrome's atomics behave differently | Accepted; amends ADR 0008; the pad64 feature was removed by ADR 0075 |
| [0050](0050-chrome-for-testing-matches-stable.md) | Chrome for Testing gives the same numbers as Chrome stable | Accepted |
| [0051](0051-foreign-cpu-threshold-and-data-check.md) | Foreign CPU threshold of 0.25 s and the data check before analysis | Accepted; sets the value left open by ADR 0037 (D7) |
| [0052](extras/0052-extras-design.md) | Design of the extra experiments | Accepted |
| [0053](extras/0053-extras-campaign-parameters.md) | Parameters of the extras campaign | Accepted |
| [0054](extras/0054-extras-results.md) | Results of the extras campaign | Accepted |
| [0055](extras/0055-weak-scaling-campaign.md) | Weak scaling campaign | Accepted |
| [0056](extras/0056-weak-scaling-results.md) | Weak scaling results | Accepted |
| [0057](extras/0057-simd-campaigns.md) | SIMD campaigns | Accepted |
| [0058](extras/0058-simd-results.md) | SIMD results | Accepted |
| [0059](extras/0059-hybrid-campaign.md) | Hybrid P+E campaign | Accepted |
| [0060](0060-local-histogram-k1-instruction-choice.md) | Why Chrome beats native on the local histogram at k = 1 | Accepted |
| [0061](extras/0061-hybrid-results.md) | Results of the hybrid P+E campaign | Accepted |
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
| [0073](0073-explainer-documentation.md) | Documentation as a multi-page explainer | Accepted. The explainer lives in the working repository. |
| [0074](0074-explainer-for-juniors.md) | The explainer is written for juniors first, in two layers | Accepted. The explainer lives in the working repository. |
| [0075](0075-pad64-feature-removed.md) | The pad64 feature is removed from the bench, codegen-neutral | Accepted; amends ADR 0008 and ADR 0049 |
| [0076](0076-below-the-shared-source.md) | What differs below the shared source, and what the v2 calibration measured | Accepted; amends ADR 0009 and ADR 0030 |
| [0077](0077-sensitivity-checks-on-campaign-v2.md) | The plan's sensitivity checks, run on the main campaign of measured/v2 | Accepted; amends ADR 0037 and ADR 0038 |
| [0078](0078-reading-the-rq2-ratio.md) | How the RQ2 ratio is read: its two factors, and what moves it | Accepted; amends ADR 0026 |
| [0079](0079-results-on-measured-v2.md) | The results on measured/v2, in one place | Accepted |
| [0080](0080-threats-to-validity.md) | The threats to validity that are declared with the results | Accepted |
| [0081](0081-one-loader-for-every-analysis-command.md) | Every analysis command reads a campaign through one loader, with the plan's exclusions | Accepted |
| [0082](0082-throughput-and-absolute-speedup.md) | Throughput and the absolute speedup are tabulated next to the relative speedup | Accepted |
| [0083](0083-recorded-host-state-and-build-inputs.md) | The host state and the build inputs that were not recorded are recorded from now on | Accepted |
| [0084](0084-v3-design.md) | The v3 build and its campaigns: what changes, what is asked and how the session runs | Accepted; amended by ADR 0085 |
| [0085](0085-per-core-check.md) | The per-core check: the degraded core is sound on the prepared PC, and what follows | Accepted; amends ADR 0084, ADR 0077 and ADR 0080 |
| [0086](0086-v3-build.md) | The v3 build: what changed in the measured code and what the compiler made of it | Accepted |
| [0087](0087-gate-of-the-v3-build.md) | The gate of the v3 build: one cell fails the drift criterion twice, and what it is | Accepted; amends ADR 0070 |
| [0088](0088-what-explains-the-results.md) | What explains the results: the open questions, what tests each, and what it would show | Accepted; amends ADR 0084 |
| [0089](0089-tier-and-atomic-increment-results.md) | What the tier campaign and the atomic increment probe show (questions 6 and 7) | Accepted |
