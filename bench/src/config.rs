mod error;
mod image_spec;
mod options;
mod thread_count;

pub use error::ConfigError;
pub use image_spec::ImageSpec;
pub use thread_count::ThreadCount;

use crate::experiment::{Environment, WorkloadKind};
use crate::input::SEED;
use crate::measurement::{MeasurementPlan, Passes};
use crate::results::{MemorySizes, RunContext};
use crate::workloads::{BufferAddresses, Checksum, Grain};
use options::Options;

pub const DEFAULT_CALIBRATION_SAMPLES: usize = 200;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RunConfig {
    pub environment: Environment,
    pub workload: WorkloadKind,
    pub image: ImageSpec,
    pub threads: ThreadCount,
    pub calibration: usize,
    pub plan: MeasurementPlan,
    pub grain: Grain,
}

impl RunConfig {
    pub fn from_query(query: &str) -> Result<Self, ConfigError> {
        let pairs = query
            .trim_start_matches('?')
            .split('&')
            .filter(|pair| !pair.is_empty())
            .map(|pair| match pair.split_once('=') {
                Some((key, value)) => Ok((key.to_string(), value.to_string())),
                None => Err(ConfigError::MissingValue(pair.to_string())),
            })
            .collect::<Result<Vec<_>, _>>()?;
        Self::from_pairs(pairs)
    }

    pub fn from_pairs(
        pairs: impl IntoIterator<Item = (String, String)>,
    ) -> Result<Self, ConfigError> {
        let options = Options::collect(pairs)?;
        let environment = options.required("env")?;
        let workload = options.required("workload")?;
        let input = options.input()?;
        let threads = ThreadCount::new(options.positive("threads")?)
            .expect("options.positive never returns zero");
        let width = options.positive("width")?;
        let image = ImageSpec {
            input,
            width,
            height: options.positive("height")?,
            seed: options.optional("seed")?.unwrap_or(SEED),
            pitch: pitch_for(workload, width, options.optional("pitch")?)?,
        };
        let passes = passes_for(workload, options.optional_positive("passes")?)?;
        let plan = MeasurementPlan::new(options.required("warmup")?, options.positive("iters")?)
            .expect("options.positive never returns zero")
            .with_passes(passes);
        Ok(Self {
            environment,
            workload,
            image,
            threads,
            calibration: options
                .optional("calibration")?
                .unwrap_or(DEFAULT_CALIBRATION_SAMPLES),
            plan,
            grain: grain_for(workload, options.optional_positive("grain")?)?,
        })
    }

    pub fn context(&self, input_fingerprint: Checksum) -> RunContext {
        RunContext {
            config: *self,
            input_fingerprint,
            memory: MemorySizes::default(),
            buffers: BufferAddresses::default(),
        }
    }
}

fn passes_for(workload: WorkloadKind, count: Option<usize>) -> Result<Passes, ConfigError> {
    let passes = count.and_then(Passes::new).unwrap_or_default();
    if passes == Passes::ONE || workload.capabilities().repeats_identically {
        Ok(passes)
    } else {
        Err(ConfigError::Unsupported {
            option: "passes",
            workload: workload.name(),
        })
    }
}

fn pitch_for(
    workload: WorkloadKind,
    width: usize,
    pitch: Option<usize>,
) -> Result<Option<usize>, ConfigError> {
    match pitch {
        None => Ok(None),
        Some(_) if !workload.capabilities().takes_pitch => Err(ConfigError::Unsupported {
            option: "pitch",
            workload: workload.name(),
        }),
        Some(pitch) if pitch < width => Err(ConfigError::Invalid {
            option: "pitch",
            value: pitch.to_string(),
        }),
        Some(pitch) => Ok(Some(pitch)),
    }
}

