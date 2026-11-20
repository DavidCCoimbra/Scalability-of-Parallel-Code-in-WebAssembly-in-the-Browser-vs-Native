use rayon::prelude::*;

use super::{CHUNK_BYTES, Histogram};
use crate::input::GrayImage;
use crate::workloads::{BufferAddresses, Checksum, Grain, Workload};

const BYTES_PER_KB: usize = 1024;

pub struct LocalHistogram {
    image: GrayImage,
    histogram: Histogram,
    grain: Grain,
}

impl LocalHistogram {
    pub fn new(image: GrayImage) -> Self {
        Self::with_grain(image, Grain::Adaptive)
    }

    pub fn with_grain(image: GrayImage, grain: Grain) -> Self {
        Self {
            image,
            histogram: Histogram::default(),
            grain,
        }
    }

    pub fn histogram(&self) -> &Histogram {
        &self.histogram
    }
}

impl Workload for LocalHistogram {
    fn run(&mut self) {
        let chunk_len = self.grain.chunk_len(CHUNK_BYTES, BYTES_PER_KB);
        self.histogram = local_counts(self.grain.tasks(self.image.pixels().par_chunks(chunk_len)));
    }

    fn checksum(&self) -> Checksum {
        self.histogram.checksum()
    }

    fn buffers(&self) -> BufferAddresses {
        BufferAddresses::of_input(self.image.pixels())
    }
}

// Histogram::default runs once per split, so every split counts into its own histogram and
// reduce merges them pairwise: no shared counters, no atomics.
fn local_counts<'a>(chunks: impl IndexedParallelIterator<Item = &'a [u8]>) -> Histogram {
    chunks
        .fold(Histogram::default, |mut histogram, chunk| {
            chunk.iter().for_each(|&value| histogram.record(value));
            histogram
        })
        .reduce(Histogram::default, Histogram::merge)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{SEED, few_colors, noise};
    use crate::test_support::{prepare_and_run, sequential_histogram};
    use crate::workloads::histogram::{MAX_TEST_THREADS, THREAD_TEST_SIDE};
    use crate::workloads::{Grain, Workload};

    fn run_with_threads(workload: &mut LocalHistogram, threads: usize) -> Histogram {
        prepare_and_run(workload, threads);
        workload.histogram().clone()
    }

    #[test]
    fn matches_sequential_histogram_on_both_inputs() {
        for image in [noise(600, 400, SEED), few_colors(600, 400, SEED, 4)] {
            let expected = sequential_histogram(&image);
            let mut workload = LocalHistogram::new(image);
            workload.run();
            assert_eq!(workload.histogram(), &expected);
        }
    }

    #[test]
    fn counts_every_pixel_once() {
        let mut workload = LocalHistogram::new(noise(600, 400, SEED));
        workload.run();
        assert_eq!(workload.histogram().total(), 600 * 400);
    }

    #[test]
    fn running_twice_gives_the_same_result() {
        let mut workload = LocalHistogram::new(noise(600, 400, SEED));
        workload.run();
        let first = workload.checksum();
        workload.run();
        assert_eq!(workload.checksum(), first);
    }

    #[test]
    fn every_fixed_grain_matches_the_sequential_histogram() {
        let image = few_colors(300, 200, SEED, 4);
        let expected = sequential_histogram(&image);
        for kb in [1, 3, 16, 64, 1000] {
            let mut workload = LocalHistogram::with_grain(image.clone(), Grain::new(Some(kb)));
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
        let mut workload = LocalHistogram::new(image);
        for threads in 1..=MAX_TEST_THREADS {
            assert_eq!(
                run_with_threads(&mut workload, threads),
                expected,
                "threads = {threads}"
            );
        }
    }
}
