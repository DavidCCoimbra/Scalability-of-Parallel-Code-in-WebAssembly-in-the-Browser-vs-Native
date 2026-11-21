use super::{Phase, RunContext, SCHEMA_VERSION};
use crate::calibration::Probe;
use crate::input::Palette;
use crate::workloads::Checksum;

const HEX_U64_WIDTH: usize = "0x".len() + 2 * size_of::<u64>();
// The 4K-aliasing window of x86 memory disambiguation (Intel optimization manual, "4K
// aliasing") and the cache line.
const ALIASING_BYTES: usize = 4096;
const CACHE_LINE_BYTES: usize = 64;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Record {
    pub context: RunContext,
    pub phase: Phase,
    pub iteration: usize,
    pub ns: u64,
    pub checksum: Checksum,
}

impl Record {
    pub fn to_csv_row(&self) -> String {
        let context = &self.context;
        let config = &context.config;
        let image = &config.image;
        [
            config.environment.name().to_string(),
            config.workload.name().to_string(),
            image.input.name().to_string(),
            optional(image.input.k()),
            image.width.to_string(),
            image.height.to_string(),
            image.seed.to_string(),
            config.threads.get().to_string(),
            self.phase.name().to_string(),
            self.iteration.to_string(),
            self.ns.to_string(),
            hex(context.input_fingerprint),
            hex(self.checksum),
            optional(self.phase.probe().map(Probe::name)),
            optional(context.memory.before_warmup),
            optional(context.memory.after_measured),
            optional(
                context
                    .buffers
                    .input
                    .map(|address| address % ALIASING_BYTES),
            ),
            optional(
                context
                    .buffers
                    .input
                    .map(|address| address % CACHE_LINE_BYTES),
            ),
            optional(
                context
                    .buffers
                    .output
                    .map(|address| address % ALIASING_BYTES),
            ),
            optional(
                context
                    .buffers
                    .output
                    .map(|address| address % CACHE_LINE_BYTES),
            ),
            image.row_stride().to_string(),
            optional(image.input.palette().map(Palette::name)),
            SCHEMA_VERSION.to_string(),
            config.plan.passes().count().to_string(),
            optional(config.grain.units()),
            optional(context.memory.before_measured),
        ]
        .join(",")
    }
}

fn hex(checksum: Checksum) -> String {
    format!("{:#0width$x}", checksum.0, width = HEX_U64_WIDTH)
}

fn optional(value: Option<impl ToString>) -> String {
    value.map(|value| value.to_string()).unwrap_or_default()
}
