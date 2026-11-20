# harness/campaigns

One JSON spec per campaign: every parameter of the campaign, read by
`harness.campaign`. Run one with `make campaign SPEC=harness/campaigns/<file>`;
its runs land in `data/raw/<name>`, where `<name>` is the spec's `name` key.

Only the specs of the final build, `measured/v2`, are here. The pilot specs
and the campaigns of earlier builds stay in the working repository.

## Campaigns of the study

| Spec | What it measures |
|---|---|
| `campaign-v2.json` | The main campaign: filter and both histograms at k 1, 4, 16, 256, N 1 to 8, 30 runs, order seed 20261109 |
| `cutoff-{512,1024,2048,4096,8192}-v2.json`, `cutoff-control-{512,2048}-v2.json` | Speedup against image size (the cutoff), with passes so every timed sample covers 8192^2 pixels |
| `grain-{1024,8192}-v2.json` | The grain sweep: fixed task sizes against Rayon's adaptive split |

## Extras (not part of RQ1 or RQ2)

| Spec | What it measures |
|---|---|
| `extras-v2.json` | Private, shared and packed atomics, the local control, sorts; Firefox runs repeated on 158.0 |
| `weak-v2.json` | Weak scaling, 1024 rows per thread |
| `simd-scalar-v2.json` | Filter, native and WASM without SIMD (`build` `scalar`) |
| `simd-avx2-v2.json` | Filter, native with AVX2 (`build` `avx2`) |
| `hybrid-v2.json` | P+E mask, `"hybrid": true`, N up to 20 |
| `perf-v2.json` | Hardware counters of the atomic histogram (k 1 and 256, N 1 and 8), run by `scripts/perf-counters-v2.sh` |

## End-to-end checks

| Spec | What it does |
|---|---|
| `smoke.json` | Every campaign workload at 1024^2, 2 runs, strict |
| `mini.json` | The same, not strict, no run scope |

## Quick checks (not results)

Tiny copies of the campaigns, run by `make quick*` into `data/raw/quick-*`,
to check that the pipeline works and to watch a run. Each keeps its real
spec's environments, workloads, W, build variant, CPU mask, hybrid flag,
start delay and discarded first launch, and shrinks the rest. All are
`"strict": false` with `"scopeUser": null`, so they run on an unprepared
machine without sudo.

| Spec | Make target | Mirrors |
|---|---|---|
| `quick-rq1.json` | `quick-rq1` | The main campaign, filter at N 1 and 8 |
| `quick-rq2.json` | `quick-rq2` | The main campaign, both histograms at k 1 and 256, N 8 |
| `quick-headless.json`, `quick-ui.json` | `quick-headless`, `quick-ui` | A headless and a headful browser run, filter only |
| `quick-extras.json` | `quick-extras` | `extras-v2.json`, the extra workloads at k 1 |
| `quick-weak.json` | `quick-weak` | `weak-v2.json` at N 1 and 8 |
| `quick-simd-scalar.json`, `quick-simd-avx2.json` | `quick-simd` | The SIMD variants at N 1 and 8 |
| `quick-hybrid.json` | `quick-hybrid` | `hybrid-v2.json` at N 1, 8 and 20 |
| `quick-size-2048.json`, `quick-size-4096.json` | `quick-sizes` | The filter at two smaller sizes |
