# core-check

The per-core check of 2026-11-21, run on the measuring PC before the v3 build. None of its
runs is a result; they answer whether every P-core of the mask is fit to measure with.

| File | Contents |
|---|---|
| `runs/` | 80 runs of the native filter at one thread, 8192x8192, each pinned to one P-core (`core-check-c<cpu>-r<round>`): the run's CSV and its context, with the busy time and frequency of that CPU in `cores` |
| `pinned-python.txt` | The analysis tests repeated on one CPU at a time, with turbo off |
| `turbo-on-segfaults.txt` | The same tests with turbo on, as the PC was found, and the kernel's record of each crash |
| `build-digests.txt` | The digests of three builds from scratch |
| `host-as-found.json`, `host-prepared.json` | The host before and after `make env-setup` |

The runs were launched with `python3 -m harness.native --cpus <cpu> --scope-user $USER`, in
ten rounds over the eight CPUs, each round starting one CPU further. What they show is in
ADR 0085.
