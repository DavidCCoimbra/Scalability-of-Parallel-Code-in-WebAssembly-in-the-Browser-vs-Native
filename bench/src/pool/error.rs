use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PoolError {
    NotStarted,
    Mismatch { pool: usize, requested: usize },
    Build(String),
}

impl fmt::Display for PoolError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::NotStarted => write!(f, "the thread pool was not started"),
            Self::Mismatch { pool, requested } => {
                write!(
                    f,
                    "thread pool has {pool} threads, config asks for {requested}"
                )
            }
            Self::Build(reason) => write!(f, "thread pool could not start: {reason}"),
        }
    }
}

impl std::error::Error for PoolError {}
