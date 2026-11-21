# Excluded runs

The 360 Firefox runs of this campaign that ran on Firefox 160.0.

- Why: Firefox updated itself from the pinned 158.0 to 160.0 in the middle of the extras
  campaigns (ADR 0071). A campaign compares one pinned browser version, so these runs are not
  analysed.
- Replacement: Firefox 158.0 was reinstalled and every one of these planned runs ran again from
  the same build, `measured/v2`, with the same spec and seed, in its planned position among the
  Firefox runs. The repeated runs are in the campaign folder and report 158.0 in their context.
  They ran as one block after the native and Chrome runs, not interleaved with them; ADR 0071
  records the control for that.
