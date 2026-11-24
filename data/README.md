# data

The measured runs of the final build, `measured/v3`, and the tables derived
from them. The paper's numbers come from here. The runs, tables and specs of
the earlier build `measured/v2` are at the tag `data/v2`.

| Folder | Contents |
|---|---|
| `raw/<campaign>-v3/` | One CSV (the run's rows) and one JSON (the run's context) per run, plus `campaign.json` (the spec and build it ran with) and `campaign.jsonl` (the journal, one line per run in execution order) |
| `raw/<campaign>-v3/discarded/` | The discarded first browser launch of each session |
| `raw/<campaign>-v3/sysinfo/` | The state of the machine when the campaign started |
| `tables/<campaign>-v3/` | What the result targets write from `raw/`: quality report, scaling table, contrasts, robustness, shape, and the sidecar JSON of each |
| `probes/atomic-increment/` | The shared histogram counted natively with the increment sequences of LLVM and of V8's two compilers (ADR 0089); a probe, not results |
| `probes/engine-code/` | The machine code of each kernel: native, WASM, V8's two compilers and SpiderMonkey's (ADR 0088); a probe, not results |
| `checks/core-check/` | The per-core check of the measuring PC before the v3 build (ADR 0085); not results |
| `checks/gate-v3/`, `checks/gate2-v3/` | The two gates before the v3 campaigns (ADR 0087); not results |
| `sessions/v3/` | The progress log of each stage of the v3 measuring session, and the digests of the two builds |

No v3 campaign has a run left out of the analysis, so no `excluded/` folder
exists.

| Campaigns | Tables by | What they show |
|---|---|---|
| `campaign` (RQ1 and RQ2) | `make results` | ADR 0095, and `tables/campaign-v3` |
| `campaign` (sequential references, per core), `tier`, `grain-threads`, `perf-loop1`, `perf-loop8` | `make v3-results` | ADR 0089, ADR 0091 |
| `perf` | `make perf-results` | ADR 0089, ADR 0091 |
| `simd-scalar`, `simd-avx2` | `make simd-results` | ADR 0091 |
| `cutoff-*` (seven) | `make cutoff-results` | ADR 0091 |
| `grain-1024`, `grain-8192` | `make grain-results` | ADR 0092 |
| `weak` | `make weak-results` | ADR 0092 |
| `extras` | `make extras-workloads-results` | ADR 0093 |
| `hybrid` | `make hybrid-results` | ADR 0094 |

Only the main campaign answers RQ1 and RQ2; every other campaign is
exploratory. The campaigns are described in `harness/campaigns/README.md`.
The pilot data and the data of builds before v2 are not part of this
repository.

Every table can be regenerated from `raw/` with `make all-results`; the
sidecar JSON files keep a fixed key order, so a regeneration changes only
their `commit` and `createdAt`. `make tables-check` does it and fails if any
other line of any table differs; CI runs it when the analysis, the harness,
the make targets or the data change.

```mermaid
flowchart LR
    spec["harness/campaigns/*-v3.json"] --> raw["raw/&lt;campaign&gt;-v3<br/>CSV + context per run"]
    raw --> check["datacheck"]
    check --> tables["tables/&lt;campaign&gt;-v3"]
    tables --> paper["paper"]
```
