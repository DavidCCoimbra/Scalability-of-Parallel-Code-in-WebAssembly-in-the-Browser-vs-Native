# Targets with "## " are listed by make help; "#: " marks internal or helper targets that it hides.
.DEFAULT_GOAL := help

SHELL := bash
P_MASK ?= 0,2,4,6,8,10,12,14
E_CPUS ?= 16-31
SPEC ?= harness/campaigns/smoke.json
NAME = $(shell python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' $(SPEC))
RAW = data/raw/$(NAME)
BUILD = $(shell python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("build", "baseline"))' $(SPEC))
CUTOFF_SIDES = 512 1024 2048 4096 8192
GRAIN_SIDES = 1024 8192
CARGO = source "$$HOME/.cargo/env" && cd bench && cargo

include make/setup.mk make/build.mk make/test.mk make/env.mk make/campaign.mk make/results.mk make/quick.mk

.PHONY: help
help: ## This list; the helper targets are in make/*.mk
	@awk 'BEGIN {FS = ":.*## "} /^##@ / {printf "\n%s\n", substr($$0, 5)} \
		/^[a-zA-Z0-9_-]+:.*## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
