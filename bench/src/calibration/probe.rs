/// `Broadcast` is the cost the paper reports; `ParIter` is split and stolen like a workload's
/// loop.
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
