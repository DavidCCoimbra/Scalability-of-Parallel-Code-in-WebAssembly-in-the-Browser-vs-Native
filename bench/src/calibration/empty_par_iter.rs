use std::hint::black_box;

use rayon::prelude::*;

use super::{ForkJoin, Probe};

pub struct EmptyParIter;

impl ForkJoin for EmptyParIter {
    fn probe(&self) -> Probe {
        Probe::ParIter
    }

    fn fork_join(&self) {
        // One item per pool thread, split adaptively as a workload's par_iter is; black_box keeps
        // the empty body from being optimized away, so what is left is the cost of entering,
        // splitting and joining an ordinary parallel region.
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
