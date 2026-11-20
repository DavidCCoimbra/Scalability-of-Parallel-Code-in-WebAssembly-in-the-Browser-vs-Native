// Steele, Lea and Flood, "Fast Splittable Pseudorandom Number Generators",
// OOPSLA 2014, https://doi.org/10.1145/2714064.2660195; constants as in
// https://prng.di.unimi.it/splitmix64.c
const GOLDEN_GAMMA: u64 = 0x9E37_79B9_7F4A_7C15;
const MIX_SHIFT_1: u32 = 30;
const MIX_MULTIPLIER_1: u64 = 0xBF58_476D_1CE4_E5B9;
const MIX_SHIFT_2: u32 = 27;
const MIX_MULTIPLIER_2: u64 = 0x94D0_49BB_1331_11EB;
const FINAL_SHIFT: u32 = 31;
const TOP_BYTE_SHIFT: u32 = u64::BITS - u8::BITS;

pub struct SplitMix64 {
    state: u64,
}

impl SplitMix64 {
    pub fn new(seed: u64) -> Self {
        Self { state: seed }
    }

    pub fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_add(GOLDEN_GAMMA);
        let mut z = self.state;
        z = (z ^ (z >> MIX_SHIFT_1)).wrapping_mul(MIX_MULTIPLIER_1);
        z = (z ^ (z >> MIX_SHIFT_2)).wrapping_mul(MIX_MULTIPLIER_2);
        z ^ (z >> FINAL_SHIFT)
    }

    pub(super) fn next_u8(&mut self) -> u8 {
        (self.next_u64() >> TOP_BYTE_SHIFT) as u8
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn top_byte_shift_keeps_the_most_significant_byte() {
        assert_eq!(TOP_BYTE_SHIFT, 56);
    }

    #[test]
    fn splitmix64_matches_reference_values() {
        let mut rng = SplitMix64::new(1234567);
        let expected = [
            6457827717110365317,
            3203168211198807973,
            9817491932198370423,
            4593380528125082431,
            16408922859458223821,
        ];
        for value in expected {
            assert_eq!(rng.next_u64(), value);
        }
    }
}
