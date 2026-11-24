# analysis

Statistics and figures of the study: the same Rust/Rayon code measured
natively and as WebAssembly in Chrome and Firefox. Everything here reads the
raw runs of a campaign (`data/raw/<campaign>`) and writes tables to `data/`
and figures to `paper/figures/`. The statistics are fixed by the analysis
plan, written before the campaign data.

## Layout

The top-level modules are the commands; the subpackages are the library they
call. Every command runs as `python3 -m analysis.<command>` (the figure
commands through `uv run --no-project --with matplotlib`, see `Makefile`).

| Command | What it writes |
|---|---|
| `datacheck` | Data quality report of a campaign |
| `sequential` | The speedup against sequential code, from the sequential references of a campaign (`filter-seq`, `hist-seq`) |
| `gate` | The gate before a build's campaigns: exits 1 unless a gate campaign is fit to start from |
| `v0` | Speedup and efficiency per configuration, `<campaign>-scaling.csv` |
| `results` | The plan's RQ1, RQ2 and absolute contrasts, `<campaign>-contrasts.csv`, and the shape table |
| `sensitivity` | The plan's sensitivity checks side by side on the 10 primary contrasts (per-run mean, median centre, no foreign-CPU exclusion) and whether each decision is robust, `<campaign>-sensitivity.csv` |
| `rq2_decomposition` | Post hoc: the two factors of each primary RQ2 ratio (atomic and local time, browser over native) and the ratio of the excesses (atomic - local), `<campaign>-rq2-decomposition.csv` |
| `calibration` | Fork-join cost per environment, N, probe and phase from the calibration samples, over all runs and per workload, `<campaign>-fork-join.csv` |
| `robustness` | Mann-Whitney U and Cliff's delta on the 10 primary contrasts, Holm-adjusted, against the bootstrap decisions, `<campaign>-robustness.csv` |
| `throughput` | Post hoc: nanoseconds per pixel, megapixels per second and the absolute speedup T(native, 1) / T(environment, N) per configuration, `<campaign>-throughput.csv` (ADR 0082) |
| `karp_flatt` | Karp-Flatt serial fraction per configuration from a scaling table, `<campaign>-karp-flatt.csv` |
| `distributions` | Violins of the per-run medians for the filter and the atomic histogram, `<campaign>-distributions.pdf`, and their quartiles, `<campaign>-distributions.csv` |
| `iteration_drift` | First over last measured iterations per configuration |
| `extras.perf_counters` | Extra: hardware counters per atomic operation per run, from the perf-v3 campaign and its 100 ms perf intervals |
| `figures` | Speedup, efficiency, absolute ratio and RQ2 figures of a campaign |
| `extras.build_variants` | Extra: SIMD build variants table and figure |
| `cutoff` | Cutoff campaigns: table, break-even and worth-it sizes, fork-join model, figure |
| `grain` | Grain sweep campaigns: U-curve points, best grain and flat region, 100:1 grain, figure. `datacheck` pools the grains of a configuration, so its order-drift lines mix grains |
| `extras.jitdump` | Extra: one function's machine code from a V8 jitdump |

| Module or package | Concept |
|---|---|
| `configuration.py` | A configuration (environment, workload, input, k, N) and the names the plan refers to |
| `runs.py` | One value per run from the measured iterations |
| `campaign.py` | What a campaign directory holds: run contexts, `campaign.json`, pinned browsers |
| `run_context.py` | `RunContext`: the context JSON of one run, each field read with one type and one default |
| `loading.py` | The one way a command reads a campaign: collect, stop on a checksum conflict, apply the plan's exclusions (ADR 0081) |
| `provenance.py` | Commit and time stamp of a generated sidecar |
| `stats/` | Generic statistics: summaries, bootstrap, Holm, Spearman, skewness, Cliff's delta, Mann-Whitney U |
| `scaling/` | Speedup and efficiency tables |
| `inference/` | The plan's contrasts and the primary family |
| `quality/` | Clock, foreign CPU, order drift and iteration drift checks |
| `figures/` | matplotlib figures |
| `tests/` | unittest suite (`python3 -m unittest discover -s analysis/tests -t .`) |

## Data flow

```mermaid
flowchart LR
    raw["data/raw/&lt;campaign&gt;<br/>run CSV + run JSON + campaign.json"]
    collect["harness.collect<br/>one row per iteration, checksum check"]
    runs["runs.run_summaries<br/>median per run (D1)"]
    quality["quality/<br/>clock, foreign CPU, drift"]
    scaling["scaling/<br/>geometric centre (D2), T1 / TN, bootstrap (D3)"]
    exclusion["inference/exclusion<br/>foreign CPU, strict validation (D7)"]
    contrasts["inference/<br/>RQ1, RQ2, ABS, Holm (D4 to D8)"]
    report["data/&lt;campaign&gt;-quality.md"]
    scalingcsv["data/&lt;campaign&gt;-scaling.csv + .json"]
    contrastcsv["data/&lt;campaign&gt;-contrasts.csv + .json<br/>data/&lt;campaign&gt;-shape.csv"]
    figures["figures/<br/>paper/figures/&lt;prefix&gt;-*.pdf"]

    raw --> collect --> exclusion --> runs
    raw --> quality
    collect --> quality --> report
    runs --> scaling --> scalingcsv
    runs --> contrasts --> contrastcsv
    scaling --> figures
    runs --> figures
```

Every command that writes a table or a figure reads its campaign through
`loading.load_campaign`, which removes the excluded runs before the run
summaries are taken (ADR 0081); each takes `--strict` and
`--foreign-cpu-threshold`. `datacheck` and `iteration_drift` are diagnostics
of the data as recorded and read every run that did not fail.

## Conventions

- The run is the unit of analysis (Georges et al. 2007,
  https://doi.org/10.1145/1297027.1297033): iterations are summarised inside
  a run before any statistic across runs.
- Speedup is always relative to N = 1 of the same environment,
  and is read next to the absolute browser / native time (Hoefler
  and Belli 2015, https://doi.org/10.1145/2807591.2807644).
- Bootstrap: 95 % percentile intervals, 10 000 resamples, seed `0x5EED`,
  groups resampled independently (`stats/bootstrap.py`).
- Sidecar JSON files keep a fixed key order, so regenerating them changes
  only `commit` and `createdAt`.
- Type checking: `uv run --no-project --with mypy --with matplotlib mypy --strict analysis`.
