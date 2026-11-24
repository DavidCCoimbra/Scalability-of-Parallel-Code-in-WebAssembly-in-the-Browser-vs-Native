# data

The measured runs of the final build, `measured/v2`, and the tables derived
from them. The paper's numbers come from here.

| Folder | Contents |
|---|---|
| `raw/<campaign>-v2/` | One CSV (the run's rows) and one JSON (the run's context) per run, plus `campaign.json` (the spec and build it ran with) and `campaign.jsonl` (the journal, one line per run in execution order) |
| `raw/<campaign>-v2/excluded/` | Runs kept but left out of the analysis, each with its reason in the folder's README |
| `raw/<campaign>-v2/discarded/` | The discarded first browser launch of each session |
| `raw/campaign-v3/`, `tables/campaign-v3/` | The main campaign of the build `measured/v3` (ADR 0084) and its tables, written by `make results MEASURED=v3`; the raw folder has the same `discarded/` launches and `sysinfo/` as the v2 ones |
| `raw/*-v3/`, `tables/*-v3/` | The other campaigns of `measured/v3` that ADR 0088 uses: `tier`, `perf`, `perf-loop1` and `perf-loop8`, `simd-scalar`, `simd-avx2`, the seven `cutoff` and `grain-threads`. Tables by `make v3-results simd-results cutoff-results perf-results MEASURED=v3`; what they show is in ADR 0089 and ADR 0091. Also the two grain sweeps (`grain-1024`, `grain-8192`) and `weak`, by `make grain-results weak-results MEASURED=v3` (ADR 0092), `extras`, by `make extras-workloads-results MEASURED=v3` (ADR 0093), and `hybrid`, by `make hybrid-results MEASURED=v3` (ADR 0094) |
| `probes/atomic-increment/` | The shared histogram counted natively with the increment sequences of LLVM and of V8's two compilers (ADR 0089); a probe, not results |
| `probes/engine-code/` | The machine code of each kernel: native, WASM, and V8's two compilers (ADR 0088); a probe, not results |
| `checks/gate-v3/`, `checks/gate2-v3/` | The two gates before the v3 campaigns (ADR 0087); not results |
| `sessions/v3/` | The progress log of each stage of the v3 measuring session, and the digests of the two builds |
| `checks/core-check/` | The per-core check of the measuring PC before the v3 build (ADR 0085); not results |
| `tables/<campaign>-v2/` | What `make results` (and the other result targets) writes from `raw/`: quality report, scaling table, contrasts, robustness, shape, and the sidecar JSON of each |

The campaigns are described in `harness/campaigns/README.md`. The extras
(`extras-v2`, `weak-v2`, `simd-*-v2`, `hybrid-v2`, `perf-v2`) are not part of
RQ1 or RQ2. The pilot data and the data of earlier builds stay in the working
repository.

Every table can be regenerated from `raw/` with `make all-results`; the
sidecar JSON files keep a fixed key order, so a regeneration changes only
their `commit` and `createdAt`. `make tables-check` does it and fails if any
other line of any table differs; CI runs it when the analysis, the harness,
the make targets or the data change.

```mermaid
flowchart LR
    spec["harness/campaigns/*-v2.json"] --> raw["raw/&lt;campaign&gt;-v2<br/>CSV + context per run"]
    raw --> check["datacheck"]
    check --> tables["tables/&lt;campaign&gt;-v2"]
    tables --> paper["paper"]
```
