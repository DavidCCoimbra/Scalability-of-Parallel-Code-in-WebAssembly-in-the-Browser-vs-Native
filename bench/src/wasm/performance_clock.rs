use wasm_bindgen::prelude::*;

use crate::measurement::Clock;

const NS_PER_MS: f64 = 1_000_000.0;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = performance, js_name = now)]
    fn performance_now() -> f64;
}

pub struct PerformanceClock;

impl Clock for PerformanceClock {
    fn now_ns(&self) -> u64 {
        (performance_now() * NS_PER_MS) as u64
    }
}
