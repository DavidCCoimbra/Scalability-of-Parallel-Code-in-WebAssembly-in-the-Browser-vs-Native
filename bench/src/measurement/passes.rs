use std::num::NonZeroUsize;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Passes(NonZeroUsize);

impl Passes {
    pub const ONE: Self = Self(NonZeroUsize::MIN);

    pub fn new(count: usize) -> Option<Self> {
        NonZeroUsize::new(count).map(Self)
    }

    pub fn count(self) -> usize {
        self.0.get()
    }

    pub fn per_pass_ns(self, total_ns: u64) -> u64 {
        let passes = self.0.get() as u64;
        let remainder = total_ns % passes;
        let rounds_up = remainder >= passes - remainder;
        total_ns / passes + u64::from(rounds_up)
    }
}

impl Default for Passes {
    fn default() -> Self {
        Self::ONE
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_passes_do_not_exist() {
        assert_eq!(Passes::new(0), None);
        assert_eq!(Passes::new(1), Some(Passes::ONE));
        assert_eq!(Passes::default(), Passes::ONE);
    }

    #[test]
    fn one_pass_keeps_the_total() {
        for total in [0, 1, 7, u64::MAX] {
            assert_eq!(Passes::ONE.per_pass_ns(total), total);
        }
    }

    #[test]
    fn per_pass_time_rounds_to_the_nearest_ns() {
        let four = Passes::new(4).unwrap();
        assert_eq!(four.per_pass_ns(40), 10);
        assert_eq!(four.per_pass_ns(41), 10);
        assert_eq!(four.per_pass_ns(42), 11);
        assert_eq!(four.per_pass_ns(43), 11);
        let three = Passes::new(3).unwrap();
        assert_eq!(three.per_pass_ns(10), 3);
        assert_eq!(three.per_pass_ns(11), 4);
        assert_eq!(three.per_pass_ns(u64::MAX), u64::MAX / 3);
    }
}
