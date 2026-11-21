#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Capabilities {
    /// Several passes per timed sample keep the checksum. The atomic histograms accumulate
    /// across passes and a sort's second pass would sort sorted data.
    pub repeats_identically: bool,
    pub takes_grain: bool,
    pub takes_pitch: bool,
    /// No Rayon call in `run`: the work stays on the calling thread, so only one thread makes
    /// sense.
    pub sequential: bool,
}
