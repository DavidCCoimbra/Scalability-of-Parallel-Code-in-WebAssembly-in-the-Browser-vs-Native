pub trait Clock {
    fn now_ns(&self) -> u64;
}

#[cfg(not(target_arch = "wasm32"))]
pub struct NativeClock {
    origin: std::time::Instant,
}

#[cfg(not(target_arch = "wasm32"))]
impl Default for NativeClock {
    fn default() -> Self {
        Self {
            origin: std::time::Instant::now(),
        }
    }
}

#[cfg(not(target_arch = "wasm32"))]
impl Clock for NativeClock {
    fn now_ns(&self) -> u64 {
        u64::try_from(self.origin.elapsed().as_nanos()).expect("clock overflow")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[cfg(not(target_arch = "wasm32"))]
    #[test]
    fn native_clock_is_monotonic() {
        let clock = NativeClock::default();
        let first = clock.now_ns();
        assert!(clock.now_ns() >= first);
    }
}
