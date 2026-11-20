use super::MemoryProbe;

const STATM: &str = "/proc/self/statm";
// statm's second field is the resident set size in pages:
// https://man7.org/linux/man-pages/man5/proc_pid_statm.5.html
const RESIDENT_FIELD: usize = 1;
// The page size of x86-64 Linux, the only native platform that measures (the PC).
const PAGE_BYTES: u64 = 4096;

/// Only recorded: the operating system may grow or trim the resident set at any time, so a
/// change is no sign of a broken run. None where /proc does not exist (macOS).
pub struct ResidentSet;

impl MemoryProbe for ResidentSet {
    const GROWTH_FAILS_RUN: bool = false;

    fn bytes(&self) -> Option<u64> {
        let statm = std::fs::read_to_string(STATM).ok()?;
        let pages: u64 = statm.split_whitespace().nth(RESIDENT_FIELD)?.parse().ok()?;
        Some(pages * PAGE_BYTES)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[cfg(target_os = "linux")]
    #[test]
    fn resident_set_is_known_and_positive_on_linux() {
        assert!(ResidentSet.bytes().is_some_and(|bytes| bytes > 0));
    }
}
