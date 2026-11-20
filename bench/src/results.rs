mod memory_sizes;
mod phase;
mod record;
mod run_context;

pub use memory_sizes::MemorySizes;
pub use phase::Phase;
pub use record::Record;
pub use run_context::RunContext;

// Schema 1: every build before v2, the first 13 columns. Schema 2 (v2) appends the rest; readers
// that find no schema column treat the row as schema 1 (harness/native/row_schema.py).
pub const SCHEMA_VERSION: u32 = 2;

pub const CSV_HEADER: &str = "env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum,probe,mem_before_bytes,mem_after_bytes,input_addr_mod4096,input_addr_mod64,output_addr_mod4096,output_addr_mod64,pitch,palette,schema,passes,grain";

#[cfg(test)]
mod tests {
    use super::*;
    use crate::calibration::{Calibration, Probe, ProbeSamples};
    use crate::config::RunConfig;
    use crate::experiment::InputKind;
    use crate::workloads::{BufferAddresses, Checksum};

    #[test]
    fn header_lists_the_shared_schema() {
        assert_eq!(
            CSV_HEADER,
            "env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum,probe,mem_before_bytes,mem_after_bytes,input_addr_mod4096,input_addr_mod64,output_addr_mod4096,output_addr_mod64,pitch,palette,schema,passes,grain"
        );
    }

    const HISTOGRAM: &str =
        "env=native&workload=hist-atomic&threads=8&width=64&height=32&warmup=1&iters=1";

    fn context(input: InputKind) -> RunContext {
        let input = match input {
            InputKind::Noise => "input=noise".to_string(),
            InputKind::FewColors { k, palette } => {
                format!("input=few&k={k}&palette={}", palette.name())
            }
        };
        RunConfig::from_query(&format!("{HISTOGRAM}&{input}"))
            .unwrap()
            .context(Checksum(0xdef))
            .with_memory(MemorySizes {
                before_warmup: Some(4096),
                after_measured: Some(8192),
            })
            .with_buffers(BufferAddresses {
                input: Some(3 * 4096 + 72),
                output: None,
            })
    }

    #[test]
    fn record_formats_as_one_csv_row() {
        let record =
            context(InputKind::few(4)).record(Phase::Measured, 3, 123_456, Checksum(0xabc));
        assert_eq!(
            record.to_csv_row(),
            "native,hist-atomic,few,4,64,32,24301,8,measured,3,123456,0x0000000000000def,0x0000000000000abc,,4096,8192,72,8,,,64,spread,2,1,"
        );
    }

    #[test]
    fn calibration_phases_have_their_own_names() {
        assert_eq!(Phase::CalibrationPause.name(), "calibration-pause");
        assert_eq!(
            Phase::CalibrationWarm(Probe::Broadcast).name(),
            "calibration-warm"
        );
        assert_eq!(
            Phase::CalibrationCold(Probe::ParIter).name(),
            "calibration-cold"
        );
    }

    #[test]
    fn calibration_becomes_a_pause_row_then_warm_and_cold_rows_per_probe() {
        let calibration = Calibration {
            pause_ns: 1_000_000,
            probes: vec![
                ProbeSamples {
                    probe: Probe::Broadcast,
                    warm_ns: vec![10, 11],
                    cold_ns: vec![50],
                },
                ProbeSamples {
                    probe: Probe::ParIter,
                    warm_ns: vec![20],
                    cold_ns: vec![60],
                },
            ],
        };
        let rows: Vec<_> = context(InputKind::Noise)
            .calibration_records(&calibration, Checksum(7))
            .iter()
            .map(|record| (record.phase, record.iteration, record.ns))
            .collect();
        assert_eq!(
            rows,
            [
                (Phase::CalibrationPause, 0, 1_000_000),
                (Phase::CalibrationWarm(Probe::Broadcast), 0, 10),
                (Phase::CalibrationWarm(Probe::Broadcast), 1, 11),
                (Phase::CalibrationCold(Probe::Broadcast), 0, 50),
                (Phase::CalibrationWarm(Probe::ParIter), 0, 20),
                (Phase::CalibrationCold(Probe::ParIter), 0, 60),
            ]
        );
    }

