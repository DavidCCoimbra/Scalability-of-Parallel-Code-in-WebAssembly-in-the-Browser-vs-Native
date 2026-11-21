# ADR 0086: The v3 build: what changed in the measured code and what the compiler made of it

Date: 2026-11-21

## Context

ADR 0084 lists the changes that make the build `measured/v3`. None is codegen-neutral, so each
is recorded here with the output of `scripts/codegen_diff.sh measured/v2`, run on the measuring
PC (x86-64), and with what was compared by hand where the script can only say that a function
was renamed. This record grows with each change until the build is tagged.

Before any change, the code of this repository gave the machine code of `measured/v2`: native
88 of 88 hot functions identical in the three variants, WASM 87 of 87 in the two variants, the
only function that differs being `__wasm_init_memory`, which writes the data segment and is not
timed.

## Decision

### 1. Every shared-counter histogram builds its tasks with the grain

`AtomicHistogram::run` builds its tasks as the local histogram does:

```rust
let chunk_len = self.grain.chunk_len(CHUNK_BYTES, BYTES_PER_KB);
self.grain
    .tasks(self.image.pixels().par_chunks(chunk_len))
    .for_each(|chunk| chunk.iter().for_each(|&value| counters.increment(value)));
```

With the adaptive grain `chunk_len` is `CHUNK_BYTES` as before and `tasks` calls
`with_max_len(usize::MAX)`, Rayon's default. `hist-atomic` now accepts a fixed grain in KB.
The packed and private extras, which the extras campaign compares with it, go through
`Grain::Adaptive.tasks` as well and still refuse a fixed grain.

- **Same split with the adaptive grain.** A test counts the tasks of an iterator with and
  without `Grain::Adaptive.tasks` on a pool of one thread, where no steal changes how often
  Rayon splits: the counts are equal.
- **What the script reports.** 63 hot functions identical in every variant. The `run` of the
  three histograms differs (the atomic one goes from 245 to 323 bytes natively: it now reads
  the grain), and `native::run` differs because `run` is inlined into it. The Rayon functions
  instantiated for the three are reported as only in base and only in head: their type changed
  from `ChunksProducer` to `MaxLenProducer<ChunksProducer>`, so their names changed. The filter,
  its `blur_interior`, the local histogram and the checksum functions are identical.
- **The counting loops, compared by hand.** In each renamed task function
  (`bridge_producer_consumer::helper`), the instructions from just before the first atomic add
  to just after the last were taken from the base and the head binaries, with jump targets
  (natively) and local and branch indices (WASM) replaced by placeholders, and compared:

  | Histogram | Native: function, loop | WASM: function, loop |
  |---|---|---|
  | atomic | 195 to 194 instructions, loop of 37 identical | 363 to 372, loop of 127 identical |
  | packed | 186 to 185, loop of 29 identical | 363 to 372, loop of 127 identical |
  | private | 215 to 214, loop of 37 identical | 408 to 417, loop of 131 identical |

  Natively the atomic loop is `movzbl; shl $7; lock incq` eight times per iteration with the
  same registers, and the same remainder loop. What changed around the loops is the split
  logic, which now also carries the maximum length.

So the code that counts is unchanged and the code that splits is not; every histogram now goes
through the same split code, which is what the change is for.

### 2. Sequential references: `filter-seq` and `hist-seq`

Two workloads with no Rayon call in `run`, accepted at one thread only:

- `SequentialHistogram` counts into one plain table in one loop, as one task of the local
  histogram counts its chunk.
- `SequentialBlur` blurs every row in one loop with the shared `blur_interior`.

**Adding a workload can change another one.** The first draft of `SequentialBlur` called the
parallel filter's `blur_row`. That function has one caller in v2 and is inlined into the
filter's task. With a second caller the compiler kept it as a call, and the machine code of the
parallel filter changed, though its source did not. Forcing the inlining (`#[inline(always)]`
on it, and then on the edge helpers `blur_clamped` and `clamped_neighbours`) gave yet other
code, in WASM first and then natively too. So `SequentialBlur` has its own copy of the row and
edge handling and shares only `blur_interior`, which is never inlined and does the work of all
but two pixels of each row. A test keeps the copy's output equal to the parallel filter's.

- **What the script reports with both changes.** The parallel filter's task function,
  `blur_interior`, the local histogram and the checksum functions are identical to
  `measured/v2` in the three native and the four WASM variants. Besides the functions of
  section 1, only `native::run` differs (it now dispatches two more workloads), and the empty
  `prepare` of the local histogram is no longer a function of its own: it is merged with the
  new, equally empty ones.
- **A first look, not a result.** Three native runs of each at 8192x8192, in one session: the
  sequential filter took 22.4 ms against 22.5 to 22.6 ms for the pool of one thread, and the
  sequential histogram matched the local one within 0.2 % at k = 1 and k = 256, with the same
  checksums.

In a campaign a sequential workload enters the plan once per repetition, at one thread,
whatever the campaign's thread counts. The analysis keeps its runs apart from the scaling
curves.

## Consequences

- The runs of `measured/v3` are not compared number by number with those of `measured/v2`
  (ADR 0062).
- The golden checksums are unchanged, and the atomic histogram gives the sequential histogram
  for every fixed grain and thread count tested.
- The grain sweep can now include the atomic histogram, which no campaign of v2 could.

## Status

Proposed; completed and accepted when `measured/v3` is tagged
