# ADR 0061: Results of the hybrid P+E campaign

Date: 2026-11-08

## Context

The study normally measures on the 8 P-cores (performance cores) of the i9-14900KF only
(ADR 0045). The chip also has 16 E-cores (efficiency cores: smaller, slower cores; 2.4 GHz with
turbo off, against 3.2 GHz for the P-cores). The hybrid campaign of ADR 0059 asked how Rayon's
work stealing (idle threads take queued tasks from busy ones) copes with these heterogeneous
cores, natively and in the browsers. Its CPU mask holds every P-core plus 12 E-cores, and it
measures the filter and the local histogram at k = 1 at N in {1, 8, 12, 16, 20}.

The campaign ran from tag `measured/hybrid` (7624d024): 900 runs, 0 missing, 0 failed, 0
checksum conflicts, 0 runs failing strict validation (in hybrid mode), 0 runs above the foreign
CPU threshold (`data/tables/hybrid/hybrid-quality.md`). Tables:
`data/tables/hybrid/hybrid-scaling.csv` and `data/tables/hybrid/hybrid-iteration-drift.csv`.
Figures: `paper/figures/hybrid-speedup.pdf` and `paper/figures/hybrid-absolute.pdf`. These are
the tables and figures of this build; they are in the working repository, and the final
repository holds the re-run on the v2 build (ADR 0069, `data/tables/hybrid-v2/`).

The P-only reference is the main campaign (`data/tables/campaign/campaign-scaling.csv`), which
ran on other days. ADR 0058 states the same caveat for its SIMD comparison.

Two probes were added after the campaign to interpret the result (both in the working
repository):

- `data/probes/ecore-workloads.txt` (in the working repository, like the next file): the native runner at N = 1 pinned to one P-core (CPU 2)
  or one E-core (CPUs 16, 20, 24), 10 measured iterations each.
- `data/probes/rmw-chain-ecore.txt`: the read-modify-write microbenchmark of ADR 0060 on
  E-cores (CPUs 16, 22, 26), with a P-core control.

## Decision

Record the following reading of the results (geometric-mean times, 95 % bootstrap intervals in
the tables).

### Filter

Time per iteration (ms):

| N | native | Chrome | Firefox |
|---|---|---|---|
| 8 (P-only, main campaign) | 3.26 | 3.85 | 4.13 |
| 8 (hybrid mask) | 3.53 | 4.06 | 4.34 |
| 12 | 3.11 | 3.54 | 3.71 |
| 16 | 2.90 | 3.50 | 3.58 |
| 20 | 2.88 | 3.52 | 3.54 |

- **E-cores help, but the filter flattens.** Adding 12 E-cores makes the filter 12 % faster
  natively, 9 % in Chrome and 14 % in Firefox than the P-only N = 8. The speedup flattens at
  about 8 from N = 16 in all three environments. The probe gives an E-core 0.76 of a P-core's
  speed on this workload (29.7 against 22.6 ms), so the CPUs alone would allow a speedup of
  about 8 + 12 x 0.76 = 17. Something else limits the filter, plausibly memory bandwidth (not
  measured).
- **The browsers use the E-cores about as well as native.** The browser / native ratio barely
  moves within the campaign: Chrome 1.15 at N = 8 and 1.22 at N = 20, Firefox 1.23 at both
  (against 1.18 and 1.27 for the P-only N = 8). The browsers' thread pools use the E-cores about
  as well as native Rayon does on this workload.
- **The mask matters even at the same N.** With the hybrid mask, N = 8 is 5 to 8 % slower than
  with the P-only mask. Thread placement was not logged; the inference is that the kernel puts
  some of the 8 threads on E-cores even when P-cores are free. The run spread supports it:
  native filter N = 8 per-run medians range from 3.35 to 4.27 ms (P-only campaign: 3.22 to
  3.31), and one Chrome k = 1 run at N = 8 takes 15.82 ms, below the 18.8 ms that 8 P-cores
  allow (150.6 / 8).
- **The cross-campaign reference holds.** The P-only reference is another campaign on other
  days. T1 agrees within 0.5 % (native 22.62 against 22.72 ms, Chrome 26.84 against 26.85,
  Firefox 30.79 against 30.68), and every hist-local N = 1 run sits at 150 to 156 ms, so T1 ran
  on a P-core.

### Local histogram, k = 1

