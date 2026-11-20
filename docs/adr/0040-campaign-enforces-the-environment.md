# ADR 0040: The campaign enforces the environment check on every start

Date: 2026-10-27

## Context

An independent review of `main` at commit `3c11115` found three gaps between the campaign
orchestrator (ADR 0034) and the environment check (ADR 0035):

- **No check before a campaign.** `harness/campaign.py` never called the environment check. After
  a reboot (turbo and SMT back on, shield gone) a strict campaign would spend hours producing
  runs that strict validation then throws away.
- **The discarded first launch was skipped on resume.** The first launch of a browser on a
  machine is slow (ADR 0034), and it was discarded only at the very start of a campaign. So the
  first browser launch after a reboot, in a resumed campaign, would be a measured run.
- **The only shipped spec could not run on the PC.** `mini.json` had no scope user and was not
  strict, and a run without a scope user fails with the shield on (the shield restricts the
  user's session to the E-cores, so the run needs its own systemd scope, ADR 0028).

## Decision

- **Check on every start.** A strict campaign needs a CPU mask. On every start and every resume
  it runs the environment check on that mask, writes the system state to
  `<campaign>/sysinfo/<UTC time>.json` with the problems found, and stops with an error before
  any run if there is a problem.
- **A discarded launch per session.** The discarded first launch carries the session number in
  its run id (`<name>-discard<session>-...`), so it runs again at the start of every session. The
  session number is 1 plus the number of recorded resumes.
- **Portable scope user.** `scopeUser: "$USER"` resolves to the user running the harness, so a
  spec does not depend on the account name on the PC.
- **A smoke spec for the PC.** `harness/campaigns/smoke.json` is the spec for the end-to-end smoke
  test on the PC: strict, run scope as `$USER`, P-core mask `0,2,4,6,8,10,12,14`, harness on
  `16-31`.

## Consequences

- A campaign cannot run on an unprepared machine; the saved system state shows why it stopped.
- Each session's first browser launch is discarded, not only the campaign's first.
- Non-strict campaigns (development on the Mac) keep working without the check.
- The machine is checked once per session, before any run; a refused start is not recorded as a
  resume. A change during a long session (for example turbo switched back on) is caught run by
  run by strict validation (ADR 0023, ADR 0025), which every run's context goes through in the
  analysis.

## Status

Accepted; amends ADR 0034 (orchestrator) and ADR 0035 (environment check)