    #[test]
    fn calibration_rows_name_their_probe_and_other_rows_leave_it_empty() {
        let context = context(InputKind::Noise);
        let warm = context.record(Phase::CalibrationWarm(Probe::ParIter), 0, 1, Checksum(1));
        assert_eq!(column(&warm, "probe"), "par-iter");
        let pause = context.record(Phase::CalibrationPause, 0, 1, Checksum(1));
        assert_eq!(column(&pause, "probe"), "");
    }

    fn column(record: &Record, name: &str) -> String {
        let index = CSV_HEADER
            .split(',')
            .position(|column| column == name)
            .unwrap();
        record
            .to_csv_row()
            .split(',')
            .nth(index)
            .unwrap()
            .to_string()
    }

    #[test]
    fn unknown_memory_sizes_are_empty() {
        let record = context(InputKind::Noise)
            .with_memory(MemorySizes::default())
            .record(Phase::Measured, 0, 1, Checksum(1));
        assert_eq!(column(&record, "mem_before_bytes"), "");
        assert_eq!(column(&record, "mem_after_bytes"), "");
    }

    #[test]
    fn rows_carry_the_schema_version_the_passes_and_the_grain() {
        let line =
            "env=native&workload=filter&input=noise&threads=8&width=64&height=32&warmup=1&iters=1";
        let adaptive = RunConfig::from_query(line)
            .unwrap()
            .context(Checksum(0))
            .record(Phase::Measured, 0, 1, Checksum(1));
        assert_eq!(column(&adaptive, "schema"), SCHEMA_VERSION.to_string());
        assert_eq!(
            (column(&adaptive, "passes"), column(&adaptive, "grain")),
            ("1".to_string(), String::new())
        );
        let fixed = RunConfig::from_query(&format!("{line}&passes=4&grain=16"))
            .unwrap()
            .context(Checksum(0))
            .record(Phase::Measured, 0, 1, Checksum(1));
        assert_eq!(
            (column(&fixed, "passes"), column(&fixed, "grain")),
            ("4".to_string(), "16".to_string())
        );
    }

    #[test]
    fn noise_rows_leave_k_empty() {
        let record = context(InputKind::Noise).record(Phase::Warmup, 0, 1, Checksum(1));
        assert!(
            record
                .to_csv_row()
                .starts_with("native,hist-atomic,noise,,64,32,")
        );
    }

    #[test]
    fn context_turns_a_measurement_into_one_record_per_iteration() {
        use crate::input::{SEED, noise};
        use crate::measurement::{MeasurementPlan, NativeClock, measure};
        let config = RunConfig::from_query(
            "env=native&workload=filter&input=noise&threads=1&width=16&height=16&warmup=2&iters=3",
        )
        .unwrap();
        let context = config.context(Checksum(0xdef));
        let mut workload = config.workload.build(noise(16, 16, SEED));
        let measurement = measure(
            workload.as_mut(),
            &NativeClock::default(),
            MeasurementPlan::new(2, 3).unwrap(),
        )
        .unwrap();
        let records = context.records(&measurement);
        let phases: Vec<_> = records
            .iter()
            .map(|record| (record.phase, record.iteration))
            .collect();
        assert_eq!(
            phases,
            [
                (Phase::Warmup, 0),
                (Phase::Warmup, 1),
                (Phase::Measured, 0),
                (Phase::Measured, 1),
                (Phase::Measured, 2)
            ]
        );
        assert!(
            records
                .iter()
                .all(|record| record.checksum == measurement.checksum())
        );
    }

    #[test]
    fn warmup_phase_name() {
        assert_eq!(Phase::Warmup.name(), "warmup");
    }
}
