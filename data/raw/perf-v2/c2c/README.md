# perf c2c on measured/v2 (ADR 0072)

One `hist-atomic` k = 16, N = 8 run per browser on `measured/v2`, recorded with
`perf c2c record -a` on the eight P-cores (`run.sh`, specs `spec-chrome.json` and
`spec-firefox.json`; the runs and their `campaign-*.json` are kept next to them).
A layout check, not a timing measurement: the run times are not reported.

- `c2c-chrome.txt`, `c2c-firefox.txt`: `perf c2c report --stdio`. In both, the 16
  contended lines are 0x800 bytes apart (16 counters x 128 bytes) and every access
  is at offset 0: each padded counter is alone on its line in WASM memory.
