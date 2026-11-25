MYPY = uv run --no-project --with mypy --with matplotlib mypy --strict

.PHONY: test test-rust test-python lint

##@ Test and lint

test: test-rust test-python lint ## What CI runs, minus LaTeX

test-rust: #: Rust tests
	$(CARGO) test --locked --release

test-python: #: Harness, analysis and scripts tests
	python3 -m unittest discover -s scripts/tests -t .
	python3 -m unittest discover -s harness/tests -t .
	python3 -m unittest discover -s analysis/tests -t .

lint: ## fmt, clippy, ADRs, explainer data up to date, shellcheck, mypy strict
	$(CARGO) fmt --check
	$(CARGO) clippy --locked --release --all-targets -- -D warnings
	python3 scripts/check_adrs.py docs/adr
	python3 -m scripts.explainer_data --check
	shellcheck bench/build-wasm.sh harness/env/*.sh scripts/*.sh scripts/lib/*.sh
	$(MYPY) harness analysis scripts
