# paper

The paper of the study, in the ACM `sigplan` template of the course (5 pages of content plus 2 of
references). Every number in it is from the build `measured/v3`.

| Path | What it holds |
|---|---|
| `final/paper.tex` | The paper |
| `extended/extended.tex`, `extended/sections/*.tex` | The extended report: the long version of the paper, with every campaign, probe, pilot decision and problem of the study, and no page limit |
| `extended/make_tables.py` | Writes the tables of the extended report from `data/tables/*-v3`, `data/probes` and the campaign journals |
| `extended/tables/*.tex` | The generated tables; never edited by hand |
| `bib/referencias.bib` | The references of the paper |
| `figures/*.pdf` | The figures, written by the result targets from `data/raw/*-v3` (`make all-results`); never edited by hand |
| `pdf/paper.pdf` | The compiled paper that is kept |
| `pdf/extended.pdf` | The compiled extended report that is kept |

## Building it

```sh
make all-results                      # the figures, from the measured runs
cd paper/final && tectonic -X compile paper.tex --outdir ../pdf

python3 paper/extended/make_tables.py # the tables of the extended report
cd paper/extended && tectonic -X compile extended.tex --outdir ../pdf
```

`latexmk -pdf paper.tex` works as well; the PDFs built next to the sources are ignored by git.

## Where each part of the paper comes from

```mermaid
flowchart LR
    raw[("data/raw/*-v3")] --> analysis["analysis: make all-results"]
    analysis --> tables[("data/tables/*-v3")]
    analysis --> figures["paper/figures/*.pdf"]
    probes[("data/probes")] --> adr["docs/adr 0084 to 0095"]
    tables --> adr
    tables --> tex["paper/final/paper.tex"]
    adr --> tex
    figures --> tex
    bib["paper/bib/referencias.bib"] --> tex
    tex --> pdf["paper/pdf/paper.pdf"]
    tables --> gen["paper/extended/make_tables.py"]
    probes --> gen
    gen --> long["paper/extended/extended.tex"]
    adr --> long
    figures --> long
    bib --> long
    long --> longpdf["paper/pdf/extended.pdf"]
```

| In the paper | Source |
|---|---|
| Run counts, exclusions, order trend | `data/tables/campaign-v3/campaign-v3-quality.md` |
| Speedup, efficiency (Figure 1) | `campaign-v3-scaling.csv`, `figures/campaign-speedup.pdf` |
| Primary contrasts and their 99.5 % intervals (Table 1, RQ1) | `campaign-v3-contrasts.csv`, `campaign-v3-sensitivity.csv` (columns `primary_*`) |
| Time over native (ABS rows), RQ2 by thread count (Figure 2) | `campaign-v3-contrasts.csv`, `figures/campaign-rq2-ends.pdf` |
| The two factors of the RQ2 ratio | `campaign-v3-rq2-decomposition.csv` |
| Mann-Whitney, Cliff's delta, re-pairings | `campaign-v3-robustness.csv` |
| Spread of the runs | `campaign-v3-distributions.csv` |
| Sequential references | `campaign-v3-sequential.csv` |
| Fork-join calibration | `campaign-v3-fork-join.csv` |
| Karp-Flatt | `campaign-v3-karp-flatt.csv` |
| Engine arms (Table 2, engine rows) | `data/tables/tier-v3/tier-v3-arms.csv`, ADR 0089 |
| Native probe (Table 2, probe rows) | `data/probes/atomic-increment/README.md` |
| Increment sequences, instructions per pixel of the listings | `data/probes/engine-code/README.md` |
| Retries per add, time against line transfers | `data/tables/perf-v3/perf-v3-retries.csv`, ADR 0091 |
| Counters of the loop alone (Table 3) | `data/tables/perf-loop-v3/`, ADR 0090, ADR 0091 |
| SIMD variants | `data/tables/simd-v3/simd-v3-variants.csv`, ADR 0091 |
| Private and packed atomics | `data/tables/extras-v3/extras-v3-scaling.csv`, ADR 0093 |
| Weak scaling | `data/tables/weak-v3/weak-v3-scaling.csv`, ADR 0092 |
| E-cores | `data/tables/hybrid-v3/hybrid-v3-scaling.csv`, ADR 0094 |
| Small regions | `data/tables/cutoff-v3/cutoff-table.csv`, `cutoff-estimates.csv`, `cutoff-model.csv` |
| Granularity | `data/tables/grain-v3/grain-points.csv`, `grain-best.csv`, ADR 0092 |
| Per-core check, the gate, the two builds | ADR 0085, ADR 0086, ADR 0087 |
| Pilot facts in the methodology (E-cores, headful, start delay, mask escape) | ADR 0045, ADR 0046, ADR 0048 |
| Threats to validity | ADR 0080, as amended by ADR 0085, 0087 and 0091 |

The extended report maps each of its sections to the decision records and tables behind it in
its appendix (Table "Where each section comes from").
