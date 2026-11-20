# Scalability of Parallel Code in WebAssembly in the Browser vs. Native

An empirical study of how the scalability (relative speedup and efficiency) of the same parallel
Rust/Rayon code differs between native execution and WebAssembly with threads in Chrome and
Firefox, and how much thread synchronization contributes to that difference.

- **RQ1:** How does the scalability of the same parallel code, run as WebAssembly in the browser
  and natively, evolve as the number of threads grows?
- **RQ2:** To what extent does synchronization between threads affect the gap observed in RQ1?

The workloads are a 3x3 Gaussian filter (embarrassingly parallel, the baseline) and an image
histogram, with shared padded atomic counters against per-task local counters, over inputs with
k in {1, 4, 16, 256} distinct values. The same source, compiler and flags build the native
runner and the WASM package. Every design decision, with its reasons, is a record in
[`docs/adr/`](docs/adr/README.md).

## Provenance

Every number of the paper comes from one build, tagged `measured/v2` (commit `c8ea7157a` of the
working repository, where the study was developed). This repository holds that build's code and
its measured data, `data/raw/*-v2` and `data/tables/*-v2` (see [`data/README.md`](data/README.md)).
The pilot data, the data of earlier builds and the one-off probes stay in the working repository.

The code comments were revised for this repository, and the extra workloads moved into
`extras/` modules; nothing else in the measured path changed. `scripts/codegen_diff.sh
measured/v2` (with the tag fetched from the working repository) finds every hot function
identical in the WASM builds, and in the native builds once the `extras::` module path is
ignored in call targets.

## Setup

Develop and test on any machine; measure only on the Linux PC (an i9-14900KF, ADR 0001).

```sh
make setup   # rustup, the pinned nightly, wasm-bindgen and the pinned browsers (no sudo)
make build   # the native runner and the WASM package
make test    # what CI runs, minus LaTeX
```

On the measuring PC, once, with sudo:

```sh
make deps sudoers chrome-apparmor
```

`sudoers` allows passwordless `systemd-run` and `systemctl` for the run scopes (ADR 0028): keep it
to the dedicated PC and remove it (`sudo rm /etc/sudoers.d/ppc-bench`) after the campaigns.

## How to run

| Command | What it does |
|---|---|
| `make env-setup` / `make env-restore` | Prepare the PC for measuring (SMT and turbo off, governor `performance`, P-cores shielded) and undo it |
| `make campaign SPEC=harness/campaigns/<name>.json` | Run a campaign: every run a fresh process, in a seeded random order, resumed if stopped |
| `make status SPEC=...` | Progress of a campaign, read-only |
| `make results` | Every table and figure of the main campaign, from `data/raw/campaign-v2` |
| `make all-results` | The same for every campaign, the exploratory ones and the hardware counters included |
| `make quick` | Tiny copies of every campaign, to check the pipeline end to end (never results) |

`make help` lists the rest. The campaigns are described in
[`harness/campaigns/README.md`](harness/campaigns/README.md).

### Checking SIMD by hand

CI checks that the filter's interior loop is vectorized on both sides (ADR 0017):

```sh
cd bench
objdump -d -C --no-show-raw-insn target/release/native > native.dis
python3 ../scripts/check_simd.py native.dis x86_64
wasm-objdump -d target/wasm32-unknown-unknown/release/bench.wasm > bench.wasm.dis
python3 ../scripts/check_simd.py bench.wasm.dis wasm32
```

## Repository layout

| Folder | Contents |
|---|---|
| `bench/` | Rust crate: workloads, native runner, WASM entry and benchmark page |
| `harness/` | Results server, browser launcher (no automation framework), environment control, campaign orchestrator and specs |
| `analysis/` | Statistics, inference, quality checks, tables and figures |
| `data/` | `raw/` (one folder per campaign, the measured runs) and `tables/` (derived from them) |
| `docs/adr/` | The decision records, with those of the exploratory campaigns in `extras/` |
| `scripts/` | Repository checks: ADR structure, SIMD, codegen diff, hardware counters |
| `paper/` | LaTeX: `final/` (the paper), `pilot/`, `proposal/`, with shared `figures/` and `bib/` |

```mermaid
flowchart LR
    bench["bench: workloads, native runner, WASM"] --> harness["harness: campaigns"]
    harness --> raw[("data/raw/*-v2")]
    raw --> analysis["analysis: tables and figures"]
    analysis --> tables[("data/tables/*-v2")]
    tables --> paper["paper"]
    adr["docs/adr: decisions"] -.-> bench
    adr -.-> harness
    adr -.-> analysis
```

Two options stay in the code without a measured campaign: the image `pitch` (row padding) and
the `consecutive` palette.

## Use of AI

See [`AI_USE.md`](AI_USE.md).
