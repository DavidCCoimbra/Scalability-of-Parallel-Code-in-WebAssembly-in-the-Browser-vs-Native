# harness/campaigns

One JSON spec per campaign: every parameter of the campaign, read by
`harness.campaign`. Run one with `make campaign SPEC=harness/campaigns/<file>`;
its runs land in `data/raw/<name>`, where `<name>` is the spec's `name` key.

Only the specs of the final build, `measured/v3`, are here, and `make` runs
and reads them by default (`MEASURED`). The specs of `measured/v2` are at the
tag `data/v2`; the pilot specs are not part of this repository.

## Campaigns of the study

| Spec | What it measures |
|---|---|
| `campaign-v3.json` | The main campaign: filter on noise and both histograms at k = 1, 4, 16, 256, N in {1, 2, 4, 6, 7, 8}, 30 runs, with the sequential references `filter-seq` and `hist-seq` at one thread: 5310 runs |
| `gate-v3.json`, `gate2-v3.json` | The cells whose code changed and the filter, 3 runs each, checked before the campaigns (ADR 0087); never results |

## Exploratory campaigns (not part of RQ1 or RQ2)

| Spec | What it measures |
|---|---|
| `tier-v3.json` | Three engine arms (as shipped, baseline compiler only, optimizing compiler only) on the filter and on both histograms at k = 1 and 256, N = 1 and 8 |
| `perf-v3.json` | Hardware counters of the atomic histogram, the filter and the local histogram (k 1 and 256, N 1 and 8), run by `scripts/perf-counters.sh` |
| `perf-loop1-v3.json`, `perf-loop8-v3.json` | The filter and the local histogram (k = 16 and 256) with 1 and with 8 passes per sample; the difference of their counters is the loop alone (ADR 0090). Run with `MEASURED=loop1-v3 scripts/perf-counters.sh` and `MEASURED=loop8-v3 scripts/perf-counters.sh` |
| `simd-scalar-v3.json` | Filter, native and WASM without SIMD (`build` `scalar`) |
| `simd-avx2-v3.json` | Filter, native with AVX2 (`build` `avx2`) |
| `cutoff-{512,1024,2048,4096,8192}-v3.json`, `cutoff-control-{512,2048}-v3.json` | Speedup against image size (the cutoff), with passes so every timed sample covers 8192^2 pixels |
| `grain-threads-v3.json` | The local histogram at k = 16 with the adaptive split and fixed grains of 256 and 1024 KB, at N = 1, 6, 7 and 8 |
| `grain-{1024,8192}-v3.json` | The grain sweep: fixed task sizes against Rayon's adaptive split; the 8192 one includes the atomic histogram |
| `weak-v3.json` | Weak scaling, 1024 rows per thread |
| `extras-v3.json` | Private, shared and packed atomics, the local control, sorts |
| `hybrid-v3.json` | P+E mask, `"hybrid": true`, N up to 20; the machine is prepared with that mask (ADR 0094) |

## End-to-end checks

| Spec | What it does |
|---|---|
| `smoke.json` | Every campaign workload at 1024^2, 2 runs, strict |

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
| `quick-headless.json` | `quick-headless` | One headless browser run per browser, filter only |
| `quick-extras.json` | `quick-extras` | `extras-v3.json`, the extra workloads at k 1 |
| `quick-weak.json` | `quick-weak` | `weak-v3.json` at N 1 and 8 |
| `quick-simd-scalar.json`, `quick-simd-avx2.json` | `quick-simd` | The SIMD variants at N 1 and 8 |
| `quick-hybrid.json` | `quick-hybrid` | `hybrid-v3.json` at N 1, 8 and 20 |
