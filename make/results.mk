.PHONY: results extras-results cutoff-results grain-results perf-results all-results tables-check

##@ Tables and figures of the paper

results: ## Every table and figure of the campaign from data/raw/campaign-v2
	mkdir -p paper/figures
	python3 -m analysis.datacheck data/raw/campaign-v2 --output data/tables/campaign-v2/campaign-v2-quality.md
	python3 -m harness.collect data/raw/campaign-v2 --output data/campaign-v2.csv
	python3 -m analysis.v0 data/raw/campaign-v2 --output data/tables/campaign-v2/campaign-v2-scaling.csv
	python3 -m analysis.results data/raw/campaign-v2 --max-threads 8 --strict --foreign-cpu-threshold 0.25 --contrasts data/tables/campaign-v2/campaign-v2-contrasts.csv --shape data/tables/campaign-v2/campaign-v2-shape.csv
	python3 -m analysis.robustness data/raw/campaign-v2 --max-threads 8 --strict --foreign-cpu-threshold 0.25 --output data/tables/campaign-v2/campaign-v2-robustness.csv
	python3 -m analysis.karp_flatt data/tables/campaign-v2/campaign-v2-scaling.csv --output data/tables/campaign-v2/campaign-v2-karp-flatt.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/campaign-v2 --output paper/figures --prefix campaign
	uv run --no-project --with matplotlib python -m analysis.distributions data/raw/campaign-v2 --figure paper/figures/campaign-distributions.pdf --table data/tables/campaign-v2/campaign-v2-distributions.csv

extras-results: ## Tables and figures of the exploratory campaigns: extras, weak scaling, SIMD, hybrid P+E
	python3 -m analysis.datacheck data/raw/extras-v2 --output data/tables/extras-v2/extras-v2-quality.md
	python3 -m harness.collect data/raw/extras-v2 --output data/extras-v2.csv
	python3 -m analysis.v0 data/raw/extras-v2 --output data/tables/extras-v2/extras-v2-scaling.csv
	python3 -m analysis.results data/raw/extras-v2 --max-threads 8 --strict --foreign-cpu-threshold 0.25 --partial --contrasts data/tables/extras-v2/extras-v2-contrasts.csv --shape data/tables/extras-v2/extras-v2-shape.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/extras-v2 --output paper/figures --prefix extras
	python3 -m analysis.datacheck data/raw/weak-v2 --output data/tables/weak-v2/weak-v2-quality.md
	python3 -m analysis.v0 data/raw/weak-v2 --weak --output data/tables/weak-v2/weak-v2-scaling.csv
	python3 -m analysis.iteration_drift data/raw/weak-v2 --output data/tables/weak-v2/weak-v2-iteration-drift.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/weak-v2 --output paper/figures --prefix weak
	rm -f paper/figures/weak-speedup.pdf paper/figures/weak-efficiency.pdf
	for c in simd-scalar simd-avx2; do \
	  python3 -m analysis.datacheck data/raw/$$c-v2 --output data/tables/simd-v2/$$c-v2-quality.md && \
	  python3 -m analysis.v0 data/raw/$$c-v2 --output data/tables/simd-v2/$$c-v2-scaling.csv && \
	  python3 -m analysis.iteration_drift data/raw/$$c-v2 --output data/tables/simd-v2/$$c-v2-iteration-drift.csv || exit 1; \
	done
	python3 -m analysis.datacheck data/raw/hybrid-v2 --output data/tables/hybrid-v2/hybrid-v2-quality.md
	python3 -m analysis.v0 data/raw/hybrid-v2 --output data/tables/hybrid-v2/hybrid-v2-scaling.csv
	python3 -m analysis.iteration_drift data/raw/hybrid-v2 --output data/tables/hybrid-v2/hybrid-v2-iteration-drift.csv
	uv run --no-project --with matplotlib python -m analysis.figures data/raw/hybrid-v2 --output paper/figures --prefix hybrid --diagonal "speedup = N"
	rm -f paper/figures/hybrid-efficiency.pdf
	uv run --no-project --with matplotlib python -m analysis.extras.build_variants baseline=data/raw/campaign-v2 scalar=data/raw/simd-scalar-v2 avx2=data/raw/simd-avx2-v2 --table data/tables/simd-v2/simd-v2-variants.csv --figure paper/figures/simd-efficiency.pdf

cutoff-results: ## Cutoff campaigns: data check and v0 per size, then the cutoff table, estimates, model and figure
	for side in $(CUTOFF_SIDES) control-512 control-2048; do \
	  python3 -m analysis.datacheck data/raw/cutoff-$$side-v2 --output data/tables/cutoff-v2/cutoff-$$side-v2-quality.md && \
	  python3 -m analysis.v0 data/raw/cutoff-$$side-v2 --output data/tables/cutoff-v2/cutoff-$$side-v2-scaling.csv || exit 1; \
	done
	uv run --no-project --with matplotlib python -m analysis.cutoff $(foreach side,$(CUTOFF_SIDES),data/raw/cutoff-$(side)-v2) \
		--table data/tables/cutoff-v2/cutoff-table.csv --estimates data/tables/cutoff-v2/cutoff-estimates.csv --model data/tables/cutoff-v2/cutoff-model.csv \
		--figure paper/figures/cutoff-speedup.pdf

grain-results: ## Grain sweep campaigns: data check per size, then the U-curve points, best grains and figure
	mkdir -p data/tables/grain-v2
	for side in $(GRAIN_SIDES); do \
	  python3 -m analysis.datacheck data/raw/grain-$$side-v2 --output data/tables/grain-v2/grain-$$side-v2-quality.md || exit 1; \
	done
	uv run --no-project --with matplotlib python -m analysis.grain $(foreach side,$(GRAIN_SIDES),data/raw/grain-$(side)-v2) \
		--points data/tables/grain-v2/grain-points.csv --best data/tables/grain-v2/grain-best.csv --figure paper/figures/grain-ucurve.pdf \
		--paper-figure paper/figures/grain-ucurve-8192.pdf

perf-results: ## Hardware counters per atomic add and V8's retries from data/raw/perf-v2
	python3 -m analysis.datacheck data/raw/perf-v2 --output data/tables/perf-v2/perf-v2-quality.md
	python3 -m analysis.extras.perf_counters data/raw/perf-v2 --runs data/tables/perf-v2/perf-v2-runs.csv \
		--summary data/tables/perf-v2/perf-v2-counters.csv --retries data/tables/perf-v2/perf-v2-retries.csv

all-results: results extras-results cutoff-results grain-results perf-results ## Every table and figure of every campaign

tables-check: all-results ## Regenerate every table and fail if one differs from the committed one
	python3 scripts/tables_diff.py data/tables
