use bench::experiment::{InputKind, WorkloadKind};
use bench::input::{Palette, SEED};
use bench::measurement::{MeasurementPlan, NativeClock, Passes, measure};
use bench::workloads::Checksum;

const WIDTH: usize = 192;
const HEIGHT: usize = 160;
const THREAD_COUNTS: [usize; 3] = [1, 3, 8];
const PASS_COUNTS: [usize; 3] = [1, 2, 5];

struct Golden {
    workload: WorkloadKind,
    input: InputKind,
    checksum: u64,
}

const fn golden(workload: WorkloadKind, input: InputKind, checksum: u64) -> Golden {
    Golden {
        workload,
        input,
        checksum,
    }
}

const FEW_1: InputKind = InputKind::few(1);
const FEW_256: InputKind = InputKind::few(256);
const CONSECUTIVE_4: InputKind = InputKind::FewColors {
    k: 4,
    palette: Palette::Consecutive,
};
const CONSECUTIVE_16: InputKind = InputKind::FewColors {
    k: 16,
    palette: Palette::Consecutive,
};

// Pinned when the consecutive palette was added (v2), and checked against a Python count of
// bench/tools/golden_inputs.py's few_colors(192, 160, SEED, k, consecutive=True).
const CONSECUTIVE_4_CHECKSUM: u64 = 0x1dc3_154e_d830_a34f;
const CONSECUTIVE_16_CHECKSUM: u64 = 0x577a_a80c_5171_14e7;

const GOLDEN: [Golden; 19] = [
    golden(
        WorkloadKind::Filter,
        InputKind::Noise,
        0xfb6a_b99c_a3f4_7d32,
    ),
    golden(WorkloadKind::HistogramAtomic, FEW_1, 0x32fa_988f_a7a1_103d),
    golden(
        WorkloadKind::HistogramAtomic,
        FEW_256,
        0xbcdd_ff52_6a1c_f985,
    ),
    golden(WorkloadKind::HistogramLocal, FEW_1, 0x32fa_988f_a7a1_103d),
    golden(WorkloadKind::HistogramLocal, FEW_256, 0xbcdd_ff52_6a1c_f985),
    golden(
        WorkloadKind::HistogramAtomicPrivate,
        FEW_1,
        0x32fa_988f_a7a1_103d,
    ),
    golden(
        WorkloadKind::HistogramAtomicPrivate,
        FEW_256,
        0xbcdd_ff52_6a1c_f985,
    ),
    golden(
        WorkloadKind::HistogramAtomicPacked,
        FEW_1,
        0x32fa_988f_a7a1_103d,
    ),
    golden(
        WorkloadKind::HistogramAtomicPacked,
        FEW_256,
        0xbcdd_ff52_6a1c_f985,
    ),
    golden(WorkloadKind::Sort, InputKind::Noise, 0x42b2_0973_fc05_a3aa),
    golden(
        WorkloadKind::HistogramAtomic,
        CONSECUTIVE_4,
        CONSECUTIVE_4_CHECKSUM,
    ),
    golden(
        WorkloadKind::HistogramLocal,
        CONSECUTIVE_4,
        CONSECUTIVE_4_CHECKSUM,
    ),
    golden(
        WorkloadKind::HistogramAtomicPrivate,
        CONSECUTIVE_4,
        CONSECUTIVE_4_CHECKSUM,
    ),
    golden(
        WorkloadKind::HistogramAtomicPacked,
        CONSECUTIVE_4,
        CONSECUTIVE_4_CHECKSUM,
    ),
    golden(
        WorkloadKind::HistogramAtomic,
        CONSECUTIVE_16,
        CONSECUTIVE_16_CHECKSUM,
    ),
    golden(
        WorkloadKind::HistogramLocal,
        CONSECUTIVE_16,
        CONSECUTIVE_16_CHECKSUM,
    ),
    golden(
        WorkloadKind::HistogramAtomicPrivate,
        CONSECUTIVE_16,
        CONSECUTIVE_16_CHECKSUM,
    ),
    golden(
        WorkloadKind::HistogramAtomicPacked,
        CONSECUTIVE_16,
        CONSECUTIVE_16_CHECKSUM,
    ),
    golden(
        WorkloadKind::SortUnstable,
        InputKind::Noise,
        0x42b2_0973_fc05_a3aa,
    ),
];

fn checksum_with_threads(case: &Golden, threads: usize) -> Checksum {
    let mut workload = case.workload.build(case.input.image(WIDTH, HEIGHT, SEED));
    rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .unwrap()
        .install(|| {
            workload.prepare();
            workload.run();
        });
    workload.checksum()
}

#[test]
fn output_checksums_match_the_values_pinned_before_the_refactor() {
    for case in &GOLDEN {
        for threads in THREAD_COUNTS {
            assert_eq!(
                checksum_with_threads(case, threads),
                Checksum(case.checksum),
                "{} {:?} threads = {threads}",
                case.workload.name(),
                case.input
            );
        }
    }
}

fn checksum_with_passes(case: &Golden, threads: usize, passes: Passes) -> Checksum {
    let mut workload = case.workload.build(case.input.image(WIDTH, HEIGHT, SEED));
    let plan = MeasurementPlan::new(1, 2).unwrap().with_passes(passes);
    rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .unwrap()
        .install(|| measure(workload.as_mut(), &NativeClock::default(), plan))
        .expect("checksum stays the same over the iterations")
        .checksum()
}

#[test]
fn several_passes_keep_the_pinned_checksums_of_the_workloads_that_repeat_identically() {
    let repeating = GOLDEN
        .iter()
        .filter(|case| case.workload.capabilities().repeats_identically);
    for case in repeating {
        for threads in THREAD_COUNTS {
            for passes in PASS_COUNTS.map(|count| Passes::new(count).unwrap()) {
                assert_eq!(
                    checksum_with_passes(case, threads, passes),
                    Checksum(case.checksum),
                    "{} {:?} threads = {threads} passes = {}",
                    case.workload.name(),
                    case.input,
                    passes.count()
                );
            }
        }
    }
}

#[test]
fn golden_cases_cover_both_workloads_that_take_several_passes() {
    let repeating: Vec<_> = GOLDEN
        .iter()
        .filter(|case| case.workload.capabilities().repeats_identically)
        .map(|case| case.workload)
        .collect();
    assert!(repeating.contains(&WorkloadKind::Filter));
    assert!(repeating.contains(&WorkloadKind::HistogramLocal));
}
