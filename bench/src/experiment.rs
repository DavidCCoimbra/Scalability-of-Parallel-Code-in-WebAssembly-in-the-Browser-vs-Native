mod capabilities;
mod environment;
mod input_kind;
mod unknown_name;
mod workload_kind;

pub use capabilities::Capabilities;
pub use environment::Environment;
pub use input_kind::InputKind;
pub use unknown_name::UnknownName;
pub use workload_kind::WorkloadKind;

fn parse_named<T: Copy>(
    name: &str,
    all: &[T],
    name_of: fn(T) -> &'static str,
) -> Result<T, UnknownName> {
    all.iter()
        .copied()
        .find(|&item| name_of(item) == name)
        .ok_or_else(|| UnknownName(name.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::{SEED, few_colors, noise};

    #[test]
    fn kinds_parse_from_their_names() {
        assert_eq!("filter".parse(), Ok(WorkloadKind::Filter));
        assert_eq!("hist-atomic".parse(), Ok(WorkloadKind::HistogramAtomic));
        assert_eq!("hist-local".parse(), Ok(WorkloadKind::HistogramLocal));
        assert_eq!("native".parse(), Ok(Environment::Native));
        assert_eq!("chrome".parse(), Ok(Environment::Chrome));
        assert_eq!("firefox".parse(), Ok(Environment::Firefox));
        assert!("blur".parse::<WorkloadKind>().is_err());
    }

    #[test]
    fn names_round_trip() {
        for kind in [
            WorkloadKind::Filter,
            WorkloadKind::HistogramAtomic,
            WorkloadKind::HistogramLocal,
        ] {
            assert_eq!(kind.name().parse(), Ok(kind));
        }
    }

    #[test]
    fn input_builds_the_matching_image() {
        assert_eq!(InputKind::Noise.image(32, 16, SEED), noise(32, 16, SEED));
        assert_eq!(
            InputKind::few(4).image(32, 16, SEED),
            few_colors(32, 16, SEED, 4)
        );
    }

    #[test]
    fn input_names() {
        assert_eq!(InputKind::Noise.name(), "noise");
        assert_eq!(InputKind::few(4).name(), "few");
    }

    #[test]
    fn every_workload_kind_builds_and_runs() {
        for kind in WorkloadKind::ALL {
            let mut workload = kind.build(noise(64, 64, SEED));
            workload.prepare();
            workload.run();
            workload.checksum();
        }
    }

    #[test]
    fn only_filter_and_local_histogram_repeat_identically() {
        let repeating: Vec<_> = WorkloadKind::ALL
            .into_iter()
            .filter(|kind| kind.capabilities().repeats_identically)
            .collect();
        assert_eq!(
            repeating,
            [WorkloadKind::Filter, WorkloadKind::HistogramLocal]
        );
    }

    #[test]
    fn grain_is_taken_by_the_filter_and_the_local_histogram_only() {
        let taking: Vec<_> = WorkloadKind::ALL
            .into_iter()
            .filter(|kind| kind.capabilities().takes_grain)
            .collect();
        assert_eq!(taking, [WorkloadKind::Filter, WorkloadKind::HistogramLocal]);
    }

    #[test]
    fn a_second_pass_without_prepare_keeps_the_checksum_only_when_it_repeats_identically() {
        let image = few_colors(256, 256, SEED, 16);
        for kind in WorkloadKind::ALL {
            let mut workload = kind.build(image.clone());
            workload.prepare();
            workload.run();
            let once = workload.checksum();
            workload.run();
            let twice = workload.checksum();
            let is_sort = matches!(kind, WorkloadKind::Sort | WorkloadKind::SortUnstable);
            assert_eq!(
                once == twice,
                kind.capabilities().repeats_identically || is_sort,
                "{}",
                kind.name()
            );
        }
    }
}
