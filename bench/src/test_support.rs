pub(crate) fn pool(threads: usize) -> rayon::ThreadPool {
    rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .expect("test pool starts")
}
