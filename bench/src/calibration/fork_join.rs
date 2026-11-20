use super::Probe;

pub trait ForkJoin {
    fn probe(&self) -> Probe;
    fn fork_join(&self);
}
