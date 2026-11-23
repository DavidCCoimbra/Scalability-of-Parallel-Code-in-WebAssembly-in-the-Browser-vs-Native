# engine-code

The machine code that runs each kernel of the study: what LLVM compiled natively, the WASM that
both browsers receive, what V8 compiled from that WASM with each of its two compilers, and what
SpiderMonkey's optimizing compiler did. A
probe, not a measurement: it is evidence for the explanations of ADR 0088.

Everything comes from the binaries of `measured/v3` (`data/sessions/v3/build/digests.txt`).

| Kernel | Function it is in | What the time is spent on |
|---|---|---|
| `blur-interior` | `blur_interior` | The filter: every pixel of a row but the two at its ends |
| `atomic-loop` | the task function of `AtomicHistogram::run` | The shared atomic counters (RQ2 numerator) |
| `local-loop` | the task function of `local_counts` | The per-task plain counters (RQ2 denominator) |
| `sequential-histogram` | `SequentialHistogram::run` | The reference without Rayon |
| `sequential-filter` | `SequentialBlur::run` | The reference without Rayon; it calls `blur_interior` |

Per kernel folder:

| File | Contents | How it was obtained |
|---|---|---|
| `native.s` | The whole function, x86-64 | `objdump -d -C` of `bench/target/release/native` |
| `wasm.wat` | The whole function, WASM | `wasm-objdump -d` of `bench/www/pkg/bench_bg.wasm` |
| `chrome-optimizing.s` | The function as V8's optimizing compiler (TurboFan) left it | A Chrome run with `--js-flags=--perf-prof`, the function whose name ends in `-turbofan` |
| `chrome-baseline.s` | The function as V8's baseline compiler (Liftoff) compiled it | The same with `--liftoff-only`, the name ending in `-liftoff` |
| `firefox-loop.s` | The loop SpiderMonkey's optimizing compiler runs, with the perf samples of each instruction (three kernels; the sequential ones were not captured) | A long Firefox run sampled with `perf record`; the bytes of the sampled pages read from the process memory. See "Firefox" below |
| `*-loop.s`, `wasm-loop.wat` | One loop of that function, cut out to be read | See below |

`summary.csv` counts the instructions of the native and WASM functions and loops.

## How to read the loop files

The loop is chosen by rule, not by hand: among the loops that read a pixel and hold the kernel's
marker instruction, the innermost with the most markers. For the atomic histogram and for the
native and WASM listings that is the unrolled main loop. For V8's plain histograms the marker is
loose (any load, add and store), so `local-loop/chrome-*-loop.s` and
`sequential-histogram/chrome-*-loop.s` are a coarse cut; the whole function is next to them.

WASM is a stack machine: an operation first pushes its operands, so a WASM loop has several
times the instructions of the x86 loop it becomes. The WASM counts are comparable with each
other, not with the x86 ones.

## What the listings show

| Kernel | Native (LLVM) | Chrome, optimizing | Chrome, baseline | Firefox, optimizing |
|---|---|---|---|---|
| Atomic increment | `lock incq (mem)`, 8 per turn | `mov (mem),%rax; add; lock cmpxchg; jne` back to the load: a compare-and-swap retried until it succeeds, 8 per turn | `lock xadd %rcx,(mem)`, 8 per turn, each behind an alignment and a bounds check | `lock add %r9,(mem)`, 8 per turn, each behind an alignment check |
| Plain increment | `incq (mem)`, 4 per turn | `mov (mem),%r; add $1,%r; mov %r,(mem)` | load, add and store through the frame | `mov (mem),%r; add $1,%r; mov %r,(mem)` |
| Filter | SSE2 with legacy encoding (`paddw`, `punpcklbw`, `movdqu`), 65 instructions | The same 128-bit operations in VEX encoding (`vpaddw`, `vpmovzxbw`, an SSE4.1 operation), 87 instructions | VEX encoding too, 122 instructions | A mix: `vmovups` and `vpmovzxbw` in VEX encoding with `paddw`, `psllw` and `palignr` (SSSE3) in legacy encoding, 85 instructions |

- The native sequential histogram and the native task of the local histogram have the same
  loop: `movzbl; incq`, four times per turn.
- LLVM unrolls alike for both targets: 8 atomic increments per turn and 4 plain ones, in x86 and
  in WASM. What differs between native and browser is made by the engine from that WASM.
- In a default Chrome run both compilers' versions of a function are in the dump: the baseline
  one runs first and the optimizing one replaces it.
- The filter loops handle 16 pixels per turn, so the listings give 4.06 instructions per pixel
  natively, 5.44 in Chrome and 5.31 in Firefox. The counters of the loop alone, measured apart
  (ADR 0091), give 4.10, 5.52 and 5.41.
- Firefox's atomic increment is the native one with an alignment check in front, which fits its
  atomic histogram running at the native speed.

## Limits

- **Firefox's listings are obtained another way and say less.** Its release build writes no
  dump of its code (ADR 0060). `scripts.capture_firefox` samples a long run with `perf`, takes
  the pages of the mapping SpiderMonkey names `js-executable-memory` that hold the samples, and
  reads them from `/proc/<pid>/mem` through a root unit. The bytes have no function names and
  no known start: `scripts.firefox_code` starts the disassembly at the offset that puts the
  samples on instruction starts (all but a few of 20 000 do) and cuts the shortest loop with
  the kernel's marker that holds a tenth of the samples. Only the optimizing compiler's code
  was captured, at one thread, for three kernels.
- **How those listings were checked.** The pages are read twice, with five more seconds of
  sampling in between, and the capture stops unless the two reads are the same bytes
  (`firefox-capture.txt` in each folder, with the process and the pages). The loop cut out holds
  all the samples of the atomic and the local histogram and a quarter of the filter run's, the
  rest being the checksum; its first line says how many. The choice of the loop was checked
  against a measurement made apart: the instructions per pixel of each listing are those of the
  counters of the loop alone (5.31 against 5.41 for the filter).
- In the filter run the most sampled loop of Firefox is not the filter but the checksum of its
  output, which runs after every iteration outside the timed region; the listing is the filter's
  loop, found by its vector instructions.
- The Chrome runs are diagnostic: `--no-sandbox` and `--perf-prof`, which no campaign uses,
  images of 4096x4096 and two threads. That the code is the one a campaign runs is assumed, not
  shown. A function is compiled more than once in a run; the listing is the last version, and
  `scripts.chrome_code` prints how many it found.
- A listing says which instructions run, not how long each takes. The times are the campaigns'.

## Reproducing it

```sh
python3 -m scripts.kernel_code --native bench/target/release/native --wasm bench/www/pkg/bench_bg.wasm --output data/probes/engine-code
python3 -m scripts.capture_chrome /tmp/chrome-dumps     # on the prepared PC, no campaign running
python3 -m scripts.chrome_code /tmp/chrome-dumps data/probes/engine-code
python3 -m scripts.capture_firefox /tmp/firefox-capture  # needs perf and the passwordless systemd-run of the harness
python3 -m scripts.firefox_code /tmp/firefox-capture data/probes/engine-code
```
