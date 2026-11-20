use std::sync::atomic::AtomicU64;

use super::counter::Counter;

// 128 bytes because Intel's adjacent-line prefetcher fetches 64-byte lines in
// pairs, so two counters 64 bytes apart can still interfere; crossbeam's
// CachePadded uses 128 on x86-64 for the same reason:
// https://docs.rs/crossbeam-utils/latest/crossbeam_utils/struct.CachePadded.html
// repr(align) needs a literal, so CACHE_LINE_BYTES repeats it.
#[cfg(not(feature = "pad64"))]
pub const CACHE_LINE_BYTES: usize = 128;
#[cfg(feature = "pad64")]
pub const CACHE_LINE_BYTES: usize = 64;

#[derive(Default)]
#[cfg_attr(not(feature = "pad64"), repr(align(128)))]
#[cfg_attr(feature = "pad64", repr(align(64)))]
pub struct PaddedCounter(AtomicU64);

impl Counter for PaddedCounter {
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
    fn counter_occupies_its_own_cache_line() {
        assert_eq!(std::mem::align_of::<PaddedCounter>(), CACHE_LINE_BYTES);
        assert_eq!(std::mem::size_of::<PaddedCounter>(), CACHE_LINE_BYTES);
    }
}
