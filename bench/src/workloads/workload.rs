use super::{BufferAddresses, Checksum};

pub trait Workload {
    fn prepare(&mut self) {}
    fn run(&mut self);
    fn checksum(&self) -> Checksum;

    fn buffers(&self) -> BufferAddresses {
        BufferAddresses::default()
    }
}
