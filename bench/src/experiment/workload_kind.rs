use std::str::FromStr;

use super::{Capabilities, UnknownName, parse_named};
use crate::input::GrayImage;
use crate::workloads::extras::sort::{ParallelSort, SortKind};
use crate::workloads::gaussian::GaussianBlur;
use crate::workloads::histogram::atomic::AtomicHistogram;
use crate::workloads::histogram::extras::packed::PackedAtomicHistogram;
use crate::workloads::histogram::extras::private::PrivateAtomicHistogram;
use crate::workloads::histogram::local::LocalHistogram;
use crate::workloads::{Grain, Workload};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WorkloadKind {
    Filter,
    HistogramAtomic,
    HistogramLocal,
    // Extras: not part of RQ1 or RQ2.
    HistogramAtomicPrivate,
    HistogramAtomicPacked,
    Sort,
    SortUnstable,
}

impl WorkloadKind {
    pub(super) const ALL: [Self; 7] = [
        Self::Filter,
        Self::HistogramAtomic,
        Self::HistogramLocal,
        Self::HistogramAtomicPrivate,
        Self::HistogramAtomicPacked,
        Self::Sort,
        Self::SortUnstable,
    ];

    pub fn name(self) -> &'static str {
        match self {
            Self::Filter => "filter",
            Self::HistogramAtomic => "hist-atomic",
            Self::HistogramLocal => "hist-local",
            Self::HistogramAtomicPrivate => "hist-atomic-private",
            Self::HistogramAtomicPacked => "hist-atomic-packed",
            Self::Sort => "sort",
            Self::SortUnstable => "sort-unstable",
        }
    }

    pub fn capabilities(self) -> Capabilities {
        match self {
            Self::Filter => Capabilities {
                repeats_identically: true,
                takes_grain: true,
                takes_pitch: true,
            },
            Self::HistogramLocal => Capabilities {
                repeats_identically: true,
                takes_grain: true,
                takes_pitch: false,
            },
            Self::HistogramAtomic
            | Self::HistogramAtomicPrivate
            | Self::HistogramAtomicPacked
            | Self::Sort
            | Self::SortUnstable => Capabilities::default(),
        }
    }

    pub fn build(self, image: GrayImage) -> Box<dyn Workload + Send> {
        self.build_with(image, Grain::Adaptive)
    }

    pub fn build_with(self, image: GrayImage, grain: Grain) -> Box<dyn Workload + Send> {
        debug_assert!(grain.is_adaptive() || self.capabilities().takes_grain);
        match self {
            Self::Filter => Box::new(GaussianBlur::with_grain(image, grain)),
            Self::HistogramAtomic => Box::new(AtomicHistogram::new(image)),
            Self::HistogramLocal => Box::new(LocalHistogram::with_grain(image, grain)),
            Self::HistogramAtomicPrivate => Box::new(PrivateAtomicHistogram::new(image)),
            Self::HistogramAtomicPacked => Box::new(PackedAtomicHistogram::new(image)),
            Self::Sort => Box::new(ParallelSort::new(image, SortKind::Stable)),
            Self::SortUnstable => Box::new(ParallelSort::new(image, SortKind::Unstable)),
        }
    }
}

impl FromStr for WorkloadKind {
    type Err = UnknownName;

    fn from_str(name: &str) -> Result<Self, Self::Err> {
        parse_named(name, &Self::ALL, Self::name)
    }
}
