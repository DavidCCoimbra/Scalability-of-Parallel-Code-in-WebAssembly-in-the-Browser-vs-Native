# histogram

256-bin histogram of the image, the RQ2 workload. The variants differ only in
how threads share the counters, so the ratio of their times isolates the
cost of synchronization.

| File | Responsibility |
|---|---|
| `mod.rs` | `Histogram` (counts, merge, checksum), `BINS` and `CHUNK_BYTES` (read by `harness/tests/test_browser_check.py`) |
| `atomic.rs` | `AtomicHistogram`: one shared table of padded atomic counters |
| `local.rs` | `LocalHistogram`: per-task counters with fold and reduce, the control |
| `extras/` | Variants outside RQ1 and RQ2: `private.rs`, `packed.rs` and the `packed_counter.rs` layout |
| `counter.rs` | `Counter`: the layout of one shared counter (an `AtomicU64` inside) |
| `counter_table.rs` | `CounterTable<C>`: exactly `BINS` counters (no bounds check on a `u8` index), `reset`, `increment`, `read` |
| `padded_counter.rs` | `PaddedCounter` (one counter per cache line) and `CACHE_LINE_BYTES` (128) |

```mermaid
flowchart LR
    pixels["pixels"] --> chunks["par_chunks(CHUNK_BYTES)"]
    chunks --> atomic["one shared CounterTable<br/>atomic (padded), packed"]
    chunks --> private["own CounterTable per thread<br/>private"]
    chunks --> local["fold into a local Histogram<br/>then reduce with merge"]
    atomic --> readback["read back the counters<br/>(timed)"]
    private --> merge["merge the tables<br/>(timed)"]
    local --> histogram["stored Histogram"]
    readback --> histogram
    merge --> histogram
    histogram --> checksum["Histogram::checksum<br/>(untimed)"]
```
