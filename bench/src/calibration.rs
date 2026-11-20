mod empty_broadcast;
mod empty_par_iter;
mod fork_join;
mod pause;
mod plan;
mod probe;
mod probe_samples;

pub use empty_broadcast::EmptyBroadcast;
pub use empty_par_iter::EmptyParIter;
pub use fork_join::ForkJoin;
pub use pause::{Pause, ThreadSleep};
pub use plan::{Calibration, CalibrationPlan};
pub use probe::Probe;
pub use probe_samples::ProbeSamples;

use std::hint::black_box;

use crate::measurement::Clock;
use crate::workloads::Workload;

pub const MIN_PAUSE_NS: u64 = 1_000_000;

/// The time of one `checksum` call: the single-threaded gap after each measured iteration in
/// which the pool workers go idle.
pub fn pause_for<W, C>(workload: &mut W, clock: &C) -> u64
where
    W: Workload + ?Sized,
    C: Clock,
{
    workload.prepare();
    let start = clock.now_ns();
    black_box(workload.checksum());
    (clock.now_ns() - start).max(MIN_PAUSE_NS)
}

/// Every probe of the run, in this order: the broadcast first, so its samples start from the
/// same pool state as before the second probe existed.
pub fn calibrate_probes<C, P>(clock: &C, pause: &P, plan: CalibrationPlan) -> Calibration
where
    C: Clock,
    P: Pause,
{
    Calibration {
        pause_ns: plan.pause_ns,
        probes: vec![
            calibrate(clock, &EmptyBroadcast, pause, plan),
            calibrate(clock, &EmptyParIter, pause, plan),
        ],
    }
}

pub fn calibrate<C, F, P>(
    clock: &C,
    fork_join: &F,
    pause: &P,
    plan: CalibrationPlan,
) -> ProbeSamples
where
    C: Clock,
    F: ForkJoin,
    P: Pause,
{
    // After one untimed call, warm samples run back to back while the workers still spin;
    // each cold sample first sleeps so the workers park, as before a measured iteration.
    let timed = || {
        let start = clock.now_ns();
        fork_join.fork_join();
        clock.now_ns() - start
    };
    fork_join.fork_join();
    let warm_ns = (0..plan.samples).map(|_| timed()).collect();
    let cold_ns = (0..plan.samples)
        .map(|_| {
            pause.pause_ns(plan.pause_ns);
            timed()
        })
        .collect();
    ProbeSamples {
        probe: fork_join.probe(),
        warm_ns,
        cold_ns,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::workloads::{Checksum, Workload};
    use std::cell::{Cell, RefCell};
    use std::rc::Rc;

    #[derive(Default)]
    struct Timeline {
        ns: Cell<u64>,
        events: RefCell<Vec<&'static str>>,
    }

    impl Timeline {
        fn advance(&self, ns: u64, event: &'static str) {
            self.ns.set(self.ns.get() + ns);
            self.events.borrow_mut().push(event);
        }
    }

    impl Clock for Rc<Timeline> {
        fn now_ns(&self) -> u64 {
            self.ns.get()
        }
    }

    struct FakeForkJoin(Rc<Timeline>);

    impl ForkJoin for FakeForkJoin {
        fn probe(&self) -> Probe {
            Probe::ParIter
        }

        fn fork_join(&self) {
            self.0.advance(10, "fork-join");
        }
    }

    struct FakePause(Rc<Timeline>);

    impl Pause for FakePause {
        fn pause_ns(&self, ns: u64) {
            self.0.advance(ns, "pause");
        }
    }

    struct SlowChecksum(Rc<Timeline>);

    impl Workload for SlowChecksum {
        fn prepare(&mut self) {
            self.0.advance(5, "prepare");
        }

        fn run(&mut self) {}

        fn checksum(&self) -> Checksum {
            self.0.advance(3_000_000, "checksum");
            Checksum(1)
        }
    }

    #[test]
    fn warm_samples_are_back_to_back_and_cold_ones_follow_a_pause() {
        let timeline = Rc::new(Timeline::default());
        let plan = CalibrationPlan {
            samples: 2,
            pause_ns: 500,
        };
        let samples = calibrate(
            &timeline,
            &FakeForkJoin(Rc::clone(&timeline)),
            &FakePause(Rc::clone(&timeline)),
            plan,
        );
        assert_eq!(
            samples,
            ProbeSamples {
                probe: Probe::ParIter,
                warm_ns: vec![10, 10],
                cold_ns: vec![10, 10],
            }
        );
        assert_eq!(
            *timeline.events.borrow(),
            [
                "fork-join",
                "fork-join",
                "fork-join",
                "pause",
                "fork-join",
                "pause",
                "fork-join"
            ]
        );
    }

    #[test]
    fn every_probe_is_calibrated_broadcast_first() {
        let pool = crate::test_support::pool(2);
        let plan = CalibrationPlan {
            samples: 3,
            pause_ns: 0,
        };
        let calibration = pool.install(|| {
            calibrate_probes(
                &crate::measurement::NativeClock::default(),
                &ThreadSleep,
                plan,
            )
        });
        let probes: Vec<_> = calibration
            .probes
            .iter()
            .map(|samples| (samples.probe, samples.warm_ns.len(), samples.cold_ns.len()))
            .collect();
        assert_eq!(probes, [(Probe::Broadcast, 3, 3), (Probe::ParIter, 3, 3)]);
    }

    #[test]
    fn probe_names() {
        assert_eq!(Probe::Broadcast.name(), "broadcast");
        assert_eq!(Probe::ParIter.name(), "par-iter");
    }

    #[test]
    fn pause_is_at_least_the_checksum_time() {
        let timeline = Rc::new(Timeline::default());
        let mut workload = SlowChecksum(Rc::clone(&timeline));
        assert_eq!(pause_for(&mut workload, &timeline), 3_000_000);
    }

    struct FastChecksum;

    impl Workload for FastChecksum {
        fn run(&mut self) {}

        fn checksum(&self) -> Checksum {
            Checksum(0)
        }
    }

    #[test]
    fn pause_never_drops_below_the_floor() {
        let timeline = Rc::new(Timeline::default());
        assert_eq!(pause_for(&mut FastChecksum, &timeline), MIN_PAUSE_NS);
    }
}
