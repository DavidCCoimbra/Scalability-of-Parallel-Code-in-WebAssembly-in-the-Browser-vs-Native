SENSITIVITY = data/tables/campaign-$(MEASURED)/sensitivity/campaign-$(MEASURED)
RESULTS = python3 -m analysis.results data/raw/campaign-$(MEASURED) --max-threads 8 --strict

.PHONY: results sensitivity extras-results extras-workloads-results hybrid-results weak-results simd-results cutoff-results grain-results perf-results v3-results all-results tables-check

##@ Tables and figures of the paper

results: ## Every table and figure of the main campaign (MEASURED=v3 by default)
	mkdir -p paper/figures data/tables/campaign-$(MEASURED)
	python3 -m analysis.datacheck data/raw/campaign-$(MEASURED) --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-quality.md
	python3 -m harness.collect data/raw/campaign-$(MEASURED) --output data/campaign-$(MEASURED).csv
	python3 -m analysis.v0 data/raw/campaign-$(MEASURED) --strict --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-scaling.csv
	python3 -m analysis.results data/raw/campaign-$(MEASURED) --max-threads 8 --strict --foreign-cpu-threshold 0.25 --contrasts data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-contrasts.csv --shape data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-shape.csv
	$(MAKE) sensitivity
	python3 -m analysis.robustness data/raw/campaign-$(MEASURED) --max-threads 8 --strict --foreign-cpu-threshold 0.25 --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-robustness.csv
	python3 -m analysis.rq2_decomposition data/raw/campaign-$(MEASURED) --max-threads 8 --strict --foreign-cpu-threshold 0.25 --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-rq2-decomposition.csv
	python3 -m analysis.calibration data/raw/campaign-$(MEASURED) --strict --foreign-cpu-threshold 0.25 --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-fork-join.csv
	python3 -m analysis.throughput data/raw/campaign-$(MEASURED) --strict --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-throughput.csv
	python3 -m analysis.karp_flatt data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-scaling.csv --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-karp-flatt.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/campaign-$(MEASURED) --strict --output paper/figures --prefix campaign
	uv run --no-project --with matplotlib python -m analysis.distributions data/raw/campaign-$(MEASURED) --strict --figure paper/figures/campaign-distributions.pdf --table data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-distributions.csv

# The sensitivity checks of the analysis plan (ADR 0037): per-run mean, median centre, and
# no exclusion by foreign CPU time. A conclusion that changes under one is not robust.
sensitivity: #: The plan's three sensitivity checks on the primary contrasts
	mkdir -p $(dir $(SENSITIVITY))
	$(RESULTS) --summary mean --contrasts $(SENSITIVITY)-summary-mean.csv
	$(RESULTS) --center median --contrasts $(SENSITIVITY)-center-median.csv
	$(RESULTS) --no-foreign-cpu-threshold --contrasts $(SENSITIVITY)-no-threshold.csv
	python3 -m analysis.sensitivity --primary data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-contrasts.csv \
		--check summary_mean=$(SENSITIVITY)-summary-mean.csv --check center_median=$(SENSITIVITY)-center-median.csv \
		--check no_threshold=$(SENSITIVITY)-no-threshold.csv --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-sensitivity.csv

# The extras, weak scaling, SIMD and hybrid tables each have their own target, so that one
# campaign's tables do not wait for another campaign's data.
extras-results: extras-workloads-results weak-results simd-results hybrid-results ## Tables and figures of the exploratory campaigns: extras, weak scaling, SIMD, hybrid P+E

extras-workloads-results: ## The extra workloads: private, shared and packed atomics, the local control, sorts
	mkdir -p data/tables/extras-$(MEASURED) paper/figures
	python3 -m analysis.datacheck data/raw/extras-$(MEASURED) --output data/tables/extras-$(MEASURED)/extras-$(MEASURED)-quality.md
	python3 -m harness.collect data/raw/extras-$(MEASURED) --output data/extras-$(MEASURED).csv
	python3 -m analysis.v0 data/raw/extras-$(MEASURED) --strict --output data/tables/extras-$(MEASURED)/extras-$(MEASURED)-scaling.csv
	python3 -m analysis.results data/raw/extras-$(MEASURED) --max-threads 8 --strict --foreign-cpu-threshold 0.25 --partial --contrasts data/tables/extras-$(MEASURED)/extras-$(MEASURED)-contrasts.csv --shape data/tables/extras-$(MEASURED)/extras-$(MEASURED)-shape.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/extras-$(MEASURED) --strict --output paper/figures --prefix extras

