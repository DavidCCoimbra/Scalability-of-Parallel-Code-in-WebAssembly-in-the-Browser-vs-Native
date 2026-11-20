# ADR 0003: Strong scaling with speedup T1/TN per environment

Date: 2026-10-17

## Context

RQ1 asks how speedup and efficiency evolve with the number of threads N. Two standard designs
answer different questions:

- strong scaling keeps the problem size fixed and adds threads: how much faster does the same
  job get? Its limit is described by Amdahl's law (the sequential part bounds the speedup);
- weak scaling grows the problem with the number of threads, so each thread has the same amount
  of work: can more threads handle a proportionally larger job in the same time? It is described
  by Gustafson-Barsis's law.

The question here is the first one: how well the same code uses more threads natively and in
the browser.

## Decision

- Strong scaling: the same input for every N.
- Speedup = T1/TN, computed within each environment (native, Chrome, Firefox): each environment
  is compared with its own single-thread time, not with native. Efficiency is speedup / N.
- Results are analysed with Amdahl's law in mind.

## Consequences

- One input size must suit every N at once: not too slow at N = 1, well above timer noise at
  N = 8, and with enough tasks per thread. The size is chosen in the pilot (ADR 0041).
- Because each environment is normalised by its own T1, a slower single-thread time in the
  browser can make its speedup look better; absolute time ratios are reported as well
  (ADR 0039).
- Weak scaling stays an optional extra (later run, ADR 0055).

## Status

Accepted
