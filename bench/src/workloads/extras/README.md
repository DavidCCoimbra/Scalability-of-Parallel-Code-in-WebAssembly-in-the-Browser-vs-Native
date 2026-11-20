# workloads/extras

Workloads outside RQ1 and RQ2.

| File | Responsibility |
|---|---|
| `sort.rs` | `ParallelSort`: Rayon's stable `par_sort` (allocates its buffer in the timed region, on purpose) and unstable `par_sort_unstable` (in place) of the pixels read as `u32` keys |

```mermaid
flowchart LR
    image["GrayImage"] --> keys["pixels as little-endian u32 keys"]
    keys --> prepare["prepare: restore the unsorted keys"]
    prepare --> run["run: par_sort or par_sort_unstable (timed)"]
    run --> checksum["checksum of the sorted keys"]
```
