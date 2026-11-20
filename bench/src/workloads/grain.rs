use std::num::NonZeroUsize;

use rayon::iter::{IndexedParallelIterator, MaxLen};

/// `Fixed(n)` makes every task exactly n units (the filter's rows, the local histogram's KB)
/// and stops Rayon from merging them, a sequential cutoff.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Grain {
    #[default]
    Adaptive,
    Fixed(NonZeroUsize),
}

impl Grain {
    pub fn new(units: Option<usize>) -> Self {
        units
            .and_then(NonZeroUsize::new)
            .map_or(Self::Adaptive, Self::Fixed)
    }

    pub fn is_adaptive(self) -> bool {
        self == Self::Adaptive
    }

    pub fn units(self) -> Option<usize> {
        match self {
            Self::Adaptive => None,
            Self::Fixed(units) => Some(units.get()),
        }
    }

    pub fn chunk_len(self, adaptive_len: usize, unit_len: usize) -> usize {
        match self {
            Self::Adaptive => adaptive_len,
            Self::Fixed(units) => units.get() * unit_len,
        }
    }

    /// Fixed: with_max_len(1) makes every chunk its own task. Adaptive: usize::MAX is Rayon's
    /// own default maximum, so the split stays Rayon's.
    pub fn tasks<I: IndexedParallelIterator>(self, chunks: I) -> MaxLen<I> {
        chunks.with_max_len(self.max_chunks_per_task())
    }

    fn max_chunks_per_task(self) -> usize {
        match self {
            Self::Adaptive => usize::MAX,
            Self::Fixed(_) => 1,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_units_means_adaptive() {
        assert_eq!(Grain::new(None), Grain::Adaptive);
        assert!(Grain::default().is_adaptive());
    }

    #[test]
    fn chunk_length_is_the_workload_default_or_the_units() {
        assert_eq!(Grain::Adaptive.chunk_len(64, 1024), 64);
        assert_eq!(Grain::new(Some(3)).chunk_len(64, 1024), 3 * 1024);
    }

    #[test]
    fn a_fixed_grain_gives_one_task_per_chunk() {
        use rayon::prelude::*;
        let pool = crate::test_support::pool(4);
        let tasks_of = |grain: Grain| {
            pool.install(|| {
                grain
                    .tasks((0..64).into_par_iter())
                    .fold(|| (), |(), _| ())
                    .map(|()| 1)
                    .sum::<usize>()
            })
        };
        assert_eq!(tasks_of(Grain::new(Some(1))), 64);
        assert!(tasks_of(Grain::Adaptive) < 64);
    }

    #[test]
    fn units_make_a_fixed_grain() {
        assert_eq!(
            Grain::new(Some(4)),
            Grain::Fixed(NonZeroUsize::new(4).unwrap())
        );
    }
}
