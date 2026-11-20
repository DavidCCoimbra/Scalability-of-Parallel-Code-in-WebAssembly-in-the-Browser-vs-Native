use std::time::Duration;

pub trait Pause {
    fn pause_ns(&self, ns: u64);
}

pub struct ThreadSleep;

impl Pause for ThreadSleep {
    fn pause_ns(&self, ns: u64) {
        std::thread::sleep(Duration::from_nanos(ns));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn thread_sleep_pauses_for_at_least_the_requested_time() {
        let start = std::time::Instant::now();
        ThreadSleep.pause_ns(2_000_000);
        assert!(start.elapsed() >= std::time::Duration::from_millis(2));
    }
}
