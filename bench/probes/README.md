# probes

One-off microbenchmarks outside the study's workloads. Extra: not part of RQ1 or RQ2, and not
built by any target.

| File | What it is |
|---|---|
| `rmw_chain.c` | The increment sequences that LLVM and V8 emit for the k = 1 local histogram (one memory-operand `inc` against load, add, store), timed on one core. It is the probe behind ADR 0060; its recorded outputs stay in the working repository |

```mermaid
flowchart LR
    source["rmw_chain.c"] --> build["cc -O2 (by hand)"]
    build --> run["taskset to one core"]
    run --> times["ms per sequence"]
    times --> adr["ADR 0060"]
```
