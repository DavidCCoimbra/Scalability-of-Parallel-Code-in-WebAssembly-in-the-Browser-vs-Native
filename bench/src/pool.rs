mod error;

pub use error::PoolError;

use std::sync::atomic::{AtomicUsize, Ordering};

// Each host starts the pool once per process (native) or per page (WASM), so a run whose
// config asks for another N would silently measure the wrong N; check() refuses it. An atomic,
// because every Web Worker of the WASM pool shares this memory.
static POOL_THREADS: AtomicUsize = AtomicUsize::new(0);
const NOT_STARTED: usize = 0;

pub fn record_start(threads: usize) {
    POOL_THREADS.store(threads, Ordering::SeqCst);
}

/// The measured iterations are then called from the main thread, outside the pool, as the WASM
/// coordinator worker calls them.
#[cfg(not(target_arch = "wasm32"))]
pub fn start_global(threads: usize) -> Result<(), PoolError> {
    rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build_global()
        .map_err(|error| PoolError::Build(error.to_string()))?;
    record_start(threads);
    Ok(())
}

pub fn check(requested: usize) -> Result<(), PoolError> {
    verify(POOL_THREADS.load(Ordering::SeqCst), requested)
}

fn verify(pool: usize, requested: usize) -> Result<(), PoolError> {
    match pool {
        NOT_STARTED => Err(PoolError::NotStarted),
        threads if threads != requested => Err(PoolError::Mismatch {
            pool: threads,
            requested,
        }),
        _ => Ok(()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_pool_that_was_not_started_is_refused() {
        assert_eq!(verify(NOT_STARTED, 4), Err(PoolError::NotStarted));
    }

    #[test]
    fn a_pool_of_another_size_is_refused() {
        assert_eq!(
            verify(8, 4),
            Err(PoolError::Mismatch {
                pool: 8,
                requested: 4
            })
        );
        assert_eq!(verify(4, 4), Ok(()));
    }
}
