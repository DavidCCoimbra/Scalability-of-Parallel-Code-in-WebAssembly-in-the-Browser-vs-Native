# ADR 0046: Headless browsers, with the difference to headful measured

Date: 2026-11-07

## Context

A browser can run headful (with a visible window, as a user would see the page) or headless
(without any window or display). Headful is closer to how a page runs for a real user, which
makes it the more realistic setting; headless is simpler to run unattended for many hours. The
choice matters for the measurements only if the window, its compositor and its rendering take
CPU time from the workers or otherwise change the timings, so it needed data before the
campaign.

The rule was fixed before measuring: run headless if the effect of the mode is negligible, and
report the number; run headful otherwise. "Negligible" means that the 95 % interval of the
ratio headful / headless includes 1 and the ratio is within 2 %.

The pilot (`harness/campaigns/pilot-head{less,ful}.json`, 2026-11-07; these pilot specs and
their data are in the working repository) ran:

- the Gaussian filter (W = 15 warm-up iterations) and `hist-local` (the per-task local
  histogram) at k = 1 (W = 71), at 8192x8192 and N = 8 threads;
- 10 runs per browser in each mode, in quiet mode (ADR 0042), with every browser process inside
  the run's CPU scope (ADR 0045). All 80 runs have `escapedProcesses` = 0, that is, no browser
  process left the scope.

The headful windows opened on the PC's idle, unlocked GNOME desktop session.

Two limits of the pilot:

- The two modes ran one after the other (headless from 02:38, headful from 02:41), not
  interleaved under one random seed. A difference between them would therefore be confounded
  with drift of the machine over time. With bounds of 0.3 % (below), this does not change the
  conclusion.
- One headful run recorded the commit of another branch, because the branch was switched during
  the campaign. That run was set aside and the campaign resumed, which ran it again. The resume
  is the second sysinfo file and the 41st line of `campaign.jsonl`; the directory holds exactly
  40 runs, one per planned run id.

Results:

| Configuration | headless (ms, CV) | headful (ms, CV) | headful / headless [95 % CI] | Cliff's delta |
|---|---|---|---|---|
| Chrome filter N = 8 | 3.90, 1.0 % | 3.89, 0.7 % | 0.998 [0.989, 1.009] | -0.07 |
| Chrome `hist-local` k1 N = 8 | 19.07, 0.3 % | 19.08, 0.5 % | 1.001 [0.997, 1.006] | +0.23 |
| Firefox filter N = 8 | 4.16, 0.5 % | 4.17, 0.8 % | 1.002 [0.999, 1.012] | +0.43 |
| Firefox `hist-local` k1 N = 8 | 20.19, 1.5 % | 20.24, 0.4 % | 1.003 [0.993, 1.006] | +0.13 |

The times are the median of the per-run medians; CV is the run-to-run coefficient of
variation; the ratio is a ratio of medians with a 95 % percentile bootstrap interval over runs;
Cliff's delta (a rank-based effect size from -1 to +1) is computed over runs.

## Decision

The rule fixed before the pilot was applied on 2026-11-07:

- The campaign runs both browsers headless (`--headless=new` for Chrome, `-headless` for
  Firefox). Every interval includes 1 and every ratio is within 0.3 %, well inside the 2 %
  bound of the rule.

## Consequences

- The methodology states the measured difference: headful changes the median by at most 0.3 %
  at N = 8 in these workloads.
- Only N = 8 was compared, because that is where the browser's own threads compete most with
  the workers for the cores. That other N do not differ is assumed, not tested.
- The bound holds for headful windows on an idle, unlocked desktop session. Because the campaign
  is headless, its results do not depend on the state of the desktop session.

## Status

Accepted
