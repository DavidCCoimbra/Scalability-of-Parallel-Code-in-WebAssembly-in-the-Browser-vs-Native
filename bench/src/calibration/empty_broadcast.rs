use super::{ForkJoin, Probe};

pub struct EmptyBroadcast;

impl ForkJoin for EmptyBroadcast {
    fn probe(&self) -> Probe {
        Probe::Broadcast
    }

    fn fork_join(&self) {
        rayon::broadcast(|_| ());
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_broadcast_returns_after_every_worker_ran() {
        let pool = crate::test_support::pool(3);
        pool.install(|| EmptyBroadcast.fork_join());
    }
}
