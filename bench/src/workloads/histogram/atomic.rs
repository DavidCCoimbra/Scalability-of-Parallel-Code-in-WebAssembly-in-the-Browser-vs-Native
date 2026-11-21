use rayon::prelude::*;

use super::{BYTES_PER_KB, CHUNK_BYTES, CounterTable, Histogram, PaddedCounter};
use crate::input::GrayImage;
use crate::workloads::{BufferAddresses, Checksum, Grain, Workload};

pub struct AtomicHistogram {
    image: GrayImage,
    counters: CounterTable<PaddedCounter>,
    histogram: Histogram,
    grain: Grain,
}

impl AtomicHistogram {
    pub fn new(image: GrayImage) -> Self {
        Self::with_grain(image, Grain::Adaptive)
    }

    pub fn with_grain(image: GrayImage, grain: Grain) -> Self {
        Self {
            image,
            counters: CounterTable::default(),
            histogram: Histogram::default(),
            grain,
        }
    }

    pub fn histogram(&self) -> &Histogram {
        &self.histogram
    }

    pub fn counter_stride(&self) -> usize {
        self.counters.stride()
    }
}

impl Workload for AtomicHistogram {
    fn prepare(&mut self) {
        self.counters.reset();
    }

    fn run(&mut self) {
        let counters = &self.counters;
        // The same task construction as the local histogram, so the two differ only in their
        // counters.
        let chunk_len = self.grain.chunk_len(CHUNK_BYTES, BYTES_PER_KB);
        self.grain
            .tasks(self.image.pixels().par_chunks(chunk_len))
            .for_each(|chunk| chunk.iter().for_each(|&value| counters.increment(value)));
        // Reading the counters back is part of the timed work, as the reduce is for the
        // local histogram.
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
    use crate::test_support::{prepare_and_run, sequential_histogram};
    use crate::workloads::histogram::Histogram;
    use crate::workloads::histogram::local::LocalHistogram;
    use crate::workloads::histogram::padded_counter::CACHE_LINE_BYTES;
    use crate::workloads::histogram::{MAX_TEST_THREADS, THREAD_TEST_SIDE};
    use crate::workloads::{Grain, Workload};

    fn run_with_threads(workload: &mut AtomicHistogram, threads: usize) -> Histogram {
        prepare_and_run(workload, threads);
        workload.histogram().clone()
    }

    #[test]
    fn neighbouring_counters_are_one_cache_line_apart() {
        let workload = AtomicHistogram::new(noise(8, 8, SEED));
        assert_eq!(workload.counter_stride(), CACHE_LINE_BYTES);
    }

    #[test]
    fn matches_sequential_histogram_on_both_inputs() {
        for image in [noise(600, 400, SEED), few_colors(600, 400, SEED, 4)] {
            let expected = sequential_histogram(&image);
            let mut workload = AtomicHistogram::new(image);
            workload.prepare();
            workload.run();
            assert_eq!(workload.histogram(), &expected);
        }
    }

    #[test]
    fn prepare_resets_the_counters_between_runs() {
        let mut workload = AtomicHistogram::new(noise(600, 400, SEED));
        workload.prepare();
        workload.run();
        let first = workload.checksum();
        workload.prepare();
        workload.run();
        assert_eq!(workload.checksum(), first);
    }

    #[test]
    fn checksum_matches_the_local_variant() {
        let image = few_colors(512, 512, SEED, 4);
        let mut local = LocalHistogram::new(image.clone());
        local.prepare();
        local.run();
        let mut atomic = AtomicHistogram::new(image);
        atomic.prepare();
        atomic.run();
        assert_eq!(atomic.checksum(), local.checksum());
    }

    #[test]
    fn every_fixed_grain_matches_the_sequential_histogram() {
        let image = few_colors(300, 200, SEED, 4);
        let expected = sequential_histogram(&image);
        for kb in [1, 3, 16, 64, 1000] {
            let mut workload = AtomicHistogram::with_grain(image.clone(), Grain::new(Some(kb)));
            for threads in [1, 3, 8] {
                assert_eq!(
                    run_with_threads(&mut workload, threads),
                    expected,
                    "kb = {kb}, threads = {threads}"
                );
            }
        }
    }

    #[test]
    fn matches_sequential_histogram_for_every_thread_count() {
        let image = few_colors(THREAD_TEST_SIDE, THREAD_TEST_SIDE, SEED, 4);
        let expected = sequential_histogram(&image);
        let mut workload = AtomicHistogram::new(image);
        for threads in 1..=MAX_TEST_THREADS {
            assert_eq!(
                run_with_threads(&mut workload, threads),
                expected,
                "threads = {threads}"
            );
        }
    }
}
