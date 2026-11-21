# Quick checks: tiny copies of every campaign of the study, to check that the
# pipeline works end to end and to watch a run. NOTHING HERE PRODUCES RESULTS
# FOR THE PAPER. The specs are harness/campaigns/quick-*.json and their runs
# land in data/raw/quick-* (ignored by git).
#
# Every quick spec keeps the design of its real spec (environments,
# workloads with their W, build variant, CPU mask, hybrid flag, start delay,
# discarded first launch) and shrinks the rest: 3 runs (1 for headless),
# few N, 4096x4096 (weak keeps 8192 wide and 1024 rows per thread),
# 5 measured iterations. All are
# "strict": false, so they run on an unprepared machine, and
# "scopeUser": null, so they need no sudo; a strict real campaign checks
# the machine and confines each run to a systemd scope.
#
# Target          Spec(s)                          Real campaign
# quick-rq1       quick-rq1                        campaign-v2 (filter)
# quick-rq2       quick-rq2                        campaign-v2 (histograms)
# quick-headless  quick-headless                   one headless filter run per browser
# quick-extras    quick-extras                     extras-v2
# quick-weak      quick-weak                       weak-v2
# quick-simd      quick-simd-scalar, -simd-avx2    simd-scalar-v2, simd-avx2-v2
# quick-hybrid    quick-hybrid                     hybrid-v2
#
# quick runs every target above except quick-hybrid, which measures on
# E-cores outside the P-core mask of every other campaign. quick-simd runs last because the
# scalar variant overwrites bench/www/pkg; the next baseline campaign
# rebuilds it.

QUICK_SPEC = harness/campaigns/quick-$(1).json
QUICK_TARGETS = quick-rq1 quick-rq2 quick-headless quick-extras quick-weak quick-simd
QUICK_SUMMARY = rq1 rq2 headless extras weak simd-scalar simd-avx2

# $(call quick-run,<spec suffix>): the campaign, then its status, which runs even if the campaign failed.
# The + makes make -n print the commands of both sub-makes.
define quick-run
+$(MAKE) campaign SPEC=$(call QUICK_SPEC,$(1)); outcome=$$?; $(MAKE) status SPEC=$(call QUICK_SPEC,$(1)); exit $$outcome
endef

.PHONY: quick quick-summary $(QUICK_TARGETS) quick-hybrid

##@ Quick checks (not results; not strict; before env-setup, whose shield refuses their plain taskset; into data/raw/quick-*)

quick: ## All quick checks below but hybrid, then a summary (about 20 min plus builds)
	@failed=; for target in $(QUICK_TARGETS); do $(MAKE) $$target || failed="$$failed $$target"; done; \
	$(MAKE) quick-summary; \
	if [ -n "$$failed" ]; then echo "failed:$$failed"; exit 1; fi

quick-summary: ## One progress line per quick spec that quick runs (read-only)
	@for spec in $(QUICK_SUMMARY); do \
		python3 -m harness.campaign.status $(call QUICK_SPEC,$$spec) | awk 'NR == 1 {name = $$2} NR == 2 {sub(/^progress +/, ""); printf "%-18s %s\n", name, $$0}'; \
	done

quick-rq1: ## RQ1: filter, N 1 and 8, three environments (not strict)
	$(call quick-run,rq1)

quick-rq2: ## RQ2: hist-atomic and hist-local, k 1 and 256, N 8 (not strict)
	$(call quick-run,rq2)

quick-headless: ## One filter run per browser, headless (not strict)
	$(call quick-run,headless)

quick-extras: ## Private and packed atomics at k 1, sort and sort-unstable (not strict)
	$(call quick-run,extras)

quick-weak: ## Weak scaling: filter and hist-local k 1, 1024 rows per thread (not strict)
	$(call quick-run,weak)

quick-simd: ## SIMD variants: scalar build, then avx2 native (not strict)
	$(call quick-run,simd-scalar)
	$(call quick-run,simd-avx2)

quick-hybrid: ## P+E mask with "hybrid": N 1, 8 and 20 (not strict; not in quick)
	$(call quick-run,hybrid)
