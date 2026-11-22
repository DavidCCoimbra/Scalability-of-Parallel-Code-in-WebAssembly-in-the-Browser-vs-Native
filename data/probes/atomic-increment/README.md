# atomic-increment

A native microbenchmark of the shared atomic histogram in which only the instructions of one
increment change (`bench/probes/atomic_increment.c`). A probe, not a measurement of the study:
it tests the explanation of questions 6 and 7 of ADR 0088.

**Question.** Chrome's atomic histogram is slower than the native one at k = 1 and faster at
k = 256 with eight threads. Is that the instructions V8 emits for one increment?

**Prediction, written before the run (ADR 0088).** With V8's compare-and-swap sequence the
native program is slower at k = 1 and faster at k = 256 with eight threads.

**What it does.** The table of the bench (256 counters, 128 bytes apart) and its input (the
same generator and seed, 8192x8192, k = 1, 16 and 256), counted by 1 or 8 threads, each pinned
to one P-core and given one contiguous slice of the image. Five sequences, eight increments per
turn as LLVM unrolls the bench's loop:

| Sequence | Instructions of one increment | Whose it is |
|---|---|---|
| `lock-inc` | `lock inc [m]` | LLVM, native |
| `compare-and-swap` | `mov rax,[m]; lea rdx,[rax+1]; lock cmpxchg [m],rdx; jne` back to the load | V8's optimizing compiler |
| `lock-xadd` | `mov edx,1; lock xadd [m],rdx` | V8's baseline compiler, without its checks |
| `lock-inc-checked` | an alignment check and a bounds check, then `lock inc` | the native increment with the baseline compiler's checks |
| `lock-xadd-checked` | the same checks, then `lock xadd` | V8's baseline compiler |

Every cell runs once per round, 2 warm-up rounds and 10 timed ones (`passes.csv`, 300 rows);
every pass counted every pixel.

**Result.** Median time of a pass in ms, on the prepared PC, 2026-11-22:

| Sequence | k = 1, N = 1 | k = 1, N = 8 | k = 16, N = 1 | k = 16, N = 8 | k = 256, N = 1 | k = 256, N = 8 |
|---|---|---|---|---|---|---|
| `lock-inc` | 379.9 | 976.2 | 379.8 | 550.1 | 379.8 | 415.0 |
| `compare-and-swap` | 677.1 | 2131.8 | 484.9 | 1018.9 | 408.2 | 239.5 |
| `lock-xadd` | 382.6 | 975.3 | 380.7 | 547.1 | 380.3 | 437.2 |
| `lock-inc-checked` | 381.6 | 972.9 | 380.3 | 556.1 | 380.0 | 401.6 |
| `lock-xadd-checked` | 392.4 | 983.9 | 383.5 | 556.4 | 380.2 | 348.8 |

The slowest pass of a cell is at most 0.8 % above its fastest.

- **The prediction holds.** The compare-and-swap is 1.78 times the locked increment at k = 1
  with one thread and 2.18 times with eight, and 0.58 times at k = 256 with eight.
- **It gives Chrome's times.** In the main campaign Chrome's atomic histogram takes 698, 488
  and 412 ms with one thread at k = 1, 16 and 256; the compare-and-swap gives 677, 485 and
  408 ms. With eight threads at k = 256 Chrome takes 210 ms and the compare-and-swap 240 ms.
- **The locked increment gives the native times**: 380 ms with one thread at every k and
  415 ms at k = 256 with eight threads, against 380 and 415 ms in the campaign.
- **The baseline compiler's sequence gains at k = 256 too, less**: 349 ms against 415 ms. The
  checks alone (402 ms) or the exchange-and-add alone (437 ms) do not; it takes both.

**Limits.** Each thread has a fixed slice and a fixed core, where the bench splits the image
into Rayon tasks and leaves placement to the kernel, so the eight-thread times at k = 1 and 16
are not the bench's (976 against 856 ms at k = 1). One session, ten passes per cell. The probe
shows that the sequence is enough to produce the effect on this CPU; why a load before the
locked write contends less over 256 lines is not shown.

## Reproducing it

```sh
cc -O2 -pthread -masm=intel -o atomic_increment bench/probes/atomic_increment.c
./atomic_increment > passes.csv    # on the prepared PC, in a scope that may use the P-cores
```