fn grain_for(workload: WorkloadKind, units: Option<usize>) -> Result<Grain, ConfigError> {
    let grain = Grain::new(units);
    if grain.is_adaptive() || workload.capabilities().takes_grain {
        Ok(grain)
    } else {
        Err(ConfigError::Unsupported {
            option: "grain",
            workload: workload.name(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::experiment::{Environment, InputKind, WorkloadKind};
    use crate::input::{Palette, SEED};
    use crate::measurement::Passes;

    const FULL: &str = "env=chrome&workload=hist-atomic&input=few&k=4&threads=8&width=64&height=32&seed=7&warmup=2&iters=5";

    fn query(text: &str) -> Result<RunConfig, ConfigError> {
        RunConfig::from_query(text)
    }

    #[test]
    fn parses_every_option_from_a_query_string() {
        let config = query(FULL).unwrap();
        assert_eq!(config.environment, Environment::Chrome);
        assert_eq!(config.workload, WorkloadKind::HistogramAtomic);
        assert_eq!(config.image.input, InputKind::few(4));
        assert_eq!(
            (
                config.threads.get(),
                config.image.width,
                config.image.height,
                config.image.seed
            ),
            (8, 64, 32, 7)
        );
        assert_eq!((config.plan.warmup(), config.plan.measured()), (2, 5));
    }

    #[test]
    fn leading_question_mark_is_ignored() {
        assert_eq!(query(&format!("?{FULL}")), query(FULL));
    }

    #[test]
    fn seed_defaults_to_the_study_seed() {
        let config = query(
            "env=native&workload=filter&input=noise&threads=1&width=8&height=8&warmup=0&iters=1",
        )
        .unwrap();
        assert_eq!(config.image.seed, SEED);
    }

    #[test]
    fn calibration_defaults_to_the_study_sample_count() {
        let config = query(FULL).unwrap();
        assert_eq!(config.calibration, DEFAULT_CALIBRATION_SAMPLES);
        assert_eq!(DEFAULT_CALIBRATION_SAMPLES, 200);
    }

    #[test]
    fn calibration_sample_count_can_be_set() {
        for samples in [0, 3] {
            let config = query(&format!("{FULL}&calibration={samples}")).unwrap();
            assert_eq!(config.calibration, samples);
        }
    }

    #[test]
    fn passes_default_to_one() {
        assert_eq!(query(FULL).unwrap().plan.passes(), Passes::ONE);
    }

    #[test]
    fn passes_can_be_set_for_workloads_that_repeat_identically() {
        for workload in ["filter", "hist-local"] {
            let line = FULL.replace("hist-atomic", workload);
            let config = query(&format!("{line}&passes=5")).unwrap();
            assert_eq!(config.plan.passes(), Passes::new(5).unwrap());
        }
    }

    #[test]
    fn more_than_one_pass_is_rejected_for_workloads_that_accumulate_or_sort() {
        for workload in [
            "hist-atomic",
            "hist-atomic-private",
            "hist-atomic-packed",
            "sort",
            "sort-unstable",
        ] {
            let line = FULL.replace("hist-atomic", workload);
            assert_eq!(
                query(&format!("{line}&passes=2")).unwrap_err(),
                ConfigError::Unsupported {
                    option: "passes",
                    workload: workload.parse::<WorkloadKind>().unwrap().name(),
                },
                "{workload}"
            );
            assert_eq!(
                query(&format!("{line}&passes=1")).unwrap().plan.passes(),
                Passes::ONE
            );
        }
    }

    #[test]
    fn grain_defaults_to_adaptive() {
        assert_eq!(query(FULL).unwrap().grain, Grain::Adaptive);
    }

    #[test]
    fn grain_is_set_for_the_filter_and_the_two_main_histograms_only() {
        let filter =
            "env=native&workload=filter&input=noise&threads=8&width=64&height=32&warmup=1&iters=1";
        let local = "env=native&workload=hist-local&input=few&k=4&threads=8&width=64&height=32&warmup=1&iters=1";
        for line in [filter, local, FULL] {
            assert_eq!(
                query(&format!("{line}&grain=16")).unwrap().grain,
                Grain::new(Some(16))
            );
        }
        let private = FULL.replace("hist-atomic", "hist-atomic-private");
        assert_eq!(
            query(&format!("{private}&grain=16")).unwrap_err(),
            ConfigError::Unsupported {
                option: "grain",
                workload: "hist-atomic-private",
            }
        );
    }

    #[test]
    fn pitch_is_absent_unless_set_and_at_least_the_width_for_the_filter_only() {
        let filter =
            "env=native&workload=filter&input=noise&threads=8&width=64&height=32&warmup=1&iters=1";
        assert_eq!(query(filter).unwrap().image.pitch, None);
        assert_eq!(query(filter).unwrap().image.row_stride(), 64);
        for pitch in [64, 4160] {
            let config = query(&format!("{filter}&pitch={pitch}")).unwrap();
            assert_eq!(config.image.pitch, Some(pitch));
            assert_eq!(config.image.row_stride(), pitch);
        }
        assert_eq!(
            query(&format!("{filter}&pitch=63")).unwrap_err(),
            ConfigError::Invalid {
                option: "pitch",
                value: "63".to_string()
            }
        );
        assert_eq!(
            query(&format!("{FULL}&pitch=64")).unwrap_err(),
            ConfigError::Unsupported {
                option: "pitch",
                workload: "hist-atomic",
            }
        );
    }

    #[test]
    fn zero_passes_are_rejected() {
        let line = FULL.replace("hist-atomic", "filter");
        assert!(matches!(
            query(&format!("{line}&passes=0")),
            Err(ConfigError::Invalid {
                option: "passes",
                ..
            })
        ));
    }

    #[test]
    fn palette_defaults_to_spread_and_can_be_consecutive_for_few_colors_only() {
        assert_eq!(query(FULL).unwrap().image.input, InputKind::few(4));
        assert_eq!(
            query(&format!("{FULL}&palette=consecutive"))
                .unwrap()
                .image
                .input,
            InputKind::FewColors {
                k: 4,
                palette: Palette::Consecutive
            }
        );
        assert!(matches!(
            query(&format!("{FULL}&palette=rainbow")),
            Err(ConfigError::Invalid {
                option: "palette",
                ..
            })
        ));
        let noise = FULL.replace("input=few&k=4", "input=noise");
        assert_eq!(
            query(&format!("{noise}&palette=spread")).unwrap_err(),
            ConfigError::Invalid {
                option: "palette",
                value: "spread".to_string()
            }
        );
    }

    #[test]
    fn noise_rejects_k() {
        let line = FULL.replace("input=few", "input=noise");
        assert_eq!(
            query(&line).unwrap_err(),
            ConfigError::Invalid {
                option: "k",
                value: "4".to_string()
            }
        );
    }

    #[test]
    fn few_colors_requires_k_in_range() {
        let without = FULL.replace("&k=4", "");
        assert_eq!(query(&without).unwrap_err(), ConfigError::Missing("k"));
        for k in ["0", "257"] {
            let line = FULL.replace("k=4", &format!("k={k}"));
            assert!(
                matches!(query(&line), Err(ConfigError::Invalid { option: "k", .. })),
                "k = {k}"
            );
        }
    }

    #[test]
    fn zero_threads_width_height_or_iters_are_rejected() {
        for (option, from) in [
            ("threads", "threads=8"),
            ("width", "width=64"),
            ("height", "height=32"),
            ("iters", "iters=5"),
        ] {
            let line = FULL.replace(from, &format!("{option}=0"));
            assert!(
                matches!(query(&line), Err(ConfigError::Invalid { option: o, .. }) if o == option),
                "{option}"
            );
        }
    }

    #[test]
    fn missing_option_is_reported() {
        assert_eq!(
            query("env=native&workload=filter&input=noise").unwrap_err(),
            ConfigError::Missing("threads")
        );
    }

    #[test]
    fn unknown_option_is_rejected() {
        assert_eq!(
            query(&format!("{FULL}&colour=red")).unwrap_err(),
            ConfigError::Unknown("colour".into())
        );
    }

    #[test]
    fn repeated_option_is_rejected() {
        assert_eq!(
            query(&format!("{FULL}&threads=2")).unwrap_err(),
            ConfigError::Duplicate("threads".into())
        );
    }

    #[test]
    fn option_without_value_is_rejected() {
        assert_eq!(
            query(&format!("{FULL}&seed")).unwrap_err(),
            ConfigError::MissingValue("seed".into())
        );
    }

    #[test]
    fn invalid_value_is_rejected() {
        let line = FULL.replace("threads=8", "threads=eight");
        assert!(matches!(
            query(&line),
            Err(ConfigError::Invalid {
                option: "threads",
                ..
            })
        ));
    }

    #[test]
    fn context_carries_the_configuration() {
        let config = query(FULL).unwrap();
        let context = config.context(Checksum(3));
        assert_eq!(context.config, config);
        assert_eq!(context.input_fingerprint, Checksum(3));
    }
}
