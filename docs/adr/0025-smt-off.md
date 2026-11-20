# ADR 0025: SMT off, one CPU per physical P-core, checked on every result

Date: 2026-10-17

## Context

ADR 0001 measures on the 8 physical P-cores (performance cores) of the i9-14900KF without
hyperthreading. Hyperthreading, or SMT (simultaneous multithreading), lets one physical core run
two hardware threads that share its execution units; Linux shows each hardware thread as a
separate CPU.

On this CPU, Linux numbers the two hardware threads of each P-core side by side (0/1, 2/3, ...,
14/15). A mask such as `0-7` therefore looks like 8 CPUs but is 4 physical cores x 2 threads: from
N = 5 on, two measured threads would share a core, and the resulting drop in efficiency would look
like a scalability result of the code. Nothing in the code enforced ADR 0001, so this mistake would
not have been caught.

## Decision

- **SMT off.** SMT is turned off on the PC for every measurement session
  (`echo off > /sys/devices/system/cpu/smt/control`), set by the environment script and checked
  before each session (ADR 0035); decided by the author.
- **Mask.** The measurement mask is one CPU per P-core: `0,2,4,6,8,10,12,14`.
- **Recorded.** Every result records `smt` (the `smt/control` value), `pCpus` (the P-core CPUs from
  `/sys/devices/cpu_core/cpus`) and `maskSiblings` (the `thread_siblings_list` of each masked CPU).
- **Enforced.** Strict validation (ADR 0023) rejects SMT that is not off, a mask with two CPUs on
  the same physical core, and masked CPUs that are not P-cores.

## Consequences

- No sibling hardware thread is left free for other processes to share a measured core.
- The whole machine runs without SMT during sessions. The setting does not survive a reboot, so
  the session check must run every time.
- Supersedes nothing; makes ADR 0001 enforceable.

## Status

Accepted
