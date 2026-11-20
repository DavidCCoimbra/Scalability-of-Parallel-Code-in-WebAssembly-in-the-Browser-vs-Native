mod memory_probe;
#[cfg(not(target_arch = "wasm32"))]
mod native;
#[cfg(not(target_arch = "wasm32"))]
mod resident_set;

pub use memory_probe::MemoryProbe;
#[cfg(not(target_arch = "wasm32"))]
pub use resident_set::ResidentSet;

/// Each host builds one and passes it to `run::execute`, so the shared code never asks which
/// environment it is in.
pub struct Platform<C, M, P> {
    pub clock: C,
    pub memory: M,
    pub pause: P,
}
