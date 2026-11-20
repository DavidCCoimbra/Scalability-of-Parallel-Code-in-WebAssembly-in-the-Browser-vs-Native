use crate::calibration::Probe;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Phase {
    CalibrationPause,
    CalibrationWarm(Probe),
    CalibrationCold(Probe),
    Warmup,
    Measured,
}

impl Phase {
    pub fn name(self) -> &'static str {
        match self {
            Self::CalibrationPause => "calibration-pause",
            Self::CalibrationWarm(_) => "calibration-warm",
            Self::CalibrationCold(_) => "calibration-cold",
            Self::Warmup => "warmup",
            Self::Measured => "measured",
        }
    }

    pub fn probe(self) -> Option<Probe> {
        match self {
            Self::CalibrationWarm(probe) | Self::CalibrationCold(probe) => Some(probe),
            Self::CalibrationPause | Self::Warmup | Self::Measured => None,
        }
    }
}
