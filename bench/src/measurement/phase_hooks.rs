/// Called between the phases of `measure_with`, outside every timed region.
pub trait PhaseHooks {
    fn before_warmup(&mut self) {}
    fn before_measured(&mut self) {}
    fn after_measured(&mut self) {}
}

impl PhaseHooks for () {}
