use super::{BufferAddresses, Checksum};

/// Only `run` is timed, so it must end with the final result stored; `prepare` and `checksum`
/// run outside the timed region.
pub trait Workload {
    fn prepare(&mut self) {}
    fn run(&mut self);
    fn checksum(&self) -> Checksum;

    fn buffers(&self) -> BufferAddresses {
        BufferAddresses::default()
    }
}
