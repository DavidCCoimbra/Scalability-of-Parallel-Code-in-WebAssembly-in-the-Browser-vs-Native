use super::RunError;
use crate::measurement::PhaseHooks;
use crate::platform::MemoryProbe;
use crate::results::MemorySizes;

pub(super) struct MemoryTracker<'a, M> {
    probe: &'a M,
    before_warmup: Option<u64>,
    before_measured: Option<u64>,
    after_measured: Option<u64>,
}

impl<'a, M: MemoryProbe> MemoryTracker<'a, M> {
    pub(super) fn new(probe: &'a M) -> Self {
        Self {
            probe,
            before_warmup: None,
            before_measured: None,
            after_measured: None,
        }
    }

    pub(super) fn sizes(&self) -> MemorySizes {
        MemorySizes {
            before_warmup: self.before_warmup,
            before_measured: self.before_measured,
            after_measured: self.after_measured,
        }
    }

    /// Growth between the first and the last measured iteration means an allocation inside the
    /// measured phase. Warm-up may grow memory (first-touch allocations are what it is for),
    /// so the check starts at the end of the warm-up.
    pub(super) fn check(&self) -> Result<(), RunError> {
        match (self.before_measured, self.after_measured) {
            (Some(before), Some(after)) if M::GROWTH_FAILS_RUN && after > before => {
                Err(RunError::MemoryGrew { before, after })
            }
            _ => Ok(()),
        }
    }
}

impl<M: MemoryProbe> PhaseHooks for MemoryTracker<'_, M> {
    fn before_warmup(&mut self) {
        self.before_warmup = self.probe.bytes();
    }

    fn before_measured(&mut self) {
        self.before_measured = self.probe.bytes();
    }

    fn after_measured(&mut self) {
        self.after_measured = self.probe.bytes();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;

    struct Growing<const FAILS: bool> {
        bytes: Cell<u64>,
    }

    impl<const FAILS: bool> MemoryProbe for Growing<FAILS> {
        const GROWTH_FAILS_RUN: bool = FAILS;

        fn bytes(&self) -> Option<u64> {
            let bytes = self.bytes.get();
            self.bytes.set(bytes + 100);
            Some(bytes)
        }
    }

    fn tracked<const FAILS: bool>() -> (MemorySizes, Result<(), RunError>) {
        let probe = Growing::<FAILS> {
            bytes: Cell::new(1_000),
        };
        let mut tracker = MemoryTracker::new(&probe);
        tracker.before_warmup();
        tracker.before_measured();
        tracker.after_measured();
        (tracker.sizes(), tracker.check())
    }

    #[test]
    fn records_the_size_before_warmup_between_the_phases_and_after_the_last_iteration() {
        let (sizes, _) = tracked::<false>();
        assert_eq!(
            sizes,
            MemorySizes {
                before_warmup: Some(1_000),
                before_measured: Some(1_100),
                after_measured: Some(1_200),
            }
        );
    }

    #[test]
    fn growth_during_the_measured_phase_fails_only_where_the_probe_says_so() {
        assert_eq!(tracked::<false>().1, Ok(()));
        assert_eq!(
            tracked::<true>().1,
            Err(RunError::MemoryGrew {
                before: 1_100,
                after: 1_200
            })
        );
    }
}
