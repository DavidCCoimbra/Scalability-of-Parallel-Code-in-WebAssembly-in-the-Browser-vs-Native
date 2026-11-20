use super::{GrayImage, MAX_COLORS, Palette, SplitMix64};

pub fn noise(width: usize, height: usize, seed: u64) -> GrayImage {
    let mut rng = SplitMix64::new(seed);
    GrayImage::generate(width, height, || rng.next_u8())
}

pub fn few_colors(width: usize, height: usize, seed: u64, k: usize) -> GrayImage {
    few_colors_with(width, height, seed, k, Palette::Spread)
}

/// The same random draws for every palette: pixel n is palette value number
/// (n-th SplitMix64 output mod k), so only the values differ between palettes.
pub fn few_colors_with(
    width: usize,
    height: usize,
    seed: u64,
    k: usize,
    palette: Palette,
) -> GrayImage {
    assert!(
        (1..=MAX_COLORS).contains(&k),
        "k must be in 1..={MAX_COLORS}, got {k}"
    );
    let palette = palette.values(k);
    let mut rng = SplitMix64::new(seed);
    GrayImage::generate(width, height, || {
        palette[(rng.next_u64() % k as u64) as usize]
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::SEED;
    use crate::workloads::Checksum;
    use std::collections::HashSet;

    fn distinct(image: &GrayImage) -> usize {
        image.pixels().iter().collect::<HashSet<_>>().len()
    }

    // Independent reference: bench/tools/golden_inputs.py.
    const CONSECUTIVE_4_FINGERPRINT: u64 = 0x97cd_2683_77e5_e7d1;
    fn fingerprint(image: &GrayImage) -> u64 {
        Checksum::of_bytes(image.pixels()).0
    }

    #[test]
    fn images_match_golden_fingerprints() {
        assert_eq!(fingerprint(&noise(256, 256, SEED)), 0xff2f_1557_ec76_b9a8);
        assert_eq!(
            fingerprint(&few_colors(256, 256, SEED, 4)),
            0x0c34_c3ba_dfc1_bba5
        );
        assert_eq!(
            fingerprint(&few_colors_with(256, 256, SEED, 4, Palette::Consecutive)),
            CONSECUTIVE_4_FINGERPRINT
        );
    }

    #[test]
    fn image_has_width_times_height_pixels() {
        let image = noise(64, 32, SEED);
        assert_eq!((image.width(), image.height()), (64, 32));
        assert_eq!(image.pixels().len(), 64 * 32);
    }

    #[test]
    fn same_seed_gives_same_image() {
        assert_eq!(noise(64, 64, SEED), noise(64, 64, SEED));
        assert_eq!(few_colors(64, 64, SEED, 4), few_colors(64, 64, SEED, 4));
    }

    #[test]
    fn different_seed_gives_different_image() {
        assert_ne!(noise(64, 64, SEED), noise(64, 64, SEED + 1));
    }

    #[test]
    fn noise_covers_all_256_values() {
        assert_eq!(distinct(&noise(256, 256, SEED)), MAX_COLORS);
    }

    #[test]
    fn few_colors_uses_exactly_k_values() {
        for k in [1, 2, 3, 4, 16, 255, 256] {
            assert_eq!(distinct(&few_colors(256, 256, SEED, k)), k, "k = {k}");
        }
    }

    #[test]
    fn few_colors_values_are_evenly_spaced() {
        let image = few_colors(256, 256, SEED, 4);
        let values: HashSet<u8> = image.pixels().iter().copied().collect();
        assert_eq!(values, HashSet::from([0, 64, 128, 192]));
    }

    #[test]
    fn consecutive_values_are_the_first_k_and_follow_the_same_draws() {
        let spread = few_colors(256, 256, SEED, 16);
        let consecutive = few_colors_with(256, 256, SEED, 16, Palette::Consecutive);
        let values: HashSet<u8> = consecutive.pixels().iter().copied().collect();
        assert_eq!(values, (0..16).collect());
        assert!(
            spread
                .pixels()
                .iter()
                .zip(consecutive.pixels())
                .all(|(&wide, &narrow)| usize::from(wide) == usize::from(narrow) * MAX_COLORS / 16)
        );
    }

    #[test]
    fn few_colors_with_k_256_uses_every_value() {
        let image = few_colors(256, 256, SEED, 256);
        let values: HashSet<u8> = image.pixels().iter().copied().collect();
        assert_eq!(values, (0..=255).collect());
    }

    #[test]
    #[should_panic]
    fn few_colors_rejects_k_zero() {
        few_colors(8, 8, SEED, 0);
    }

    #[test]
    #[should_panic]
    fn few_colors_rejects_k_above_256() {
        few_colors(8, 8, SEED, 257);
    }
}
