// Extra, not part of RQ1 or RQ2: the same padded atomics with one table per thread, so nothing
// contends. Local, private and shared atomics at the same k separate the cost of the atomic
// instruction from the cost of contention.

use rayon::prelude::*;

use crate::input::GrayImage;
use crate::workloads::histogram::{CHUNK_BYTES, CounterTable, Histogram, PaddedCounter};
use crate::workloads::{BufferAddresses, Checksum, Workload};

const OUTSIDE_POOL_TABLES: usize = 1;

pub struct PrivateAtomicHistogram {
    image: GrayImage,
    tables: Vec<CounterTable<PaddedCounter>>,
    histogram: Histogram,
}

impl PrivateAtomicHistogram {
    pub fn new(image: GrayImage) -> Self {
        Self {
            image,
            tables: Vec::new(),
            histogram: Histogram::default(),
        }
    }

    pub fn histogram(&self) -> &Histogram {
        &self.histogram
    }
}

impl Workload for PrivateAtomicHistogram {
    fn prepare(&mut self) {
        // The counters are atomic only because run() reaches the tables through a shared
        // reference; with one writer per table nothing contends. Exactly N + 1 tables, so the
        // timed merge does not read tables an earlier, larger pool left behind.
        let tables = rayon::current_num_threads() + OUTSIDE_POOL_TABLES;
        self.tables.resize_with(tables, CounterTable::default);
        self.tables.iter_mut().for_each(CounterTable::reset);
    }

    fn run(&mut self) {
        debug_assert_eq!(
            self.tables.len(),
            rayon::current_num_threads() + OUTSIDE_POOL_TABLES,
            "run must use the pool that prepare sized the tables for"
        );
        let tables = &self.tables;
        self.image
            .pixels()
            .par_chunks(CHUNK_BYTES)
            .for_each(|chunk| {
                let own = &tables
                    [rayon::current_thread_index().unwrap_or(tables.len() - OUTSIDE_POOL_TABLES)];
                chunk.iter().for_each(|&value| own.increment(value));
            });
        self.histogram = self
            .tables
            .iter()
            .map(CounterTable::read)
            .fold(Histogram::default(), Histogram::merge);
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
    use crate::workloads::histogram::{MAX_TEST_THREADS, THREAD_TEST_SIDE};

    fn run_with_threads(workload: &mut PrivateAtomicHistogram, threads: usize) -> Histogram {
        prepare_and_run(workload, threads);
        workload.histogram().clone()
    }

    #[test]
    fn matches_the_local_variant_at_every_thread_count() {
        for image in [
            noise(THREAD_TEST_SIDE, THREAD_TEST_SIDE, SEED),
            few_colors(THREAD_TEST_SIDE, THREAD_TEST_SIDE, SEED, 4),
        ] {
            let expected = sequential_histogram(&image);
            for threads in 1..=MAX_TEST_THREADS {
                let mut workload = PrivateAtomicHistogram::new(image.clone());
                assert_eq!(
                    run_with_threads(&mut workload, threads),
                    expected,
                    "{threads} threads"
                );
            }
        }
    }

    #[test]
    fn one_table_per_thread_of_the_pool_and_one_for_callers_outside_it() {
        let mut workload = PrivateAtomicHistogram::new(noise(64, 64, SEED));
        run_with_threads(&mut workload, 3);
        assert_eq!(workload.tables.len(), 4);
    }

    #[test]
    fn a_caller_outside_the_pool_uses_its_own_table() {
        let image = noise(64, 64, SEED);
        let mut workload = PrivateAtomicHistogram::new(image.clone());
        workload.prepare();
        workload.run();
        assert_eq!(workload.histogram(), &sequential_histogram(&image));
    }

    #[test]
    fn prepare_resets_every_table_between_runs() {
        let image = noise(600, 400, SEED);
        let mut workload = PrivateAtomicHistogram::new(image.clone());
        run_with_threads(&mut workload, 4);
        assert_eq!(
            run_with_threads(&mut workload, 4),
            sequential_histogram(&image)
        );
    }
}
