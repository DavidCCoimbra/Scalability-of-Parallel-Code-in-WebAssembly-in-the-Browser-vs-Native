# ADR 0042: Quiet mode before measuring and no sleep during a campaign

Date: 2026-11-06

## Context

The shield (ADR 0028) keeps the rest of the system on the E-cores (the efficiency cores of the
hybrid i9-14900KF), so no foreign process runs on the measured P-cores. But the CPU's last-level
cache (LLC) and memory bandwidth are still shared between P- and E-cores. Desktop apps left open
and background work that comes in bursts (the GNOME indexer, apt and snap updates, firmware
checks, docker) can therefore still disturb a run through those shared resources. A long
campaign could also be cut short by the PC going to sleep.

## Decision

Decided by the author on 2026-11-06:

- **Quiet mode.** `make quiet` (`harness/env/quiet.sh on`) is run before every measuring session,
  after `make env-setup`. It closes desktop apps and stops the indexer, evolution,
  speech-dispatcher, the apt timers and unattended-upgrades, snapd, fwupd, packagekit, docker and
  containerd, until a reboot or `make quiet-off`. It never touches the session that runs it (its
  ancestor processes, such as an editor's terminal) or the pinned browsers.
- **No sleep.** `make campaign` runs under `systemd-inhibit --what=sleep:idle` when the command
  exists. It does not stop the screen lock, which does not matter for headless runs.
- **Recorded.** `sysinfo` (written by every `env-check` and every campaign start) records
  `quietMode`: whether it is on and which units it stopped, so runs with and without it can be
  told apart.

## Consequences

- Fewer bursts of foreign work on the shared caches and memory during a run;
  `foreignCpuSeconds` (ADR 0028) still measures what is left on the P-cores.
- Quiet mode is recorded, not enforced: a session without it still runs, and its sysinfo says
  so. It is not a strict-validation condition.

## Status

Accepted