hybrid-results: ## P-cores plus E-cores
	mkdir -p data/tables/hybrid-$(MEASURED) paper/figures
	python3 -m analysis.datacheck data/raw/hybrid-$(MEASURED) --output data/tables/hybrid-$(MEASURED)/hybrid-$(MEASURED)-quality.md
	python3 -m analysis.v0 data/raw/hybrid-$(MEASURED) --strict --output data/tables/hybrid-$(MEASURED)/hybrid-$(MEASURED)-scaling.csv
	python3 -m analysis.iteration_drift data/raw/hybrid-$(MEASURED) --output data/tables/hybrid-$(MEASURED)/hybrid-$(MEASURED)-iteration-drift.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/hybrid-$(MEASURED) --strict --output paper/figures --prefix hybrid --diagonal "speedup = N"
	rm -f paper/figures/hybrid-efficiency.pdf

weak-results: ## Weak scaling: the image grows with the thread count
	mkdir -p data/tables/weak-$(MEASURED) paper/figures
	python3 -m analysis.datacheck data/raw/weak-$(MEASURED) --output data/tables/weak-$(MEASURED)/weak-$(MEASURED)-quality.md
	python3 -m analysis.v0 data/raw/weak-$(MEASURED) --strict --weak --output data/tables/weak-$(MEASURED)/weak-$(MEASURED)-scaling.csv
	python3 -m analysis.iteration_drift data/raw/weak-$(MEASURED) --output data/tables/weak-$(MEASURED)/weak-$(MEASURED)-iteration-drift.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/weak-$(MEASURED) --strict --output paper/figures --prefix weak
	rm -f paper/figures/weak-speedup.pdf paper/figures/weak-efficiency.pdf

simd-results: ## The SIMD build variants of the filter: scalar, baseline and AVX2
	mkdir -p data/tables/simd-$(MEASURED)
	for c in simd-scalar simd-avx2; do \
	  python3 -m analysis.datacheck data/raw/$$c-$(MEASURED) --output data/tables/simd-$(MEASURED)/$$c-$(MEASURED)-quality.md && \
	  python3 -m analysis.v0 data/raw/$$c-$(MEASURED) --strict --output data/tables/simd-$(MEASURED)/$$c-$(MEASURED)-scaling.csv && \
	  python3 -m analysis.iteration_drift data/raw/$$c-$(MEASURED) --output data/tables/simd-$(MEASURED)/$$c-$(MEASURED)-iteration-drift.csv || exit 1; \
	done
	uv run --no-project --with matplotlib python -m analysis.extras.build_variants --strict baseline=data/raw/campaign-$(MEASURED) scalar=data/raw/simd-scalar-$(MEASURED) avx2=data/raw/simd-avx2-$(MEASURED) --table data/tables/simd-$(MEASURED)/simd-$(MEASURED)-variants.csv --figure paper/figures/simd-efficiency.pdf

cutoff-results: ## Cutoff campaigns: data check and v0 per size, then the cutoff table, estimates, model and figure
	mkdir -p data/tables/cutoff-$(MEASURED)
	for side in $(CUTOFF_SIDES) control-512 control-2048; do \
	  python3 -m analysis.datacheck data/raw/cutoff-$$side-$(MEASURED) --output data/tables/cutoff-$(MEASURED)/cutoff-$$side-$(MEASURED)-quality.md && \
	  python3 -m analysis.v0 data/raw/cutoff-$$side-$(MEASURED) --strict --output data/tables/cutoff-$(MEASURED)/cutoff-$$side-$(MEASURED)-scaling.csv || exit 1; \
	done
	uv run --no-project --with matplotlib python -m analysis.cutoff --strict $(foreach side,$(CUTOFF_SIDES),data/raw/cutoff-$(side)-$(MEASURED)) \
		--table data/tables/cutoff-$(MEASURED)/cutoff-table.csv --estimates data/tables/cutoff-$(MEASURED)/cutoff-estimates.csv --model data/tables/cutoff-$(MEASURED)/cutoff-model.csv \
		--figure paper/figures/cutoff-speedup.pdf

