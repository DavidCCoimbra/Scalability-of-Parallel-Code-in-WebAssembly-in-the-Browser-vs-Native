# Data quality: extras-v3

- Runs done: 5400; missing: 0; failed: 0 {}
- Runs replaced by a re-run (kept in `excluded/`): 0
- Checksum conflicts: 0
- Runs failing strict validation: 0 {}; reasons: {}
- Runs above the foreign CPU threshold (0.25 s): 0 {}
- Configurations under 100 times the clock resolution: 0
- Configurations whose valid run values trend with the execution order (|rho| > 0.5, at least 10 runs): 1
  - chrome hist-atomic-private k1 N=2: rho = +0.52 over 30 runs
- Configurations mixing width, height, pitch, palette, passes: 0
- Blocking the analysis (checksum conflicts, missing or failed runs, mixed settings): no
