// The 3x3 binomial kernel, the usual integer approximation of a Gaussian:
// https://en.wikipedia.org/wiki/Gaussian_blur
pub(super) const KERNEL: [[u16; 3]; 3] = [[1, 2, 1], [2, 4, 2], [1, 2, 1]];
pub(super) const TAPS: usize = KERNEL.len();
pub(super) const RADIUS: usize = TAPS / 2;
pub(super) const LEFT: usize = 0;
pub(super) const CENTRE: usize = RADIUS;
pub(super) const RIGHT: usize = TAPS - 1;
const KERNEL_SHIFT: u32 = 4;
const ROUNDING: u16 = 1 << (KERNEL_SHIFT - 1);

const fn kernel_sum() -> u16 {
    let mut sum = 0;
    let mut row = 0;
    while row < TAPS {
        sum += KERNEL[row][LEFT] + KERNEL[row][CENTRE] + KERNEL[row][RIGHT];
        row += 1;
    }
    sum
}

// The weights sum to 16, so the division is `>> 4`, and the largest sum (16 * 255 + 8) fits
// in a u16, which gives eight SIMD lanes per 128-bit register.
const _: () = assert!(kernel_sum() == 1 << KERNEL_SHIFT);
const _: () = assert!(kernel_sum() as u32 * u8::MAX as u32 + ROUNDING as u32 <= u16::MAX as u32);

pub(super) fn blur_clamped(rows: &[&[u8]; TAPS], x: usize) -> u8 {
    let columns = clamped_neighbours(x, rows[CENTRE].len());
    let sum = rows
        .iter()
        .zip(KERNEL)
        .map(|(line, weights)| weighted_sum(&columns.map(|column| line[column]), weights))
        .sum();
    normalize(sum)
}

fn weighted_sum(window: &[u8], weights: [u16; TAPS]) -> u16 {
    window
        .iter()
        .zip(weights)
        .map(|(&value, weight)| weight * u16::from(value))
        .sum()
}

// Adding half the divisor before the flooring shift rounds sum / 16 to the nearest.
pub(super) fn normalize(sum: u16) -> u8 {
    ((sum + ROUNDING) >> KERNEL_SHIFT) as u8
}

pub(super) fn clamped_neighbours(index: usize, len: usize) -> [usize; TAPS] {
    [
        index.saturating_sub(RADIUS),
        index,
        (index + RADIUS).min(len - 1),
    ]
}
