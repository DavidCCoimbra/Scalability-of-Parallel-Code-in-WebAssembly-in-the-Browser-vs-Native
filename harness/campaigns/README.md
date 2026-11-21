# harness/campaigns

One JSON spec per campaign: every parameter of the campaign, read by
`harness.campaign`. Run one with `make campaign SPEC=harness/campaigns/<file>`;
its runs land in `data/raw/<name>`, where `<name>` is the spec's `name` key.

Only the specs of the final build, `measured/v2`, are here. The pilot specs
and the campaigns of earlier builds stay in the working repository.

## Campaigns of the study

| Spec | What it measures |
|---|---|
| `campaign-v2.json` | The main campaign: filter on noise and both histograms at k = 1, 4, 16, 256, N in {1, 2, 4, 6, 7, 8}, 30 runs, order seed 20261109 |
| `cutoff-{512,1024,2048,4096,8192}-v2.json`, `cutoff-control-{512,2048}-v2.json` | Speedup against image size (the cutoff), with passes so every timed sample covers 8192^2 pixels |
| `grain-{1024,8192}-v2.json` | The grain sweep: fixed task sizes against Rayon's adaptive split |

## Campaigns of the v3 build (ADR 0084)

Every v2 spec has a `-v3` twin with a new order seed, and `make` runs and reads them with
`MEASURED=v3`. What differs from v2:

| Spec | Difference |
|---|---|
| `campaign-v3.json` | Adds the sequential references `filter-seq` and `hist-seq` (k = 1, 4, 16, 256), at one thread: 5310 runs |
| `tier-v3.json` | New: three engine arms (as shipped, baseline compiler only, optimizing compiler only) on the filter and on both histograms at k = 1, N = 1 and 8 |
| `grain-threads-v3.json` | New: the local histogram at k = 16 with the adaptive split and fixed grains of 256 and 1024 KB, at N = 1, 6, 7 and 8 |
| `grain-8192-v3.json` | Adds the atomic histogram at the grains of the local one; `grain-1024-v3.json` cannot (it needs passes) |
| `perf-v3.json` | Adds the filter and the local histogram at k = 256; the script counts two cache events more |
| `gate-v3.json` | New: the cells whose code changed and the filter, 3 runs each, checked before the campaigns; never results |

## Extras (not part of RQ1 or RQ2)

| Spec | What it measures |
|---|---|
| `extras-v2.json` | Private, shared and packed atomics, the local control, sorts |
| `weak-v2.json` | Weak scaling, 1024 rows per thread |
| `simd-scalar-v2.json` | Filter, native and WASM without SIMD (`build` `scalar`) |
| `simd-avx2-v2.json` | Filter, native with AVX2 (`build` `avx2`) |
| `hybrid-v2.json` | P+E mask, `"hybrid": true`, N up to 20 |
| `perf-v2.json` | Hardware counters of the atomic histogram (k 1 and 256, N 1 and 8), run by `scripts/perf-counters.sh` |

Firefox updated itself from 158.0 to 160.0 in the middle of the extras
campaigns. Their Firefox runs were run again on a reinstalled 158.0, each in
its planned position; the kept runs report 158.0 in their context, and the
160.0 runs are kept apart in `excluded/` in each campaign's data folder.

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
| `quick-extras.json` | `quick-extras` | `extras-v2.json`, the extra workloads at k 1 |
| `quick-weak.json` | `quick-weak` | `weak-v2.json` at N 1 and 8 |
| `quick-simd-scalar.json`, `quick-simd-avx2.json` | `quick-simd` | The SIMD variants at N 1 and 8 |
| `quick-hybrid.json` | `quick-hybrid` | `hybrid-v2.json` at N 1, 8 and 20 |
