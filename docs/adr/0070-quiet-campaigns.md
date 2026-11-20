# ADR 0070: Campaigns run in quiet mode, with the coding assistant stopped

Date: 2026-11-10

## Context

Quiet mode (ADR 0042) stops desktop apps and bursty background services before a measuring
session, because they share the last-level cache and memory bandwidth with the measured cores
even when they run on other CPUs. Until now it had to be turned on and off by hand.

On 2026-11-10 a `git worktree add` during the cutoff campaigns put one run over the foreign CPU
threshold (ADR 0051: CPU time used by other processes during a run), and that run had to be
repeated (PR #103 of the working repository). The requirement that followed: nothing but the campaign runs on the PC
while it measures. That includes the AI coding assistant used during development (Claude Code),
which can start commands on the PC at any time.

## Decision

- **Automatic quiet mode.** `make campaign`, `make cutoff-campaigns` and `make grain-campaigns`
  turn quiet mode on before the first run.
  - An EXIT trap turns it off again, also when the campaign fails or is interrupted.
  - The EXIT trap is set before quiet mode starts, so a failure inside `quiet.sh on` still runs
    `off`. INT and TERM exit through the same trap.
  - `QUIET=0` runs without it.
- **The assistant is paused.** `quiet.sh on` also stops every Claude Code process with SIGSTOP,
  and `quiet.sh off` continues them with SIGCONT.
  - A stopped process keeps its children running, so a campaign that the assistant started goes
    on.
  - Such a campaign's output must go to a file, not to the assistant's pipe.
  - `QUIET_KEEP_CLAUDE=1` keeps the assistant running.
  - `off` continues a PID only if it is still a `claude` process.
- **What is not touched.** The terminal and the shell that run `make`.

## Consequences

- **A change of environment state.** The campaigns before this ADR ran with quiet mode turned
  on by hand, and with the assistant running. Comparisons across campaigns are across that
  change. Foreign CPU stayed under the threshold in all of them except the one run repeated in
  PR #103.
- **No load from the assistant.** No command from the assistant can load the PC during a
  campaign.
- **Recovery.** If a campaign is killed so hard that the trap does not run, `make quiet-off`
  continues the assistant. The PIDs are in the quiet state file.

## Status

Accepted
