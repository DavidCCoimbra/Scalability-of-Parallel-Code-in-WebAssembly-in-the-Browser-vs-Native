INHIBIT = $(if $(shell command -v systemd-inhibit),systemd-inhibit --what=sleep:idle --who=ppc-bench --why="campaign $(NAME)",)

.PHONY: smoke mini campaign status collect analysis cutoff-campaigns grain-campaigns

##@ Measure (SPEC=harness/campaigns/<name>.json; resumes if stopped)

smoke: ## The smoke campaign
	$(MAKE) campaign SPEC=harness/campaigns/smoke.json

mini: #: The mini campaign
	$(MAKE) campaign SPEC=harness/campaigns/mini.json

# A campaign runs in quiet mode, and quiet mode ends when it ends, also on failure or
# Ctrl-C: the EXIT trap is set before quiet mode starts, and INT/TERM exit through it. QUIET=0 runs it without; the sequence targets below turn it on once.
QUIET ?= 1
QUIET_AROUND = $(if $(filter 0,$(QUIET)),,trap 'harness/env/quiet.sh off' EXIT && trap 'exit 130' INT TERM && harness/env/quiet.sh on &&)

campaign: build-$(BUILD) ## Run SPEC into data/raw/<name> in quiet mode (QUIET=0 without), built as its build variant
	$(QUIET_AROUND) $(INHIBIT) python3 -m harness.campaign $(SPEC)

# One randomized campaign per size, one after the other. A campaign with failed runs does
# not stop the next ones; the target fails at the end if any did.
cutoff-campaigns: ## The five cutoff campaigns in sequence, make status after each
	$(QUIET_AROUND) failed=0; for side in $(CUTOFF_SIDES) control-512 control-2048; do \
	  $(MAKE) campaign QUIET=0 SPEC=harness/campaigns/cutoff-$$side-v2.json || failed=1; \
	  $(MAKE) status SPEC=harness/campaigns/cutoff-$$side-v2.json; \
	done; exit $$failed

grain-campaigns: ## The two grain sweep campaigns in sequence, make status after each
	$(QUIET_AROUND) failed=0; for side in $(GRAIN_SIDES); do \
	  $(MAKE) campaign QUIET=0 SPEC=harness/campaigns/grain-$$side-v2.json || failed=1; \
	  $(MAKE) status SPEC=harness/campaigns/grain-$$side-v2.json; \
	done; exit $$failed

status: ## Progress of SPEC, running or finished: counts, problems, elapsed, ETA (read-only)
	python3 -m harness.campaign.status $(SPEC)

collect: #: One table of every run of SPEC
	python3 -m harness.collect $(RAW) --output data/$(NAME).csv

analysis: #: Speedup, efficiency and the plan's contrasts for SPEC
	python3 -m analysis.v0 $(RAW) --output data/$(NAME)-scaling.csv
	python3 -m analysis.results $(RAW) --max-threads 8 --contrasts data/$(NAME)-contrasts.csv --shape data/$(NAME)-shape.csv
