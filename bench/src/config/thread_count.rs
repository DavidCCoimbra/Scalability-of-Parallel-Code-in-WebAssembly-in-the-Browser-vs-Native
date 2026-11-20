use std::num::NonZeroUsize;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ThreadCount(NonZeroUsize);

impl ThreadCount {
    pub fn new(threads: usize) -> Option<Self> {
        NonZeroUsize::new(threads).map(Self)
    }

    pub fn get(self) -> usize {
        self.0.get()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_threads_do_not_exist() {
        assert_eq!(ThreadCount::new(0), None);
        assert_eq!(ThreadCount::new(8).map(ThreadCount::get), Some(8));
    }
}
