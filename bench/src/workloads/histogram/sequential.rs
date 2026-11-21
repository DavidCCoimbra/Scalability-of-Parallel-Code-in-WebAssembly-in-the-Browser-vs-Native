use super::Histogram;
use crate::input::GrayImage;
use crate::workloads::{BufferAddresses, Checksum, Workload};

/// The histogram without Rayon and without atomics: one plain table counted in one loop on the
/// calling thread, as one task of the local histogram counts its chunk.
pub struct SequentialHistogram {
    image: GrayImage,
    histogram: Histogram,
}

impl SequentialHistogram {
    pub fn new(image: GrayImage) -> Self {
        Self {
            image,
            histogram: Histogram::default(),
        }
    }

    pub fn histogram(&self) -> &Histogram {
        &self.histogram
    }
}

impl Workload for SequentialHistogram {
    fn run(&mut self) {
        let mut histogram = Histogram::default();
        self.image
            .pixels()
            .iter()
            .for_each(|&value| histogram.record(value));
        self.histogram = histogram;
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

    #[test]
    fn gives_the_histogram_of_the_local_variant() {
        for image in [noise(600, 400, SEED), few_colors(600, 400, SEED, 4)] {
            let mut local = LocalHistogram::new(image.clone());
            local.run();
            let mut sequential = SequentialHistogram::new(image);
            sequential.run();
            assert_eq!(sequential.histogram(), local.histogram());
            assert_eq!(sequential.checksum(), local.checksum());
        }
    }

    #[test]
    fn counts_every_pixel_once_and_starts_again_on_each_run() {
        let mut workload = SequentialHistogram::new(noise(600, 400, SEED));
        workload.run();
        workload.run();
        assert_eq!(workload.histogram().total(), 600 * 400);
    }
}
