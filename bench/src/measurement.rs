mod clock;
mod measure;
mod passes;
mod phase_hooks;
mod plan;
mod step_stats;

pub use clock::Clock;
#[cfg(not(target_arch = "wasm32"))]
pub use clock::NativeClock;
pub use measure::{IterationTimes, Measurement, MeasurementError, measure, measure_with};
pub use passes::Passes;
pub use phase_hooks::PhaseHooks;
pub use plan::{MeasurementPlan, PlanError};
pub use step_stats::{RESOLUTION_SAMPLES, StepStats};
