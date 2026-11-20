# ADR 0032: ADRs brought in line with the code

Date: 2026-10-17

## Context

The ADRs are the record that justifies the measurements, so an ADR that describes something the
code does not do is a false claim about the method. The review of the code, done once it was
complete and before the pilots, found three such places:

- ADR 0015 and ADR 0016 say the native runner builds an explicit Rayon thread pool and measures
  inside `ThreadPool::install`. Since ADR 0018 it uses the global pool (`build_global`)
  without `install`.
- ADR 0011 says the input fingerprint (an FNV-1a hash of the input pixels) is recorded, and
  that golden fingerprints are checked on wasm32 in the browser CI job. Neither existed.
- ADR 0019 says the campaign orchestrator runs the results server outside the measured CPU
  mask. No code did that.

## Decision

Each mismatch is resolved, either by marking the ADR as amended or by making the code do what
the ADR intended:

- **Thread pool.** ADR 0015 and ADR 0016 are marked as amended by ADR 0018: the native runner
  uses the global pool, as the WASM entry does, so both sides set up their threads the same way.
- **Input fingerprint.** The input fingerprint is recorded in every CSV row (ADR 0027), and the
  browser CI job (ADR 0024) now compares it as well. A run's identity is its input fingerprint
  plus its checksum, and every Chrome and Firefox case must match native on both. The golden
  values are the native run's, not a list kept in the repository. ADR 0011 is marked as
  amended by ADR 0027 and this ADR.
- **Server placement.** The placement of ADR 0019 is implemented by ADR 0028 (`taskset` on the
  E-cores, the slower efficiency cores of the hybrid CPU, plus the cpuset shield that keeps the
  rest of the system off the measured P-cores). The campaign orchestrator (ADR 0034) starts
  the server that way. ADR 0019 is marked as amended by ADR 0028.

## Consequences

- An ADR that says more than the code is a review finding; the review of each pull request
  checks the ADRs it touches against the diff.
- A pixel difference between the native and the WASM input now fails CI as an input mismatch,
  separately from an output (checksum) mismatch, so a wrong input generator and a wrong kernel
  are told apart.

## Status

Accepted; amends ADR 0011, ADR 0015, ADR 0016, ADR 0019 and ADR 0024
