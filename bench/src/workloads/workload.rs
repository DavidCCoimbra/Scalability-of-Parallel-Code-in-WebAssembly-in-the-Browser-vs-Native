use super::{BufferAddresses, Checksum};

/// `prepare` resets state outside the timed region; `run` is the timed work and ends with the
/// workload's final result stored (the output image, the merged histogram, the sorted keys);
/// `checksum` only hashes that stored result, so no part of computing it is left untimed.
pub trait Workload {
    fn prepare(&mut self) {}
    fn run(&mut self);
    fn checksum(&self) -> Checksum;

    /// Where the image buffers start, recorded for the 4K-aliasing analysis.
    fn buffers(&self) -> BufferAddresses {
        BufferAddresses::default()
    }
}
