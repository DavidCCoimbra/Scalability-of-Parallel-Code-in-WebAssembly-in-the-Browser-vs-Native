# ADR 0060: Why Chrome beats native on the local histogram at k = 1

Date: 2026-11-08

## Context

In the main campaign the local histogram at k = 1 is the only configuration where a browser is
faster than native among the workloads with no shared counters (the filter and the local
histogram; with shared atomics the browsers are faster in several configurations, as the absolute ratios
of ADR 0039 show):
Chrome takes 151.5 ms at N = 1 against 154.9 ms natively (0.978), and 0.979
at N = 8; Firefox takes 155.6 ms (1.004). The same source, compiler and release profile (ADR 0076) produce both
binaries, so the difference has to come from the machine code that each side ends up running:
LLVM's code natively, and the code V8's compiler generates from the WASM in Chrome.

The cause was investigated on 2026-11-08, down to the assembly. Hardware counters were not
available (`perf_event_paranoid` was 4 and changing it was not in scope at the time), so the
investigation reads the generated code and times it in isolation.

## Decision

Record the cause and how it was found.

### The loop

At k = 1 every pixel increments the same counter of a per-task `[u64; 256]` table. Each
iteration therefore loads, adds to and stores the value the previous iteration stored: the loop
is a dependency chain through memory, bound by store-to-load forwarding latency (the time for a
stored value to reach the next load of the same address), not by throughput. The native time is
2.31 ns per pixel, 7.4 cycles at 3.2 GHz.

### The two machine codes

- **Native** (`data/earlier/probes/native-hist-local-k1-loop.asm`, where every `data/probes/` file
  named below is; `objdump` of the baseline build):
  LLVM unrolls the loop by four and uses one read-modify-write instruction per pixel,
  `inc QWORD PTR [rsp+rcx*8+0x48]`.
- **Chrome** (`data/probes/v8-hist-local-k1-loop.asm`): Chrome was started with
  `--no-sandbox --js-flags="--perf-prof --perf-prof-annotate-wasm"`, which writes the bytes of
  every compiled function to `jit-<pid>.dump`; `python3 -m analysis.extras.jitdump` extracts the
  TurboFan code (V8's optimizing compiler) of the Rayon fold helper (function 32). TurboFan
  keeps LLVM's four-way unroll but splits each increment into a load, an add and a store,
  `mov rdx,[r15+rbx]; add rdx,1; mov [r15+rbx],rdx`, addressed as memory base plus a 32-bit
  offset. It also adds an interrupt check (`cmp BYTE PTR [r13-0x4f],0`) every four pixels.

The two `.asm` files and the microbenchmark results below are in `data/earlier/probes`.

### The microbenchmark

`bench/probes/rmw_chain.c` (results in `data/probes/rmw-chain.txt`) runs each instruction
sequence by hand on 8192^2 pixels, pinned to one P-core through the benchmark slice, on three
P-cores:

| Sequence | Time | Campaign reference |
|---|---|---|
| native `inc [b+i*8]` | 155.1 to 155.2 ms | native 154.9 ms |
| Chrome's exact sequence, with the check | 152.7 to 153.6 ms | Chrome 151.5 ms (0.8 to 1.4 % off) |
| Chrome's sequence without the check | 150.7 to 150.9 ms | - |
| `add [b+i*8],1` | 152.7 ms | - |
| load / add / store on `[b+i*8]` | 151.6 to 152.2 ms | - |

- The interrupt check costs about 1.3 %.
- The memory-destination `inc` makes the chain 1.5 to 2 % slower than the other forms.
- The probe's native / V8 gap is 2.4 ms (1.6 %), against 3.4 ms (2.2 %) in the campaign. So
  instruction selection explains between about 45 % and 75 % of Chrome's advantage (the probe's
  gap of 1.5 to 2.5 ms against 3.4 ms in the campaign), but not all of it.

Limits of the probe:

- The variants are not fully isolated: V8's sequence without the check (32-bit `lea`, base plus
  offset) is 1 ms faster than load / add / store on `[b+i*8]`, which is not explained.
- The probe runs its variants in a fixed order in one process, with no run-level repetitions.
- Why `inc` is slower on Raptor Cove (the P-core microarchitecture), for example its uop count
  or flag handling, is not measured.

### A larger effect neither compiler uses

With the counter's address in one register (`[reg]` instead of base plus index), the same chain
runs 6.4 times faster (0.36 ns, 1.15 cycles per pixel), for `inc` and for load / add / store
alike. This is consistent with the fast store forwarding of recent Intel cores applying only to
simple addressing; it is not documented by Intel for this core and was not measured further.

### Other k and Firefox

- **Other k.** At k = 256 consecutive pixels mostly hit different counters, so the chain is
  broken and throughput decides. There the probe puts Chrome's sequence 7 % above native, while
  the campaign has Chrome 23 % above native at k = 256 (the probe's input is a hash pattern, not
  the campaign's). The probe explains k = 1, not the browser cost at other k.
- **Firefox** was not inspected: its release build wrote no jitdump with `IONPERF`. It runs at
  native speed (1.004).

## Consequences

- The paper can state that Chrome's 2 % advantage at k = 1 is not a scaling effect (it is
  present at N = 1 and unchanged at N = 8) and that instruction selection explains part of it,
  between about 45 % and 75 %; the rest, about 25 % to 55 %, is unexplained.
- It is a reminder for RQ1 that "same source, same compiler" does not mean the same instructions:
  the WASM engine's code generator is part of the environment being measured.

## Status

Accepted
