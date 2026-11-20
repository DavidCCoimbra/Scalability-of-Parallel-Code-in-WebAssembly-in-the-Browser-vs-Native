use crate::input::GrayImage;
use crate::workloads::Workload;
use crate::workloads::histogram::Histogram;

pub(crate) fn pool(threads: usize) -> rayon::ThreadPool {
    rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .expect("test pool starts")
}

pub(crate) fn prepare_and_run<W: Workload + Send + ?Sized>(workload: &mut W, threads: usize) {
    pool(threads).install(|| {
        workload.prepare();
        workload.run();
    });
}

pub(crate) fn sequential_histogram(image: &GrayImage) -> Histogram {
    let mut histogram = Histogram::default();
    image
        .pixels()
        .iter()
        .for_each(|&value| histogram.record(value));
    histogram
}
