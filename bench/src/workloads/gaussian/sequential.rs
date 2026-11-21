use super::blur_interior;
use super::kernel::{CENTRE, KERNEL, KERNEL_SHIFT, RADIUS, ROUNDING, TAPS};
use crate::input::GrayImage;
use crate::workloads::{BufferAddresses, Checksum, Workload};

/// The filter without Rayon: every row blurred by the same `blur_interior`, from one plain loop
/// on the calling thread. The reference that the one-thread pool is compared with.
pub struct SequentialBlur {
    source: GrayImage,
    output: Vec<u8>,
}

impl SequentialBlur {
    pub fn new(source: GrayImage) -> Self {
        let output = vec![0; source.pixels().len()];
        Self { source, output }
    }

    pub fn output(&self) -> &[u8] {
        &self.output
    }

    fn output_rows(&self) -> impl Iterator<Item = &[u8]> {
        let width = self.source.width();
        self.output
            .chunks(self.source.pitch())
            .map(move |row| &row[..width])
    }
}

impl Workload for SequentialBlur {
    fn run(&mut self) {
        let source = &self.source;
        let (width, pitch) = (source.width(), source.pitch());
        self.output
            .chunks_mut(pitch)
            .enumerate()
            .for_each(|(y, row)| blur_row(source, y, &mut row[..width]));
    }

    fn checksum(&self) -> Checksum {
        Checksum::of_slices(self.output_rows())
    }

    fn buffers(&self) -> BufferAddresses {
        BufferAddresses::of_input_and_output(self.source.pixels(), &self.output)
    }
}

// The handling of a row and of its two edge pixels is a copy of the parallel filter's
// (`blur_row` there, `blur_clamped` and `clamped_neighbours` in the kernel), on purpose. Those
// functions have one caller and are inlined into the parallel filter's task; a second caller
// makes the compiler keep them as calls, which changes the machine code of the measured filter.
// The interior of the row, where the time goes, is the shared `blur_interior`, which is never
// inlined. A test keeps the copy's output equal to the parallel filter's.
fn blur_row(source: &GrayImage, y: usize, row: &mut [u8]) {
    let rows = neighbours(y, source.height()).map(|index| source.row(index));
    let last = row.len() - 1;
    row[0] = blur_edge(&rows, 0);
    if last == 0 {
        return;
    }
    row[last] = blur_edge(&rows, last);
    let [top, middle, bottom] = rows;
    blur_interior(top, middle, bottom, &mut row[RADIUS..last]);
}

fn blur_edge(rows: &[&[u8]; TAPS], x: usize) -> u8 {
    let columns = neighbours(x, rows[CENTRE].len());
    let sum: u16 = rows
        .iter()
        .zip(KERNEL)
        .map(|(line, weights)| {
            columns
                .iter()
                .zip(weights)
                .map(|(&column, weight)| weight * u16::from(line[column]))
                .sum::<u16>()
        })
        .sum();
    ((sum + ROUNDING) >> KERNEL_SHIFT) as u8
}

fn neighbours(index: usize, len: usize) -> [usize; TAPS] {
    [
        index.saturating_sub(RADIUS),
        index,
        (index + RADIUS).min(len - 1),
    ]
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{SEED, noise};
    use crate::workloads::gaussian::GaussianBlur;

    #[test]
    fn gives_the_output_of_the_parallel_filter() {
        for (width, height) in [(257, 131), (1, 5), (3, 1)] {
            let image = noise(width, height, SEED);
            let mut parallel = GaussianBlur::new(image.clone());
            parallel.run();
            let mut sequential = SequentialBlur::new(image);
            sequential.run();
            assert_eq!(sequential.output(), parallel.output(), "{width}x{height}");
            assert_eq!(sequential.checksum(), parallel.checksum());
        }
    }

    #[test]
    fn running_twice_gives_the_same_result() {
        let mut blur = SequentialBlur::new(noise(64, 48, SEED));
        blur.run();
        let first = blur.checksum();
        blur.run();
        assert_eq!(blur.checksum(), first);
    }
}
