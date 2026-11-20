mod kernel;

use rayon::prelude::*;

use super::{BufferAddresses, Checksum, Grain, Workload};
use crate::input::GrayImage;
use kernel::{CENTRE, KERNEL, LEFT, RADIUS, RIGHT, blur_clamped, clamped_neighbours, normalize};

const ROWS_PER_ADAPTIVE_CHUNK: usize = 1;

pub struct GaussianBlur {
    source: GrayImage,
    output: Vec<u8>,
    grain: Grain,
}

impl GaussianBlur {
    pub fn new(source: GrayImage) -> Self {
        Self::with_grain(source, Grain::Adaptive)
    }

    pub fn with_grain(source: GrayImage, grain: Grain) -> Self {
        let output = vec![0; source.pixels().len()];
        Self {
            source,
            output,
            grain,
        }
    }

    pub fn output(&self) -> &[u8] {
        &self.output
    }

    pub fn output_rows(&self) -> impl Iterator<Item = &[u8]> {
        let width = self.source.width();
        self.output
            .chunks(self.source.pitch())
            .map(move |row| &row[..width])
    }
}

impl Workload for GaussianBlur {
    fn run(&mut self) {
        let source = &self.source;
        let (width, pitch) = (source.width(), source.pitch());
        let rows = self.grain.chunk_len(ROWS_PER_ADAPTIVE_CHUNK, 1);
        self.grain
            .tasks(self.output.par_chunks_mut(pitch * rows))
            .enumerate()
            .for_each(|(chunk, pixels)| {
                let first = chunk * rows;
                pixels
                    .chunks_mut(pitch)
                    .enumerate()
                    .for_each(|(offset, row)| blur_row(source, first + offset, &mut row[..width]));
            });
    }

    // Padding excluded, so the checksum does not depend on the pitch.
    fn checksum(&self) -> Checksum {
        Checksum::of_slices(self.output_rows())
    }

    fn buffers(&self) -> BufferAddresses {
        BufferAddresses::of_input_and_output(self.source.pixels(), &self.output)
    }
}

fn blur_row(source: &GrayImage, y: usize, row: &mut [u8]) {
    let rows = clamped_neighbours(y, source.height()).map(|index| source.row(index));
    let last = row.len() - 1;
    row[0] = blur_clamped(&rows, 0);
    if last == 0 {
        return;
    }
    row[last] = blur_clamped(&rows, last);
    let [top, middle, bottom] = rows;
    blur_interior(top, middle, bottom, &mut row[RADIUS..last]);
}

