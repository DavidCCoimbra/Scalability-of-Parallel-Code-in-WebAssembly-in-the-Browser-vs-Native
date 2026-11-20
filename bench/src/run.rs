mod error;
mod memory_tracker;

pub use error::RunError;

use crate::calibration::{CalibrationPlan, Pause, calibrate_probes, pause_for};
use crate::config::RunConfig;
use crate::measurement::{Clock, measure_with};
use crate::platform::{MemoryProbe, Platform};
use crate::pool;
use crate::results::{CSV_HEADER, Record};
use memory_tracker::MemoryTracker;

pub fn run_in_pool<C, M, P>(
    config: &RunConfig,
    platform: &Platform<C, M, P>,
) -> Result<Vec<Record>, RunError>
where
    C: Clock,
    M: MemoryProbe,
    P: Pause,
{
    pool::check(config.threads.get())?;
    execute(config, platform)
}

pub fn execute<C, M, P>(
    config: &RunConfig,
    platform: &Platform<C, M, P>,
) -> Result<Vec<Record>, RunError>
where
    C: Clock,
    M: MemoryProbe,
    P: Pause,
{
    let clock = &platform.clock;
    let image = config.image.image();
    let input_fingerprint = image.fingerprint();
    let mut workload = config.workload.build_with(image, config.grain);
    let calibration = (config.calibration > 0).then(|| {
        let plan = CalibrationPlan {
            samples: config.calibration,
            pause_ns: pause_for(workload.as_mut(), clock),
        };
        calibrate_probes(clock, &platform.pause, plan)
    });
    let mut memory = MemoryTracker::new(&platform.memory);
    let measurement = measure_with(workload.as_mut(), clock, config.plan, &mut memory)?;
    memory.check()?;
    let context = config
        .context(input_fingerprint)
        .with_memory(memory.sizes())
        .with_buffers(workload.buffers());
    let mut records = calibration
        .map(|calibration| context.calibration_records(&calibration, measurement.checksum()))
        .unwrap_or_default();
    records.extend(context.records(&measurement));
    Ok(records)
}

