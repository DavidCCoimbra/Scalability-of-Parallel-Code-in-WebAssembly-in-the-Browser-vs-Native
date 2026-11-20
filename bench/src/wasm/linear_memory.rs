use crate::platform::MemoryProbe;

// https://webassembly.github.io/spec/core/exec/runtime.html#page-size
const WASM_PAGE_BYTES: u64 = 64 * 1024;
const MEMORY_INDEX: u32 = 0;

/// Growing the shared memory during the measured iterations means an allocation inside the
/// timed region, so it fails the run.
pub struct LinearMemory;

impl MemoryProbe for LinearMemory {
    const GROWTH_FAILS_RUN: bool = true;

    fn bytes(&self) -> Option<u64> {
        let pages = core::arch::wasm32::memory_size::<MEMORY_INDEX>();
        Some(pages as u64 * WASM_PAGE_BYTES)
    }
}
