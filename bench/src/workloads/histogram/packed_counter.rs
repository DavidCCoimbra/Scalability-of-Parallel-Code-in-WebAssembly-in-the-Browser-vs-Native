// Extra, not part of RQ1 or RQ2: the counter layout of the packed histogram.

use std::sync::atomic::AtomicU64;

use super::counter::Counter;

// The unpadded control: eight counters to a cache line, so threads counting different values
// can still collide (false sharing).
#[derive(Default)]
pub struct PackedCounter(AtomicU64);

impl Counter for PackedCounter {
    #[inline(always)]
    fn atomic(&self) -> &AtomicU64 {
        &self.0
    }

    fn atomic_mut(&mut self) -> &mut AtomicU64 {
        &mut self.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn counter_is_one_u64_wide() {
        assert_eq!(std::mem::size_of::<PackedCounter>(), size_of::<u64>());
    }
}
