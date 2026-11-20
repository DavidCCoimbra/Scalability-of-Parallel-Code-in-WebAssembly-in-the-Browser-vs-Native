/// The fork-join regions the calibration times. `Broadcast` wakes every pool worker
/// and waits for all of them, the cost the paper reports; `ParIter` is an ordinary
/// optional-parallelism region, an empty `par_iter` over one item per thread, which Rayon may
/// split and steal like a workload's loop.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Probe {
    Broadcast,
    ParIter,
}

impl Probe {
    pub fn name(self) -> &'static str {
        match self {
            Self::Broadcast => "broadcast",
            Self::ParIter => "par-iter",
        }
    }
}
