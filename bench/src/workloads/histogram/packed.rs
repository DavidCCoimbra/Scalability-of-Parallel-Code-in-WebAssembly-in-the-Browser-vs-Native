// Extra, not part of RQ1 or RQ2: the shared atomic table without padding, eight counters to a
// cache line, to measure what false sharing adds to the padded atomic histogram.

use rayon::prelude::*;

use super::{CHUNK_BYTES, CounterTable, Histogram, PackedCounter};
use crate::input::GrayImage;
use crate::workloads::{BufferAddresses, Checksum, Workload};

pub struct PackedAtomicHistogram {
    image: GrayImage,
    counters: CounterTable<PackedCounter>,
    histogram: Histogram,
}

impl PackedAtomicHistogram {
    pub fn new(image: GrayImage) -> Self {
        Self {
            image,
            counters: CounterTable::default(),
            histogram: Histogram::default(),
        }
    }

    pub fn histogram(&self) -> &Histogram {
        &self.histogram
    }

    pub fn counter_stride(&self) -> usize {
        self.counters.stride()
    }
}

impl Workload for PackedAtomicHistogram {
    fn prepare(&mut self) {
        self.counters.reset();
    }

    fn run(&mut self) {
        let counters = &self.counters;
        self.image
            .pixels()
            .par_chunks(CHUNK_BYTES)
            .for_each(|chunk| chunk.iter().for_each(|&value| counters.increment(value)));
        self.histogram = self.counters.read();
    }

    fn checksum(&self) -> Checksum {
        self.histogram.checksum()
    }

    fn buffers(&self) -> BufferAddresses {
        BufferAddresses::of_input(self.image.pixels())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{SEED, few_colors, noise};
    use crate::workloads::histogram::local::LocalHistogram;
    use crate::workloads::histogram::{MAX_TEST_THREADS, THREAD_TEST_SIDE};

    #[test]
    fn neighbouring_counters_share_cache_lines() {
        let workload = PackedAtomicHistogram::new(noise(8, 8, SEED));
        assert_eq!(workload.counter_stride(), size_of::<u64>());
    }

    #[test]
    fn matches_the_local_variant_at_every_thread_count() {
        let image = few_colors(THREAD_TEST_SIDE, THREAD_TEST_SIDE, SEED, 16);
        let mut local = LocalHistogram::new(image.clone());
        local.prepare();
        local.run();
        for threads in 1..=MAX_TEST_THREADS {
            let mut workload = PackedAtomicHistogram::new(image.clone());
            workload.prepare();
            crate::test_support::pool(threads).install(|| workload.run());
            assert_eq!(workload.histogram(), local.histogram(), "{threads} threads");
        }
    }

    #[test]
    fn prepare_resets_the_counters_between_runs() {
        let mut workload = PackedAtomicHistogram::new(noise(600, 400, SEED));
        workload.prepare();
        workload.run();
        let first = workload.checksum();
        workload.prepare();
        workload.run();
        assert_eq!(workload.checksum(), first);
    }
}
