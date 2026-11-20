use std::fmt;

use super::{Clock, MeasurementPlan, Passes, PhaseHooks};
use crate::workloads::{Checksum, Workload};

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct IterationTimes {
    pub warmup_ns: Vec<u64>,
    pub measured_ns: Vec<u64>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Measurement {
    times: IterationTimes,
    checksum: Checksum,
}

impl Measurement {
    pub fn warmup_ns(&self) -> &[u64] {
        &self.times.warmup_ns
    }

    pub fn measured_ns(&self) -> &[u64] {
        &self.times.measured_ns
    }

    pub fn checksum(&self) -> Checksum {
        self.checksum
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MeasurementError {
    InconsistentChecksum {
        first: Checksum,
        iteration: usize,
        found: Checksum,
        times: IterationTimes,
    },
}

impl fmt::Display for MeasurementError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InconsistentChecksum {
                first,
                iteration,
                found,
                ..
            } => write!(
                f,
                "iteration {iteration} gave checksum {:#018x}, the first gave {:#018x}",
                found.0, first.0
            ),
        }
    }
}

impl std::error::Error for MeasurementError {}

pub fn measure<W, C>(
    workload: &mut W,
    clock: &C,
    plan: MeasurementPlan,
) -> Result<Measurement, MeasurementError>
where
    W: Workload + ?Sized,
    C: Clock,
{
    measure_with(workload, clock, plan, &mut ())
}

pub fn measure_with<W, C, H>(
    workload: &mut W,
    clock: &C,
    plan: MeasurementPlan,
    hooks: &mut H,
) -> Result<Measurement, MeasurementError>
where
    W: Workload + ?Sized,
    C: Clock,
    H: PhaseHooks,
{
    let mut times = IterationTimes {
        warmup_ns: Vec::with_capacity(plan.warmup),
        measured_ns: Vec::with_capacity(plan.measured),
    };
    let mut first = None;
    hooks.before_warmup();
    for iteration in 0..plan.warmup {
        let elapsed = timed_iteration(workload, clock, plan.passes);
        times.warmup_ns.push(elapsed);
        verify_checksum(workload, &mut first, iteration, &times)?;
    }
    hooks.before_measured();
    for iteration in plan.warmup..plan.warmup + plan.measured {
        let elapsed = timed_iteration(workload, clock, plan.passes);
        times.measured_ns.push(elapsed);
        verify_checksum(workload, &mut first, iteration, &times)?;
    }
    hooks.after_measured();
    Ok(Measurement {
        times,
        checksum: first.expect("at least one iteration"),
    })
}

fn verify_checksum<W>(
    workload: &W,
    first: &mut Option<Checksum>,
    iteration: usize,
    times: &IterationTimes,
) -> Result<(), MeasurementError>
where
    W: Workload + ?Sized,
{
    let checksum = workload.checksum();
    let expected = *first.get_or_insert(checksum);
    if checksum == expected {
        Ok(())
    } else {
        Err(MeasurementError::InconsistentChecksum {
            first: expected,
            iteration,
            found: checksum,
            times: times.clone(),
        })
    }
}

