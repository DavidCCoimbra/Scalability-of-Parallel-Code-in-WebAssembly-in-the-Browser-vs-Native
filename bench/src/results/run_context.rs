use super::{MemorySizes, Phase, Record};
use crate::calibration::Calibration;
use crate::config::RunConfig;
use crate::measurement::Measurement;
use crate::workloads::{BufferAddresses, Checksum};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RunContext {
    pub config: RunConfig,
    pub input_fingerprint: Checksum,
    pub memory: MemorySizes,
    pub buffers: BufferAddresses,
}

impl RunContext {
    pub fn with_memory(self, memory: MemorySizes) -> Self {
        Self { memory, ..self }
    }

    pub fn with_buffers(self, buffers: BufferAddresses) -> Self {
        Self { buffers, ..self }
    }

    pub fn records(&self, measurement: &Measurement) -> Vec<Record> {
        let checksum = measurement.checksum();
        let mut records = self.phase_records(Phase::Warmup, measurement.warmup_ns(), checksum);
        records.extend(self.phase_records(Phase::Measured, measurement.measured_ns(), checksum));
        records
    }

    pub fn calibration_records(
        &self,
        calibration: &Calibration,
        checksum: Checksum,
    ) -> Vec<Record> {
        let mut records =
            vec![self.record(Phase::CalibrationPause, 0, calibration.pause_ns, checksum)];
        for samples in &calibration.probes {
            let (warm, cold) = (
                Phase::CalibrationWarm(samples.probe),
                Phase::CalibrationCold(samples.probe),
            );
            records.extend(self.phase_records(warm, &samples.warm_ns, checksum));
            records.extend(self.phase_records(cold, &samples.cold_ns, checksum));
        }
        records
    }

    fn phase_records(&self, phase: Phase, times: &[u64], checksum: Checksum) -> Vec<Record> {
        times
            .iter()
            .enumerate()
            .map(|(iteration, &ns)| self.record(phase, iteration, ns, checksum))
            .collect()
    }

    pub fn record(&self, phase: Phase, iteration: usize, ns: u64, checksum: Checksum) -> Record {
        Record {
            context: *self,
            phase,
            iteration,
            ns,
            checksum,
        }
    }
}
