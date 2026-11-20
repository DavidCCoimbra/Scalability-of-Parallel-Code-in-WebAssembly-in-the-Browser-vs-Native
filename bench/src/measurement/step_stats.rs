use super::Clock;

pub const RESOLUTION_SAMPLES: usize = 100_000;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StepStats {
    pub smallest: u64,
    pub most_common: u64,
}

impl StepStats {
    pub fn from_readings(readings: impl Iterator<Item = u64>) -> Option<Self> {
        let mut readings = readings.peekable();
        let mut counts = std::collections::BTreeMap::new();
        // A BTreeMap keeps its keys sorted, so the first key is the smallest step.
        while let (Some(current), Some(&next)) = (readings.next(), readings.peek()) {
            let step = next.saturating_sub(current);
            if step > 0 {
                *counts.entry(step).or_insert(0usize) += 1;
            }
        }
        let smallest = *counts.keys().next()?;
        // On a tie in count, Reverse makes the smaller step win.
        let most_common = counts
            .iter()
            .max_by_key(|&(&step, &count)| (count, std::cmp::Reverse(step)))
            .map(|(&step, _)| step)?;
        Some(Self {
            smallest,
            most_common,
        })
    }

    pub fn of_clock(clock: &impl Clock, samples: usize) -> Option<Self> {
        Self::from_readings((0..samples).map(|_| clock.now_ns()))
    }

    pub fn json_of(stats: Option<Self>) -> String {
        let field =
            |value: Option<u64>| value.map_or_else(|| "null".to_string(), |ns| ns.to_string());
        format!(
            r#"{{"resolutionNs":{},"smallestStepNs":{}}}"#,
            field(stats.map(|stats| stats.most_common)),
            field(stats.map(|stats| stats.smallest))
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn step_stats_report_smallest_and_most_common_step() {
        let stats = StepStats::from_readings([0, 0, 100, 200, 300, 350, 450].into_iter()).unwrap();
        assert_eq!(
            stats,
            StepStats {
                smallest: 50,
                most_common: 100
            }
        );
    }

    #[test]
    fn json_has_both_figures_or_nulls() {
        let stats = StepStats {
            smallest: 20,
            most_common: 100,
        };
        assert_eq!(
            StepStats::json_of(Some(stats)),
            r#"{"resolutionNs":100,"smallestStepNs":20}"#
        );
        assert_eq!(
            StepStats::json_of(None),
            r#"{"resolutionNs":null,"smallestStepNs":null}"#
        );
    }

    #[test]
    fn step_stats_are_unknown_without_any_step() {
        assert_eq!(StepStats::from_readings([7, 7, 7].into_iter()), None);
    }
}