fn timed_iteration<W, C>(workload: &mut W, clock: &C, passes: Passes) -> u64
where
    W: Workload + ?Sized,
    C: Clock,
{
    workload.prepare();
    let start = clock.now_ns();
    for _ in 0..passes.count() {
        workload.run();
    }
    passes.per_pass_ns(clock.now_ns() - start)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{SEED, few_colors};
    use crate::workloads::histogram::atomic::AtomicHistogram;
    use std::cell::{Cell, RefCell};
    use std::rc::Rc;

    #[derive(Default)]
    struct FakeClock {
        ns: Cell<u64>,
    }

    impl FakeClock {
        fn advance(&self, ns: u64) {
            self.ns.set(self.ns.get() + ns);
        }
    }

    impl Clock for Rc<FakeClock> {
        fn now_ns(&self) -> u64 {
            self.ns.get()
        }
    }

    struct SpyWorkload {
        clock: Rc<FakeClock>,
        events: RefCell<Vec<&'static str>>,
        run_ns: u64,
        runs: u64,
        drift: bool,
    }

    impl SpyWorkload {
        fn new(clock: &Rc<FakeClock>, run_ns: u64) -> Self {
            Self {
                clock: Rc::clone(clock),
                events: RefCell::default(),
                run_ns,
                runs: 0,
                drift: false,
            }
        }
    }

    impl Workload for SpyWorkload {
        fn prepare(&mut self) {
            self.events.borrow_mut().push("prepare");
            self.clock.advance(1_000);
        }

        fn run(&mut self) {
            self.events.borrow_mut().push("run");
            self.clock.advance(self.run_ns);
            self.runs += 1;
        }

        fn checksum(&self) -> Checksum {
            self.events.borrow_mut().push("checksum");
            self.clock.advance(1_000);
            Checksum(if self.drift { self.runs } else { 42 })
        }
    }

    #[test]
    fn records_one_time_per_iteration_in_each_phase() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 7);
        let plan = MeasurementPlan::new(2, 3).unwrap();
        let measurement = measure(&mut workload, &clock, plan).unwrap();
        assert_eq!(measurement.warmup_ns(), [7, 7]);
        assert_eq!(measurement.measured_ns(), [7, 7, 7]);
    }

    #[test]
    fn only_run_is_inside_the_timed_region() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 5);
        let measurement =
            measure(&mut workload, &clock, MeasurementPlan::new(1, 1).unwrap()).unwrap();
        assert_eq!(measurement.measured_ns(), [5]);
    }

    #[test]
    fn prepare_runs_before_every_iteration_including_warmup() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 1);
        measure(&mut workload, &clock, MeasurementPlan::new(1, 2).unwrap()).unwrap();
        let events = workload.events.borrow();
        let runs: Vec<_> = events.iter().filter(|&&event| event == "run").collect();
        assert_eq!(runs.len(), 3);
        events
            .windows(2)
            .filter(|pair| pair[1] == "run")
            .for_each(|pair| assert_eq!(pair[0], "prepare"));
    }

    #[test]
    fn returns_the_checksum_of_the_iterations() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 1);
        let measurement =
            measure(&mut workload, &clock, MeasurementPlan::new(1, 2).unwrap()).unwrap();
        assert_eq!(measurement.checksum(), Checksum(42));
    }

    #[test]
    fn changing_checksum_between_iterations_is_an_error() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 1);
        workload.drift = true;
        let result = measure(&mut workload, &clock, MeasurementPlan::new(1, 2).unwrap());
        assert_eq!(
            result.unwrap_err(),
            MeasurementError::InconsistentChecksum {
                first: Checksum(1),
                iteration: 1,
                found: Checksum(2),
                times: IterationTimes {
                    warmup_ns: vec![1],
                    measured_ns: vec![1],
                },
            }
        );
    }

    #[test]
    fn passes_run_inside_the_timed_region_and_record_the_time_per_pass() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 7);
        let plan = MeasurementPlan::new(1, 2)
            .unwrap()
            .with_passes(Passes::new(3).unwrap());
        let measurement = measure(&mut workload, &clock, plan).unwrap();
        assert_eq!(measurement.warmup_ns(), [7]);
        assert_eq!(measurement.measured_ns(), [7, 7]);
        assert_eq!(workload.runs, 9);
    }

    #[test]
    fn prepare_runs_once_per_iteration_whatever_the_passes() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 1);
        let plan = MeasurementPlan::new(0, 2)
            .unwrap()
            .with_passes(Passes::new(4).unwrap());
        measure(&mut workload, &clock, plan).unwrap();
        let events = workload.events.borrow();
        let order: Vec<_> = events
            .iter()
            .copied()
            .filter(|&event| event != "checksum")
            .collect();
        assert_eq!(
            order,
            [
                "prepare", "run", "run", "run", "run", "prepare", "run", "run", "run", "run"
            ]
        );
    }

    #[derive(Default)]
    struct HookSpy {
        points: Vec<(&'static str, u64)>,
        clock: Rc<FakeClock>,
    }

    impl PhaseHooks for HookSpy {
        fn before_warmup(&mut self) {
            self.points.push(("before warm-up", self.clock.ns.get()));
        }

        fn before_measured(&mut self) {
            self.points.push(("before measured", self.clock.ns.get()));
        }

        fn after_measured(&mut self) {
            self.points.push(("after measured", self.clock.ns.get()));
        }
    }

    #[test]
    fn hooks_run_before_warmup_between_the_phases_and_after_the_last_iteration() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = SpyWorkload::new(&clock, 10);
        let mut hooks = HookSpy {
            clock: Rc::clone(&clock),
            ..HookSpy::default()
        };
        let plan = MeasurementPlan::new(1, 2).unwrap();
        measure_with(&mut workload, &clock, plan, &mut hooks).unwrap();
        // Each iteration advances the fake clock by prepare (1000) + run (10) + checksum (1000).
        assert_eq!(
            hooks.points,
            [
                ("before warm-up", 0),
                ("before measured", 2_010),
                ("after measured", 6_030)
            ]
        );
    }

    #[test]
    fn inconsistent_checksum_is_displayed_with_both_values() {
        let error = MeasurementError::InconsistentChecksum {
            first: Checksum(1),
            iteration: 3,
            found: Checksum(2),
            times: IterationTimes::default(),
        };
        assert_eq!(
            error.to_string(),
            "iteration 3 gave checksum 0x0000000000000002, the first gave 0x0000000000000001"
        );
    }

    #[test]
    fn atomic_histogram_gives_the_same_checksum_over_two_iterations() {
        let clock = Rc::new(FakeClock::default());
        let mut workload = AtomicHistogram::new(few_colors(256, 256, SEED, 4));
        let plan = MeasurementPlan::new(1, 2).unwrap();
        assert!(measure(&mut workload, &clock, plan).is_ok());
    }
}
