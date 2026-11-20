pub trait MemoryProbe {
    const GROWTH_FAILS_RUN: bool;

    fn bytes(&self) -> Option<u64>;
}
