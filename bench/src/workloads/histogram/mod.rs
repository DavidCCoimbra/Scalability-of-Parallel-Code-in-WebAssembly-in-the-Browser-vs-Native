pub mod atomic;
mod counter;
mod counter_table;
pub mod extras;
pub mod local;
pub mod padded_counter;

pub use counter::Counter;
pub use counter_table::CounterTable;
pub use extras::packed_counter::PackedCounter;
pub use padded_counter::PaddedCounter;

use super::Checksum;

pub const BINS: usize = 256;
pub const CHUNK_BYTES: usize = 64 * 1024;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Histogram {
    counts: [u64; BINS],
}

impl Default for Histogram {
    fn default() -> Self {
        Self { counts: [0; BINS] }
    }
}

impl Histogram {
    pub fn from_counts(counts: [u64; BINS]) -> Self {
        Self { counts }
    }

    pub fn record(&mut self, value: u8) {
        self.counts[usize::from(value)] += 1;
    }

    pub fn merge(mut self, other: Self) -> Self {
        self.counts
            .iter_mut()
            .zip(other.counts)
            .for_each(|(count, more)| *count += more);
        self
    }

    pub fn count(&self, value: u8) -> u64 {
        self.counts[usize::from(value)]
    }

    pub fn total(&self) -> u64 {
        self.counts.iter().sum()
    }

    pub fn checksum(&self) -> Checksum {
        Checksum::of_words(self.counts.iter().map(|count| count.to_le_bytes()))
    }
}

#[cfg(test)]
pub(crate) const THREAD_TEST_SIDE: usize = 1024;
#[cfg(test)]
pub(crate) const MAX_TEST_THREADS: usize = 8;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::workloads::Checksum;

    #[test]
    fn thread_count_test_images_have_more_chunks_than_threads() {
        let chunks = THREAD_TEST_SIDE * THREAD_TEST_SIDE / CHUNK_BYTES;
        assert!(
            chunks >= 2 * MAX_TEST_THREADS,
            "{chunks} chunks for {MAX_TEST_THREADS} threads"
        );
    }

    #[test]
    fn empty_histogram_has_zero_counts() {
        assert_eq!(Histogram::default().total(), 0);
    }

    #[test]
    fn record_counts_each_value() {
        let mut histogram = Histogram::default();
        for value in [0, 7, 7, 255] {
            histogram.record(value);
        }
        assert_eq!(histogram.count(7), 2);
        assert_eq!(histogram.count(255), 1);
        assert_eq!(histogram.total(), 4);
    }

    #[test]
    fn merge_adds_counts() {
        let mut left = Histogram::default();
        left.record(3);
        let mut right = Histogram::default();
        right.record(3);
        right.record(9);
        let merged = left.merge(right);
        assert_eq!((merged.count(3), merged.count(9)), (2, 1));
    }

    #[test]
    fn checksum_detects_counts_moved_between_bins() {
        let mut original = [0; BINS];
        original[10] = 1;
        original[20] = 1;
        let mut moved = [0; BINS];
        moved[11] = 1;
        moved[19] = 1;
        assert_ne!(
            Histogram::from_counts(original).checksum(),
            Histogram::from_counts(moved).checksum()
        );
    }

    #[test]
    fn checksum_is_fnv1a_of_the_little_endian_counts() {
        let mut histogram = Histogram::default();
        histogram.record(1);
        let mut bytes = vec![0u8; BINS * 8];
        bytes[8] = 1;
        assert_eq!(histogram.checksum(), Checksum::of_bytes(&bytes));
    }

    #[test]
    fn from_counts_round_trips() {
        let mut counts = [0; BINS];
        counts[42] = 5;
        assert_eq!(Histogram::from_counts(counts).count(42), 5);
    }
}
