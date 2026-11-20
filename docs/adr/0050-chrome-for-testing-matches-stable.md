# ADR 0050: Chrome for Testing gives the same numbers as Chrome stable

Date: 2026-11-07

## Context

The campaign uses Chrome for Testing 155.0.8059.84 (ADR 0021). Chrome for Testing is Google's
build of Chrome for testing: a fixed version can still be downloaded later, with the same
V8/Blink as Chrome stable of that version (ADR 0007), which makes the browser environment
reproducible. It was chosen to stay close to the browser users run while keeping a pinned build
that needs no automation framework. ADR 0007 recorded the assumption that it performs like
Chrome stable of the same version as a threat to validity, with an optional check.

The open question was whether that testing build behaves like the branded stable Chrome. If it
did not, the browser results would describe a build that users do not run. To compare like
with like, both must have the same V8 engine. On 2026-11-07 the stable Chrome was
157.0.8103.38, so the same-engine comparison used:

- Chrome for Testing 157.0.8103.38 (SHA-256 of the archive
  8cdeb344e9b2cefe59f4aea8d1d93d5d93054c03cde217665c16fc1f62e72a66);
- stable 157.0.8103.38 (`google-chrome-stable_current_amd64.deb`, SHA-256
  a62b277dc03da2cff50cc04589deb66f6875be339c066d46adb49b49eedb629d, extracted without
  installing).

The pinned 155 was run too, to see how much the version itself matters.

### Pilot

The pilot (`harness/campaigns/pilot-chrome-{cft155,cft157,stable157}.json`; in the working
repository) ran the filter at N = 1 and 8 and `hist-atomic` k = 16 at N = 1 and 8, at
8192x8192, 10 runs each, with the 3 s start delay (ADR 0048). It ran as three campaigns one
after the other: 120 runs, all with `escapedProcesses` = 0.

Differences between the three that were not controlled:

- the order: CfT 155, then CfT 157, then stable 157, about 10 minutes each, not interleaved;
- the 157 runs were not strict runs, because their version is not the pinned one;
- stable ran from an extracted `.deb` rather than an installed package.

`hist-atomic` k16 at N = 1 has a run-to-run CV of 0.007 %, hence its narrow interval. Ratio of
geometric means (`analysis/compare.py`, 95 % bootstrap interval):

| Configuration | stable 157 / CfT 157 | CfT 157 / CfT 155 |
|---|---|---|
| filter N = 1 | 0.998 [0.988, 1.008] | 1.000 [0.991, 1.011] |
| filter N = 8 | 1.013 [1.005, 1.020] | 0.994 [0.987, 1.001] |
| `hist-atomic` k16 N = 1 | 1.0001 [1.0000, 1.0002] | 0.998 [0.995, 1.000] |
| `hist-atomic` k16 N = 8 | 1.003 [0.998, 1.008] | 0.998 [0.993, 1.002] |

## Decision

Decided on 2026-11-07; the option recommended from the data above was applied:

- Chrome for Testing 155 stays the campaign's Chrome. Stable and Chrome for Testing of the same
  version differ by at most 1.3 % in the configurations tried (point estimates; 2.0 % at the upper
  end of the widest interval), and 155 and 157 differ by at most 0.6 %.
- The filter at N = 8 is the one interval that excludes 1 ([1.005, 1.020]). Because the builds
  ran one after the other, a real 1.3 % build effect there cannot be ruled out, but it is small
  against the environment differences the study measures.

## Consequences

- The paper can say that the testing build behaves like the stable one within about 1.3 % for
  the filter and `hist-atomic` k = 16, with the numbers above. Other workloads (for example
  `hist-atomic` k = 1) were not compared.
- Only Chrome was checked: Firefox is the official release build (ADR 0021).

## Status

Accepted
