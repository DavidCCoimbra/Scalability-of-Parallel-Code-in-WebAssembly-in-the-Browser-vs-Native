use std::sync::atomic::AtomicU64;

pub trait Counter: Default + Send + Sync {
    fn atomic(&self) -> &AtomicU64;
    fn atomic_mut(&mut self) -> &mut AtomicU64;
}
