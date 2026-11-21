# ADR 0080: The threats to validity that are declared with the results

Date: 2026-11-21

## Context

The threats to the study's validity were spread over many records, each written when its
problem appeared, and an audit of the final repository found several that no record named.
A reader, and the paper, need them in one list, each with what is known about its size. This
record collects them. It decides nothing about the measurements: every item is a limit of what
the results of `measured/v2` (ADR 0079) can support.

Each item says how it is known: *measured* (a number from the committed data), *recorded* (a
fact of the setup written in a record or in the run context), or *not established* (a likely
cause that no data here isolates).

## Decision

The following are stated wherever the results are reported.

### Internal validity

- **One P-core of the machine is degraded.** Recorded (ADR 0002, ADR 0052): one core fails at
  high frequencies, which is why turbo could not be measured. Measured: five filter runs at
  N = 1, three native and two Chrome, are 1.21 times their configuration's median, and they
  widen the RQ1 interval (ADR 0077). Not established: that those runs ran on that core, since
  no run records the frequency of the core it ran on. Measured later (ADR 0085): with turbo
  off that core is as fast as the others and gives the right checksum, so a core slow by
  itself does not explain those runs.
- **Thread placement is left to the kernel.** Recorded (ADR 0001): a process-level mask, no
  per-thread pinning, because the browser cannot pin. The shared-atomic cells at k = 1 land on
  several time levels from run to run, which is why they are the widest cells.
- **The layers below the crate differ between environments.** Recorded (ADR 0076): WASM-only
  flags, a rebuilt standard library, other locks inside Rayon, idle workers that spin instead
  of yielding, and the engines' own compilers. They are the environment under study, not a
  defect, but "the same code" is claimed for the crate only.
- **Which compiler tier ran is inferred, not checked.** Recorded: no engine flag is set or
  stored. Measured: no measured iteration shows a tier-up step, and Firefox's atomic histogram
  at N = 1 takes 379.7 ms against 379.6 ms natively, which fits optimized code. In Chrome the
  first warm-up iteration of the atomic histogram is faster than every measured one in 30 of
  30 runs (0.948 times, k = 1, N = 1). Not established: that the steady state is V8's fastest
  code for that loop.
- **The fork-join calibration has 20 samples and a coarse clock in Firefox.** Recorded (ADR
  0076): with a 20 us clock, Firefox's warm fork-join reads 0 at N <= 4.
- **The Firefox runs of the extras campaigns are a block, not interleaved.** Recorded and
  measured (ADR 0071): the block is within -4.9 % to +3.3 % of the main campaign, against
  -2.4 % to +4.5 % for the interleaved environments.
- **Browser threads share the measured cores.** Recorded: Firefox reports a hardware
  concurrency of 32 and Chrome of 8, so Firefox sizes its helper threads for the whole
  machine while confined to eight cores. Not established: how much CPU, cache or memory
  bandwidth they take during a timed iteration.
- **The machine's memory configuration was not recorded.** Transparent huge pages, the RAM
  layout, the kernel command line, mitigations, C-states and firmware settings are in no run
  context. They matter for workloads that stream from memory. New campaigns record them
  (`sysinfo.hostState`, ADR 0083); for the stored ones they can only be read after the fact.
- **Native memory growth during the measured phase cannot be ruled out from the data.** The
  run reads the resident set before and after the measured phase but stores only the sizes
  before the warm-up and after the last iteration; growth fails a WASM run, not a native one.
  The filter's 64 MiB of first touches are expected in the warm-up.

### Construct validity

- **RQ2 is a ratio of ratios.** Measured (ADR 0078): the environment gap of the local control
  moves it as much as the atomics do; it is reported with both factors.
- **The two histograms differ in more than their counters.** Recorded (ADR 0078): only the
  local one passes through the grain control.
- **Speedup is relative to a one-thread Rayon pool**, not to the best sequential code; time
  over native at the same N is reported next to it (ADR 0039), and the absolute speedup
  against native's one-thread time is tabulated (ADR 0082).
- **The efficiency dip at N = 6 and 7 is not explained.** Measured: it appears in every
  environment (local histogram at k = 16, N = 6 / 7 / 8: 0.945 / 0.938 / 0.972 natively,
  0.949 / 0.945 / 1.001 in Chrome, 0.960 / 0.958 / 1.014 in Firefox). Not established: whether
  it comes from Rayon splitting work in powers of two, so that six or seven threads share
  eight pieces, or from placement.

### Statistical conclusion validity

- **RQ1 for Chrome is not robust** to the centre of a configuration (ADR 0077), and the two
  non-rejections are bounds of about 5 % and 6 %, not equalities.
- **Firefox's RQ2 values moved between builds** by more than the smallest effects rejected
  (ADR 0078).
- **The intervals are percentile bootstrap intervals over 30 runs**, which run slightly narrow
  at the 99.5 % level; the plan fixed them before the data (ADR 0037).
- **The points of one speedup curve share their T1**, so an error in T1 shifts the whole
  curve.

### External validity

- **One machine, one compiler version, one version of each browser.**
- **Every primary cell lives in memory, not in cache**: 128 MiB for the filter's two images and
  64 MiB for the histograms, against a 36 MB last-level cache. ADR 0058 reads the native
  filter's loss of efficiency at N = 8 as contention for a resource the cores share, such as
  memory bandwidth, without reaching a ceiling; a slower environment asks less of that
  resource, which may be part of Firefox's higher speedup. The in-cache regime appears only in
  the cutoff campaigns, measured with repeated passes.
- **Inputs are uniform random values** with no spatial structure.
- **The cutoff sizes are lower bounds for a single call**, and no size measured reached
  break-even (ADR 0065).

## Consequences

- Each item above has an owner record or a number; none is left as an unstated assumption.
- Four of the "not established" items can be settled without a new build: the tier that runs
  (engine flags), the dip at N = 6 and 7 (fixed grain at those N), the memory configuration
  (read from the unchanged machine) and Firefox's filter code (a profile). They are optional
  experiments, not conditions of the results.

## Status

Accepted
