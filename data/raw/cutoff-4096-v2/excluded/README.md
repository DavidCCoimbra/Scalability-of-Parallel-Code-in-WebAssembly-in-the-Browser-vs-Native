# Excluded runs

`cutoff-4096-v2-0427-firefox-filter-noise-n2-r1`
- Why: 0.286 s of foreign CPU, over the 0.25 s threshold fixed in ADR 0051 before the data. It was the slowest run of its configuration (5.98 ms against a median of 3.89 ms). It started at 16:53 UTC, 35 s after a `git worktree add` on the same machine.
- Replacement: moved here, and the same planned run (position 427) ran again on 2026-11-10 at 18:58 UTC, from the same build `measured/v2`, in a new session. It ran about 2 h after its place in the randomized order.
