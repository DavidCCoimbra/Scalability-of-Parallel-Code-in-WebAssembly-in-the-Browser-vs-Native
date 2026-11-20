use super::{Platform, ResidentSet};
use crate::calibration::ThreadSleep;
use crate::measurement::NativeClock;

impl Platform<NativeClock, ResidentSet, ThreadSleep> {
    pub fn native() -> Self {
        Self {
            clock: NativeClock::default(),
            memory: ResidentSet,
            pause: ThreadSleep,
        }
    }
}
