# tools

| File | What it does |
|---|---|
| `golden_inputs.py` | Reimplements SplitMix64 and the two input generators in Python and prints the FNV-1a fingerprints that `bench/src/input/generators.rs` pins, so that test does not check the Rust code against itself. Run: `python3 bench/tools/golden_inputs.py` |

```mermaid
flowchart LR
    python["golden_inputs.py<br/>independent implementation"] --> prints["fingerprints"]
    prints --> pinned["constants in generators.rs tests"]
    rust["Rust generators"] --> test["images_match_golden_fingerprints"]
    pinned --> test
```