pub fn to_csv(records: &[Record]) -> String {
    let mut csv = String::from(CSV_HEADER);
    csv.push('\n');
    records.iter().for_each(|record| {
        csv.push_str(&record.to_csv_row());
        csv.push('\n');
    });
    csv
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::calibration::Probe;
    use crate::config::RunConfig;
    use crate::platform::Platform;
    use crate::results::{CSV_HEADER, Phase};

    #[test]
    fn execute_returns_one_record_per_iteration() {
        let config = RunConfig::from_query(
            "env=native&workload=hist-local&input=few&k=4&threads=1&width=128&height=128&warmup=1&iters=3&calibration=0",
        )
        .unwrap();
        let records = execute(&config, &Platform::native()).unwrap();
        assert_eq!(records.len(), 4);
        assert_eq!(records[0].phase, Phase::Warmup);
        assert!(
            records
                .iter()
                .all(|record| record.context.config.environment == config.environment)
        );
    }

    #[test]
    fn passes_keep_one_record_per_iteration_and_the_single_pass_checksum() {
        let line = "env=native&workload=filter&input=noise&threads=1&width=64&height=64&warmup=1&iters=2&calibration=0";
        let once = execute(&RunConfig::from_query(line).unwrap(), &Platform::native()).unwrap();
        let config = RunConfig::from_query(&format!("{line}&passes=3")).unwrap();
        let thrice = execute(&config, &Platform::native()).unwrap();
        assert_eq!(thrice.len(), once.len());
        assert!(
            thrice
                .iter()
                .all(|record| record.checksum == once[0].checksum)
        );
    }

    #[test]
    fn calibration_rows_come_before_the_workload_iterations() {
        let config = RunConfig::from_query(
            "env=native&workload=filter&input=noise&threads=2&width=32&height=32&warmup=1&iters=1&calibration=2",
        )
        .unwrap();
        let pool = crate::test_support::pool(2);
        let records = pool.install(|| execute(&config, &Platform::native()).unwrap());
        let phases: Vec<_> = records.iter().map(|record| record.phase).collect();
        let probe_rows = [Probe::Broadcast, Probe::ParIter].map(|probe| {
            [
                Phase::CalibrationWarm(probe),
                Phase::CalibrationWarm(probe),
                Phase::CalibrationCold(probe),
                Phase::CalibrationCold(probe),
            ]
        });
        let expected: Vec<_> = std::iter::once(Phase::CalibrationPause)
            .chain(probe_rows.into_iter().flatten())
            .chain([Phase::Warmup, Phase::Measured])
            .collect();
        assert_eq!(phases, expected);
        assert!(records[0].ns >= crate::calibration::MIN_PAUSE_NS);
    }

    #[test]
    fn records_carry_the_fingerprint_of_the_input_image() {
        use crate::workloads::Checksum;
        let config = RunConfig::from_query(
            "env=native&workload=filter&input=noise&threads=1&width=32&height=32&warmup=0&iters=1",
        )
        .unwrap();
        let image = config.image.image();
        let records = execute(&config, &Platform::native()).unwrap();
        assert!(
            records.iter().all(
                |record| record.context.input_fingerprint == Checksum::of_bytes(image.pixels())
            )
        );
    }

    #[test]
    fn records_carry_the_memory_size_before_and_after_on_linux() {
        let config = RunConfig::from_query(
            "env=native&workload=filter&input=noise&threads=1&width=32&height=32&warmup=1&iters=2&calibration=0",
        )
        .unwrap();
        let records = execute(&config, &Platform::native()).unwrap();
        let memory = records[0].context.memory;
        assert_eq!(memory.before_warmup.is_some(), cfg!(target_os = "linux"));
        assert_eq!(memory.after_measured.is_some(), cfg!(target_os = "linux"));
        assert!(records.iter().all(|record| record.context.memory == memory));
    }

    #[test]
    fn filter_records_both_buffer_addresses_and_histograms_only_the_input() {
        let line =
            "env=native&input=few&k=4&threads=1&width=32&height=32&warmup=0&iters=1&calibration=0";
        let filter = execute(
            &RunConfig::from_query(&format!("{line}&workload=filter")).unwrap(),
            &Platform::native(),
        )
        .unwrap();
        let buffers = filter[0].context.buffers;
        assert!(buffers.input.is_some() && buffers.output.is_some());
        let histogram = execute(
            &RunConfig::from_query(&format!("{line}&workload=hist-atomic")).unwrap(),
            &Platform::native(),
        )
        .unwrap();
        let buffers = histogram[0].context.buffers;
        assert!(buffers.input.is_some() && buffers.output.is_none());
    }

    #[test]
    fn a_padded_filter_run_keeps_the_fingerprint_and_checksum_of_the_unpadded_one() {
        let line = "env=native&workload=filter&input=noise&threads=1&width=48&height=16&warmup=0&iters=1&calibration=0";
        let plain = execute(&RunConfig::from_query(line).unwrap(), &Platform::native()).unwrap();
        let padded = execute(
            &RunConfig::from_query(&format!("{line}&pitch=4096")).unwrap(),
            &Platform::native(),
        )
        .unwrap();
        assert_eq!(
            padded[0].context.input_fingerprint,
            plain[0].context.input_fingerprint
        );
        assert_eq!(padded[0].checksum, plain[0].checksum);
    }

    #[test]
    fn csv_has_header_then_rows() {
        let config = RunConfig::from_query(
            "env=firefox&workload=filter&input=noise&threads=1&width=16&height=16&warmup=0&iters=2&calibration=0",
        )
        .unwrap();
        let csv = to_csv(&execute(&config, &Platform::native()).unwrap());
        let lines: Vec<_> = csv.lines().collect();
        assert_eq!(lines[0], CSV_HEADER);
        assert_eq!(lines.len(), 3);
        assert!(lines[1].starts_with("firefox,filter,noise,,16,16,"));
        assert!(csv.ends_with('\n'));
    }
}
