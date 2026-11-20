# Data quality: campaign-v2

- Runs done: 4860; missing: 0; failed: 0 {}
- Runs replaced by a re-run (kept in `excluded/`): 0
- Checksum conflicts: 0
- Runs failing strict validation: 0 {}; reasons: {}
- Runs above the foreign CPU threshold (0.25 s): 0 {}
- Configurations under 100 times the clock resolution: 0
- Configurations whose valid run values trend with the execution order (|rho| > 0.5, at least 10 runs): 3
  - chrome hist-atomic k1 N=8: rho = -0.56 over 30 runs
  - chrome hist-atomic k16 N=4: rho = -0.62 over 30 runs
  - firefox hist-local k4 N=4: rho = -0.62 over 30 runs
- Configurations mixing width, height, pitch, palette, passes: 0
- Blocking the analysis (checksum conflicts, missing or failed runs, mixed settings): no
