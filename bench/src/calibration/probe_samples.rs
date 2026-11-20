use super::Probe;

/// Warm samples run back to back; cold ones after a pause.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProbeSamples {
    pub probe: Probe,
    pub warm_ns: Vec<u64>,
    pub cold_ns: Vec<u64>,
}
