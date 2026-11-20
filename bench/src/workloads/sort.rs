use rayon::prelude::*;

use crate::input::GrayImage;
use crate::workloads::{Checksum, Workload};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SortKind {
    Stable,
    Unstable,
}

pub struct ParallelSort {
    keys: Vec<u32>,
    sorted: Vec<u32>,
    kind: SortKind,
}

fn keys_of(image: &GrayImage) -> Vec<u32> {
    image
        .pixels()
        .as_chunks::<{ size_of::<u32>() }>()
        .0
        .iter()
        .map(|bytes| u32::from_le_bytes(*bytes))
        .collect()
}

impl ParallelSort {
    pub fn new(image: GrayImage, kind: SortKind) -> Self {
        let keys = keys_of(&image);
        let sorted = keys.clone();
        Self { keys, sorted, kind }
    }

    pub fn sorted(&self) -> &[u32] {
        &self.sorted
    }
}

impl Workload for ParallelSort {
    fn prepare(&mut self) {
        self.sorted.copy_from_slice(&self.keys);
    }

    fn run(&mut self) {
        match self.kind {
            SortKind::Stable => self.sorted.par_sort(),
            SortKind::Unstable => self.sorted.par_sort_unstable(),
        }
    }

    fn checksum(&self) -> Checksum {
        Checksum::of_words(self.sorted.iter().map(|key| key.to_le_bytes()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{SEED, noise};

    fn sorted_with_threads(image: &GrayImage, kind: SortKind, threads: usize) -> Vec<u32> {
        let mut workload = ParallelSort::new(image.clone(), kind);
        workload.prepare();
        crate::test_support::pool(threads).install(|| workload.run());
        workload.sorted().to_vec()
    }

    #[test]
    fn keys_are_the_pixels_read_four_at_a_time() {
        let image = GrayImage::from_pixels(4, 2, vec![1, 0, 0, 0, 0, 1, 0, 0]);
        assert_eq!(keys_of(&image), vec![1, 256]);
    }

    #[test]
    fn sorts_like_the_standard_library_at_every_thread_count() {
        let image = noise(512, 512, SEED);
        let mut expected = keys_of(&image);
        expected.sort();
        for kind in [SortKind::Stable, SortKind::Unstable] {
            for threads in [1, 2, 3, 8] {
                assert_eq!(
                    sorted_with_threads(&image, kind, threads),
                    expected,
                    "{kind:?} {threads} threads"
                );
            }
        }
    }

    #[test]
    fn prepare_restores_the_unsorted_keys() {
        let image = noise(64, 64, SEED);
        let mut workload = ParallelSort::new(image.clone(), SortKind::Stable);
        workload.prepare();
        workload.run();
        workload.prepare();
        assert_eq!(workload.sorted(), keys_of(&image).as_slice());
    }
}