// Kept as a named symbol so scripts/check_simd.py can find it and check it is vectorized.
#[inline(never)]
pub fn blur_interior(top: &[u8], middle: &[u8], bottom: &[u8], out: &mut [u8]) {
    let n = out.len();
    // out[i] is pixel i + 1, so t0[i], t1[i] and t2[i] are its left, centre and right neighbours
    // in the top row. Nine slices of length n let the compiler drop the bounds checks and
    // vectorize.
    let (t0, t1, t2) = (
        &top[LEFT..n + LEFT],
        &top[CENTRE..n + CENTRE],
        &top[RIGHT..n + RIGHT],
    );
    let (m0, m1, m2) = (
        &middle[LEFT..n + LEFT],
        &middle[CENTRE..n + CENTRE],
        &middle[RIGHT..n + RIGHT],
    );
    let (b0, b1, b2) = (
        &bottom[LEFT..n + LEFT],
        &bottom[CENTRE..n + CENTRE],
        &bottom[RIGHT..n + RIGHT],
    );
    let [[k00, k01, k02], [k10, k11, k12], [k20, k21, k22]] = KERNEL;
    for i in 0..n {
        let sum = k00 * u16::from(t0[i])
            + k01 * u16::from(t1[i])
            + k02 * u16::from(t2[i])
            + k10 * u16::from(m0[i])
            + k11 * u16::from(m1[i])
            + k12 * u16::from(m2[i])
            + k20 * u16::from(b0[i])
            + k21 * u16::from(b1[i])
            + k22 * u16::from(b2[i]);
        out[i] = normalize(sum);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{GrayImage, SEED, noise};
    use crate::workloads::{Checksum, Grain, Workload};

    // Literal weights, shift and rounding, so the reference shares no code with the blur.
    fn reference_blur(image: &GrayImage) -> Vec<u8> {
        let (width, height) = (image.width() as isize, image.height() as isize);
        let at = |x: isize, y: isize| {
            let x = x.clamp(0, width - 1) as usize;
            let y = y.clamp(0, height - 1) as usize;
            u32::from(image.pixels()[y * image.width() + x])
        };
        let mut out = Vec::with_capacity(image.pixels().len());
        for y in 0..height {
            for x in 0..width {
                let sum = at(x - 1, y - 1)
                    + 2 * at(x, y - 1)
                    + at(x + 1, y - 1)
                    + 2 * at(x - 1, y)
                    + 4 * at(x, y)
                    + 2 * at(x + 1, y)
                    + at(x - 1, y + 1)
                    + 2 * at(x, y + 1)
                    + at(x + 1, y + 1);
                out.push(((sum + 8) >> 4) as u8);
            }
        }
        out
    }

    fn run_with_threads(blur: &mut GaussianBlur, threads: usize) -> Checksum {
        crate::test_support::pool(threads).install(|| blur.run());
        blur.checksum()
    }

    #[test]
    fn constant_image_stays_constant() {
        let mut blur = GaussianBlur::new(GrayImage::from_pixels(5, 4, vec![77; 20]));
        blur.run();
        assert!(blur.output().iter().all(|&value| value == 77));
    }

    #[test]
    fn single_bright_pixel_spreads_with_kernel_weights() {
        let mut pixels = vec![0; 9];
        pixels[4] = 160;
        let mut blur = GaussianBlur::new(GrayImage::from_pixels(3, 3, pixels));
        blur.run();
        assert_eq!(blur.output(), [10, 20, 10, 20, 40, 20, 10, 20, 10]);
    }

    #[test]
    fn single_pixel_image_is_unchanged() {
        let mut blur = GaussianBlur::new(GrayImage::from_pixels(1, 1, vec![201]));
        blur.run();
        assert_eq!(blur.output(), [201]);
    }

    #[test]
    fn parallel_output_matches_sequential_reference() {
        let image = noise(257, 131, SEED);
        let expected = reference_blur(&image);
        let mut blur = GaussianBlur::new(image);
        blur.run();
        assert_eq!(blur.output(), expected.as_slice());
    }

    #[test]
    fn narrow_images_match_sequential_reference() {
        for width in 1..=3 {
            let image = noise(width, 5, SEED);
            let expected = reference_blur(&image);
            let mut blur = GaussianBlur::new(image);
            blur.run();
            assert_eq!(blur.output(), expected.as_slice(), "width = {width}");
        }
    }

    #[test]
    fn checksum_fingerprints_the_output() {
        let image = noise(64, 48, SEED);
        let expected = Checksum::of_bytes(&reference_blur(&image));
        let mut blur = GaussianBlur::new(image);
        blur.run();
        assert_eq!(blur.checksum(), expected);
    }

    #[test]
    fn every_fixed_grain_matches_the_sequential_reference() {
        let image = noise(67, 41, SEED);
        let expected = reference_blur(&image);
        for rows in [1, 2, 3, 7, 41, 100] {
            let mut blur = GaussianBlur::with_grain(image.clone(), Grain::new(Some(rows)));
            for threads in [1, 3, 8] {
                run_with_threads(&mut blur, threads);
                assert_eq!(
                    blur.output(),
                    expected.as_slice(),
                    "rows = {rows}, threads = {threads}"
                );
            }
        }
    }

    #[test]
    fn a_padded_image_gives_the_unpadded_rows_and_checksum() {
        let image = noise(67, 41, SEED);
        let mut plain = GaussianBlur::new(image.clone());
        plain.run();
        for pitch in [67, 68, 128, 4096] {
            for grain in [Grain::Adaptive, Grain::new(Some(3))] {
                let mut padded = GaussianBlur::with_grain(image.clone().with_pitch(pitch), grain);
                run_with_threads(&mut padded, 3);
                assert!(
                    padded.output_rows().eq(plain.output().chunks(67)),
                    "pitch = {pitch}"
                );
                assert_eq!(padded.checksum(), plain.checksum(), "pitch = {pitch}");
            }
        }
    }

    #[test]
    fn checksum_is_independent_of_thread_count() {
        let mut blur = GaussianBlur::new(noise(257, 131, SEED));
        let single = run_with_threads(&mut blur, 1);
        for threads in 2..=8 {
            assert_eq!(
                run_with_threads(&mut blur, threads),
                single,
                "threads = {threads}"
            );
        }
    }
}
