use super::ProbeSamples;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CalibrationPlan {
    pub samples: usize,
    pub pause_ns: u64,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Calibration {
    pub pause_ns: u64,
    pub probes: Vec<ProbeSamples>,
}
