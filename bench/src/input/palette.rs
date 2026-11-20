use std::str::FromStr;

use super::MAX_COLORS;

/// Which k grey levels a few-colors image uses. `Spread` (i * 256 / k) puts the k values far
/// apart, so their counters sit on different cache lines even unpadded; `Consecutive`
/// (0..k) puts them next to each other, so up to eight unpadded 8-byte counters share one
/// 64-byte line and the packed histogram shows false sharing (k = 4 and 16).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Palette {
    #[default]
    Spread,
    /// Extra: no measured campaign uses it.
    Consecutive,
}

impl Palette {
    pub fn name(self) -> &'static str {
        match self {
            Self::Spread => "spread",
            Self::Consecutive => "consecutive",
        }
    }

    pub fn values(self, k: usize) -> Vec<u8> {
        (0..k)
            .map(|i| match self {
                Self::Spread => i * MAX_COLORS / k,
                Self::Consecutive => i,
            })
            .map(|value| u8::try_from(value).expect("k <= MAX_COLORS keeps every value a byte"))
            .collect()
    }
}

impl FromStr for Palette {
    type Err = String;

    fn from_str(name: &str) -> Result<Self, Self::Err> {
        [Self::Spread, Self::Consecutive]
            .into_iter()
            .find(|palette| palette.name() == name)
            .ok_or_else(|| name.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn spread_values_are_evenly_spaced_and_consecutive_ones_start_at_zero() {
        assert_eq!(Palette::Spread.values(4), [0, 64, 128, 192]);
        assert_eq!(Palette::Consecutive.values(4), [0, 1, 2, 3]);
        assert_eq!(
            Palette::Spread.values(MAX_COLORS),
            Palette::Consecutive.values(MAX_COLORS)
        );
    }

    #[test]
    fn names_round_trip() {
        for palette in [Palette::Spread, Palette::Consecutive] {
            assert_eq!(palette.name().parse(), Ok(palette));
        }
        assert!("rainbow".parse::<Palette>().is_err());
    }
}
