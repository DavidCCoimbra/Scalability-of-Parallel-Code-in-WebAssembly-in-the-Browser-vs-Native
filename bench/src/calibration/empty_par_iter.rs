use std::hint::black_box;

use rayon::prelude::*;

use super::{ForkJoin, Probe};

pub struct EmptyParIter;

impl ForkJoin for EmptyParIter {
    fn probe(&self) -> Probe {
        Probe::ParIter
    }

    fn fork_join(&self) {
        (0..rayon::current_num_threads())
            .into_par_iter()
            .for_each(|item| {
                black_box(item);
            });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_par_iter_returns_inside_and_outside_a_pool() {
        EmptyParIter.fork_join();
        let pool = crate::test_support::pool(3);
        pool.install(|| EmptyParIter.fork_join());
    }
}
