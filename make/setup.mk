WASM_BINDGEN_VERSION = $(shell sed -n 's/^wasm-bindgen = "=\(.*\)"$$/\1/p' bench/Cargo.toml)
SUDOERS = /etc/sudoers.d/ppc-bench

.PHONY: deps sudoers chrome-apparmor toolchain wasm-bindgen browsers setup

##@ Setup, once per machine

deps: #: sudo: C toolchain (linker), wabt and shellcheck from apt
	sudo apt-get update
	sudo apt-get install -y build-essential wabt shellcheck

sudoers: #: sudo: lets the harness start and stop the run scopes without a password
	echo "$$USER ALL=(root) NOPASSWD: /usr/bin/systemd-run, /usr/bin/systemctl" \
		| sudo tee $(SUDOERS).tmp >/dev/null
	sudo visudo -cf $(SUDOERS).tmp || { sudo rm -f $(SUDOERS).tmp; exit 1; }
	sudo chmod 0440 $(SUDOERS).tmp
	sudo mv $(SUDOERS).tmp $(SUDOERS)

chrome-apparmor: browsers #: sudo: lets the pinned Chrome use its sandbox (Ubuntu 23.10+ restricts user namespaces)
	printf 'abi <abi/4.0>,\ninclude <tunables/global>\nprofile ppc-chrome %s flags=(unconfined) {\n  userns,\n  include if exists <local/ppc-chrome>\n}\n' \
		"$(CURDIR)/harness/browsers/chrome-*/chrome-linux64/chrome" | sudo tee /etc/apparmor.d/ppc-chrome >/dev/null
	sudo apparmor_parser -r /etc/apparmor.d/ppc-chrome

toolchain: #: rustup and the pinned nightly from bench/rust-toolchain.toml
	command -v rustup >/dev/null || [ -x "$$HOME/.cargo/bin/rustup" ] || \
		curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain none --profile minimal
	source "$$HOME/.cargo/env" && cd bench && rustup install

wasm-bindgen: toolchain #: wasm-bindgen-cli, the version pinned in bench/Cargo.toml
	$(CARGO) install wasm-bindgen-cli --version $(WASM_BINDGEN_VERSION) --locked

browsers: #: The pinned Chrome for Testing and Firefox, checksums verified
	python3 harness/browsers.py

setup: toolchain wasm-bindgen browsers ## Toolchain, wasm-bindgen and browsers, no sudo (first: make deps sudoers chrome-apparmor)
