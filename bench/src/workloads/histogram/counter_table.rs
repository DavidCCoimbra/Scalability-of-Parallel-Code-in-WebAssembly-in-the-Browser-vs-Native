use std::sync::atomic::Ordering;

use super::counter::Counter;
use super::{BINS, Histogram};

pub struct CounterTable<C: Counter> {
    // A fixed length of BINS lets the compiler prove a u8 index in bounds and drop the check
    // from the per-pixel loop; a Box<[C]> of unknown length keeps a cmp and a branch per pixel.
    counters: Box<[C; BINS]>,
}

impl<C: Counter> Default for CounterTable<C> {
    fn default() -> Self {
        // Built on the heap: a padded table is BINS x 128 bytes, too large to build on the
        // stack and then move.
        let counters = match (0..BINS)
            .map(|_| C::default())
            .collect::<Box<[C]>>()
            .try_into()
        {
            Ok(counters) => counters,
            Err(_) => unreachable!("the iterator yields exactly BINS counters"),
        };
        Self { counters }
    }
}

impl<C: Counter> CounterTable<C> {
    pub fn reset(&mut self) {
        self.counters
            .iter_mut()
            .for_each(|counter| *counter.atomic_mut().get_mut() = 0);
    }

    // The ordering changes nothing on our targets: an x86 locked add is a full barrier whatever
    // the ordering argument, and WASM atomics are always sequentially consistent. inline(always)
    // keeps the `lock add` in the per-pixel loop instead of a call.
    #[inline(always)]
    pub fn increment(&self, value: u8) {
        self.counters[usize::from(value)]
            .atomic()
            .fetch_add(1, Ordering::Relaxed);
    }

    pub fn read(&self) -> Histogram {
        let mut counts = [0; BINS];
        counts
            .iter_mut()
            .zip(self.counters.iter())
            .for_each(|(count, counter)| *count = counter.atomic().load(Ordering::Relaxed));
        Histogram::from_counts(counts)
    }

    pub fn stride(&self) -> usize {
        let first = &self.counters[0] as *const C as usize;
        let second = &self.counters[1] as *const C as usize;
        second - first
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::workloads::histogram::PackedCounter;
    use crate::workloads::histogram::padded_counter::{CACHE_LINE_BYTES, PaddedCounter};

    #[test]
    fn increment_counts_each_value_and_reset_clears_it() {
        let mut table = CounterTable::<PackedCounter>::default();
        for value in [0, 9, 9, 255] {
            table.increment(value);
        }
        let histogram = table.read();
        assert_eq!((histogram.count(9), histogram.count(255)), (2, 1));
        table.reset();
        assert_eq!(table.read().total(), 0);
    }

    #[test]
    fn stride_is_the_counter_size() {
        assert_eq!(
            CounterTable::<PaddedCounter>::default().stride(),
            CACHE_LINE_BYTES
        );
        assert_eq!(
            CounterTable::<PackedCounter>::default().stride(),
            size_of::<u64>()
        );
    }
}
