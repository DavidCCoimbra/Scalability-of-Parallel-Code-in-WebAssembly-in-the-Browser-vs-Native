mod args;

use std::process::ExitCode;

use bench::build_info::BuildInfo;
use bench::measurement::{NativeClock, RESOLUTION_SAMPLES, StepStats};
use bench::platform::Platform;
use bench::pool;
use bench::run::{run_in_pool, to_csv};

fn main() -> ExitCode {
    match run() {
        Ok(csv) => {
            print!("{csv}");
            ExitCode::SUCCESS
        }
        Err(message) => {
            eprintln!("error: {message}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> Result<String, String> {
    if std::env::args().nth(1).as_deref() == Some("--build-info") {
        return Ok(build_info());
    }
    let config = args::parse(std::env::args().skip(1)).map_err(|error| error.to_string())?;
    pool::start_global(config.threads.get()).map_err(|error| error.to_string())?;
    let records = run_in_pool(&config, &Platform::native()).map_err(|error| error.to_string())?;
    Ok(to_csv(&records))
}

fn build_info() -> String {
    let resolution = StepStats::of_clock(&NativeClock::default(), RESOLUTION_SAMPLES)
        .map(|stats| stats.most_common);
    format!(
        "{}\n",
        BuildInfo::current()
            .with_clock_resolution(resolution)
            .to_json()
    )
}
