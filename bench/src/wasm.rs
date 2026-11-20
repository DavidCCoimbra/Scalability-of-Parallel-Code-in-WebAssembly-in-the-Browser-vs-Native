mod linear_memory;
mod performance_clock;

use js_sys::Promise;
use wasm_bindgen::prelude::*;

use crate::build_info::BuildInfo;
use crate::calibration::ThreadSleep;
use crate::config::RunConfig;
use crate::measurement::{RESOLUTION_SAMPLES, StepStats};
use crate::platform::Platform;
use crate::pool;
use crate::run::{run_in_pool, to_csv};
use linear_memory::LinearMemory;
use performance_clock::PerformanceClock;

// wasm_bindgen_rayon starts `threads` Web Workers that share this module's memory (a
// SharedArrayBuffer) and become the Rayon pool. SharedArrayBuffer needs a cross-origin
// isolated page (COOP/COEP headers from harness/server.py).
#[wasm_bindgen(js_name = startThreadPool)]
pub fn start_thread_pool(threads: usize) -> Promise {
    pool::record_start(threads);
    wasm_bindgen_rayon::init_thread_pool(threads)
}

#[wasm_bindgen]
pub fn run(query: &str) -> Result<String, JsError> {
    let config = RunConfig::from_query(query)?;
    let platform = Platform {
        clock: PerformanceClock,
        memory: LinearMemory,
        pause: ThreadSleep,
    };
    Ok(to_csv(&run_in_pool(&config, &platform)?))
}

/// The thread count of the run, read by the same parser as `run`, so the page never parses the
/// configuration itself.
#[wasm_bindgen(js_name = requestedThreads)]
pub fn requested_threads(query: &str) -> Result<usize, JsError> {
    Ok(RunConfig::from_query(query)?.threads.get())
}

#[wasm_bindgen(js_name = clockStats)]
pub fn clock_stats() -> String {
    StepStats::json_of(StepStats::of_clock(&PerformanceClock, RESOLUTION_SAMPLES))
}

#[wasm_bindgen(js_name = buildInfo)]
pub fn build_info() -> String {
    BuildInfo::current().to_json()
}
