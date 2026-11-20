NO_VECTORIZE = "-C", "llvm-args=-vectorize-loops=false", "-C", "llvm-args=-vectorize-slp=false"

.PHONY: build build-native build-wasm build-native-avx2 build-native-scalar build-wasm-scalar \
	build-baseline build-avx2 build-scalar

##@ Build

build: build-native build-wasm ## Native runner and WASM package

build-native: #: Native runner, x86-64 baseline
	$(CARGO) build --release --bin native

build-wasm: #: WASM with threads and simd128, into bench/www/pkg
	source "$$HOME/.cargo/env" && bench/build-wasm.sh

build-native-avx2: #: SIMD extra: native runner with target-cpu=native (AVX2), into bench/target/avx2
	$(CARGO) build --release --bin native --target-dir target/avx2 --config 'build.rustflags=["-C", "target-cpu=native"]'

build-native-scalar: #: SIMD extra: native runner without auto-vectorization, into bench/target/scalar
	$(CARGO) build --release --bin native --target-dir target/scalar --config 'build.rustflags=[$(NO_VECTORIZE)]'

build-wasm-scalar: #: SIMD extra: WASM without simd128, into bench/www/pkg (rebuild with build-wasm after)
	source "$$HOME/.cargo/env" && bench/build-wasm.sh --config 'target.wasm32-unknown-unknown.rustflags=["-C", "target-feature=-simd128"]'

# The build variant of a spec (its "build" key) names one of these; make campaign builds it first.
build-baseline: build
build-avx2: build-native-avx2
build-scalar: build-native-scalar build-wasm-scalar