Speedups exceed N: at N = 20 native 23.7, Chrome 29.3, Firefox 24.7 (times 6.54, 5.13 and
6.31 ms). This is not super-linear scaling in the usual sense (better than ideal because of,
for example, more total cache). On this loop an E-core at 2.4 GHz is faster than a P-core at
3.2 GHz (single-core probes; E-cores share an L2 cache per cluster of four, and that sharing at
N = 20 was not probed):

- **Native runner at N = 1.** 154.9 ms on a P-core. On an E-core iterations take 74.3 to
  115.7 ms (medians 74.6, 85.9 and 115.5 ms on CPUs 16, 20 and 24), and they switch between a
  fast mode near 75 ms and a slow mode near 115 ms.
- **The microbenchmark shows the same.** At k = 1 every pixel increments the same counter, so
  the loop is a chain of read-modify-write operations through one memory address (ADR 0060).
  On the indexed-address form of that chain that the k = 1 loop compiles to, the
  memory-destination `inc [b+i*8]` takes 2.7 to 4.1 cycles per pixel on an E-core against 7.4
  on a P-core. The load/add/store sequence that V8 emits runs at 42 to 86 ms on an E-core
  against 151 to 153 ms on a P-core. The advantage is specific to that addressing: with a
  plain register address the P-core is 3 to 6 times faster (24 ms against 80 to 155 ms). The
  E-core times are bimodal across sessions and cores; the P-core times are stable in the one
  P-core session measured per probe.
- **What that predicts.** For native code each E-core thread is worth 1.3 to 2.1 P-core
  threads, so a balanced split would reach 8 + 12 x (1.3 to 2.1) = 24 to 33 at N = 20; native
  reaches 23.7, at the bottom. For Chrome's sequence the ratio is 1.7 to 3.6 (150.6 ms against
  42 to 86), so 29 to 51; Chrome reaches 29.3, also at the bottom. Firefox's machine code was
  not extracted. A speedup at the bottom of the range fits balanced work on E-cores in their
  slow mode as well as unbalanced work in the fast mode. So the results are consistent with
  work stealing balancing the heterogeneous cores in all three environments, without proving
  it.
- **Why Chrome gains most.** V8's load/add/store sequence gains most on the E-cores
  (ADR 0060). The browser / native ratio for Chrome goes from 0.96 at N = 8 to 0.70 at N = 16
  and 0.79 at N = 20; for Firefox from 1.01 to 0.87 and 0.97. The k = 1 local histogram is the
  case where the choice of instructions dominates: the gap is a microarchitecture effect, not a
  threading effect.

### Drift with execution order

Four filter configurations trend with their position in the execution order (Spearman |rho|
0.52 to 0.67, runs getting faster): Chrome and Firefox at N = 16, Firefox and native at N = 20.
They sit where the filter has already flattened, so they do not change the reading above, but
they are reported as a threat to validity.

Chrome filter N = 1 has two runs at 32.2 ms against 26.1 to 27.0 for the rest. The P-only
campaign has the same two-run mode (32.3 ms), so it is a Chrome mode, not E-core placement. It
widens the Chrome filter intervals, not their centres.

## Consequences

- **What is claimed.** The paper gets one paragraph in the exploratory results, and the pilot
  report gets a section with both figures. The claim is limited to two points: the browsers use
  E-cores about as well as native Rayon for the filter, and the k = 1 histogram speedups above
  N are consistent with the E-cores running the indexed-address read-modify-write chain faster than the
  P-cores.
- **What is not investigated.** Why the E-core is faster on this chain and slower on the
  register form (differences between the Gracemont and Raptor Cove cores in memory
  disambiguation or store forwarding, and the bimodal modes) is not investigated: `perf` was
  not available at the time (`perf_event_paranoid` = 4, later changed by ADR 0068), and the
  extra is exploratory.
- **No efficiency figure.** Strong-scaling efficiency (speedup / N) is not a meaningful number
  on a mask with two kinds of core, so the efficiency figure is not kept.
- **Reproduction.** `make extras-results` regenerates the tables and both figures. The hybrid
  speedup figure labels its diagonal "speedup = N", not "ideal".
- **A limit of the stored-run check.** Validating stored runs in `hybrid` mode cannot check
  that the mask holds every P-core, because the recorded `pCpus` also lists the offline SMT
  siblings. The live environment check does it, and refuses a hybrid mask when the P-cores are
  unknown.

## Status

Accepted
