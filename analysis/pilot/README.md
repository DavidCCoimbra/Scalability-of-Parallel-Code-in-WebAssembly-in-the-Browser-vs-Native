# analysis.pilot

The rules that sized the campaign from the pilot data. They are kept to
reproduce the pilot decisions, not run on the campaign.

| Module | Decision |
|---|---|
| `warmup.py` | Warm-up W per workload from long runs without warm-up |
| `run_count.py` | Runs per configuration from the half-width of the Bonferroni interval of every primary-style contrast over subsamples |
| `iteration_count.py` | Measured iterations per run from how often the first M iterations agree with the rest |

```mermaid
flowchart LR
    raw["data/raw/pilot-*"] --> series["warmup.load_series<br/>measured iterations per run"]
    series --> warmup["warmup.campaign_warmups<br/>W per workload"]
    warmup --> iterations["iteration_count.iteration_agreement"]
    raw --> collect["harness.collect"] --> runs["runs.run_summaries"] --> widths["run_count.contrast_widths"]
    widths --> choice["run_count.choose_runs<br/>extrapolated_runs"]
    warmup --> figure["figures.warmup<br/>paper/figures/warmup-n*.pdf"]
```

The commands are `analysis.warmup`, `analysis.runcount` and
`analysis.plot_warmup`; `analysis.compare` compares two pilots.
