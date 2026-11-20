MYPY = uv run --no-project --with mypy --with matplotlib mypy --strict

.PHONY: test test-rust test-python lint

##@ Test and lint

test: test-rust test-python lint ## What CI runs, minus LaTeX

test-rust: #: Rust tests, default and pad64
	$(CARGO) test --release
	$(CARGO) test --release --features pad64

test-python: #: Harness, analysis and scripts tests
	python3 -m unittest discover -s scripts/tests -t .
	python3 -m unittest discover -s harness/tests -t .
	python3 -m unittest discover -s analysis/tests -t .

lint: ## fmt, clippy, ADRs, shellcheck, mypy strict
	$(CARGO) fmt --check
	$(CARGO) clippy --release --all-targets -- -D warnings
	python3 scripts/check_adrs.py docs/adr
	shellcheck bench/build-wasm.sh harness/env/*.sh scripts/*.sh
	$(MYPY) harness analysis scripts
