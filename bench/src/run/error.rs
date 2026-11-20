use std::fmt;

use crate::measurement::MeasurementError;
use crate::pool::PoolError;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RunError {
    Pool(PoolError),
    Measurement(MeasurementError),
    MemoryGrew { before: u64, after: u64 },
}

impl From<PoolError> for RunError {
    fn from(error: PoolError) -> Self {
        Self::Pool(error)
    }
}

impl From<MeasurementError> for RunError {
    fn from(error: MeasurementError) -> Self {
        Self::Measurement(error)
    }
}

impl fmt::Display for RunError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Pool(error) => write!(f, "{error}"),
            Self::Measurement(error) => write!(f, "{error}"),
            Self::MemoryGrew { before, after } => write!(
                f,
                "memory grew from {before} to {after} bytes during the measured iterations"
            ),
        }
    }
}

impl std::error::Error for RunError {}
