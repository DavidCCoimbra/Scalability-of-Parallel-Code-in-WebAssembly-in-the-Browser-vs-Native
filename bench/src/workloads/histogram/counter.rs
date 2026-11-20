use std::sync::atomic::AtomicU64;

/// Implementors differ only in memory layout: one counter per cache line, or eight per line.
pub trait Counter: Default + Send + Sync {
    fn atomic(&self) -> &AtomicU64;
    fn atomic_mut(&mut self) -> &mut AtomicU64;
}
