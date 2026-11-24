# Data quality: hybrid

- Runs done: 900; missing: 0; failed: 0 {}
- Checksum conflicts: 0
- Runs failing strict validation: 0 {}; reasons: {}
- Runs above the foreign CPU threshold (0.25 s): 0 {}
- Configurations under 100 times the clock resolution: 0
- Configurations whose valid run values trend with the execution order (|rho| > 0.5, at least 10 runs): 4
  - chrome filter N=16: rho = -0.56 over 30 runs
  - firefox filter N=16: rho = -0.67 over 30 runs
  - firefox filter N=20: rho = -0.52 over 30 runs
  - native filter N=20: rho = -0.66 over 30 runs
- Blocking the analysis (checksum conflicts, missing or failed runs): no