grain-results: ## Grain sweep campaigns: data check per size, then the U-curve points, best grains and figure
	mkdir -p data/tables/grain-$(MEASURED)
	for side in $(GRAIN_SIDES); do \
	  python3 -m analysis.datacheck data/raw/grain-$$side-$(MEASURED) --output data/tables/grain-$(MEASURED)/grain-$$side-$(MEASURED)-quality.md || exit 1; \
	done
	uv run --no-project --with matplotlib python -m analysis.grain --strict $(foreach side,$(GRAIN_SIDES),data/raw/grain-$(side)-$(MEASURED)) \
		--points data/tables/grain-$(MEASURED)/grain-points.csv --best data/tables/grain-$(MEASURED)/grain-best.csv --figure paper/figures/grain-ucurve.pdf \
		--paper-figure paper/figures/grain-ucurve-8192.pdf

perf-results: ## Hardware counters per atomic add and V8's retries from the perf campaign
	mkdir -p data/tables/perf-$(MEASURED)
	python3 -m analysis.datacheck data/raw/perf-$(MEASURED) --output data/tables/perf-$(MEASURED)/perf-$(MEASURED)-quality.md
	python3 -m analysis.extras.perf_counters data/raw/perf-$(MEASURED) --strict --runs data/tables/perf-$(MEASURED)/perf-$(MEASURED)-runs.csv \
		--summary data/tables/perf-$(MEASURED)/perf-$(MEASURED)-counters.csv --retries data/tables/perf-$(MEASURED)/perf-$(MEASURED)-retries.csv

# What only the v3 build has: the sequential references and the busy time per core of the main
# campaign, the engine arms, the grain by threads and the counters of the loop alone (ADR 0088).
v3-results: ## The tables of the campaigns that only measured/v3 has
	mkdir -p $(foreach name,campaign tier grain-threads perf-loop,data/tables/$(name)-$(MEASURED))
	python3 -m analysis.sequential data/raw/campaign-$(MEASURED) --strict --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-sequential.csv
	python3 -m analysis.extras.core_split data/raw/campaign-$(MEASURED) --strict --output data/tables/campaign-$(MEASURED)/campaign-$(MEASURED)-core-split.csv
	python3 -m analysis.datacheck data/raw/tier-$(MEASURED) --output data/tables/tier-$(MEASURED)/tier-$(MEASURED)-quality.md
	python3 -m analysis.extras.variants data/raw/tier-$(MEASURED) --by engine-arm --strict --output data/tables/tier-$(MEASURED)/tier-$(MEASURED)-arms.csv
	python3 -m analysis.datacheck data/raw/grain-threads-$(MEASURED) --output data/tables/grain-threads-$(MEASURED)/grain-threads-$(MEASURED)-quality.md
	python3 -m analysis.extras.variants data/raw/grain-threads-$(MEASURED) --by grain --strict --output data/tables/grain-threads-$(MEASURED)/grain-threads-$(MEASURED)-grains.csv
	python3 -m analysis.extras.perf_loop data/raw/perf-loop1-$(MEASURED) data/raw/perf-loop8-$(MEASURED) --strict --output data/tables/perf-loop-$(MEASURED)/perf-loop-$(MEASURED)-counters.csv --rises data/tables/perf-loop-$(MEASURED)/perf-loop-$(MEASURED)-rises.csv

all-results: results extras-results cutoff-results grain-results perf-results v3-results ## Every table and figure of every campaign

tables-check: all-results ## Regenerate every table and fail if one differs from the committed one
	python3 scripts/tables_diff.py data/tables
