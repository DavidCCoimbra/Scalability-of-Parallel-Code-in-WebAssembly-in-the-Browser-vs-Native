.PHONY: env-setup env-check env-restore quiet quiet-off

##@ Machine state, until the next reboot

env-setup: ## sudo: SMT off, turbo off, performance governor, perf counters readable, shield on, then check
	harness/env/setup.sh $(P_MASK) $(E_CPUS)

env-check: ## Fails unless the machine is prepared; saves data/sysinfo
	harness/env/check.sh $(P_MASK)

quiet: #: Close desktop apps, stop the indexer, updates and docker (until reboot or quiet-off)
	harness/env/quiet.sh on

quiet-off: #: Start again what quiet stopped
	harness/env/quiet.sh off

env-restore: ## sudo: shield off, SMT on, turbo on, powersave, perf counters restricted
	harness/env/restore.sh $(P_MASK) $(E_CPUS)
