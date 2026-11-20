use std::collections::HashMap;
use std::ops::RangeInclusive;
use std::str::FromStr;

use super::ConfigError;
use crate::experiment::InputKind;
use crate::input::MAX_COLORS;

const KEYS: &[&str] = &[
    "env",
    "workload",
    "input",
    "k",
    "threads",
    "width",
    "height",
    "seed",
    "warmup",
    "iters",
    "calibration",
    "passes",
    "grain",
    // Extras: no measured campaign sets pitch or palette.
    "pitch",
    "palette",
];

pub(super) struct Options(HashMap<&'static str, String>);

impl Options {
    pub(super) fn collect(
        pairs: impl IntoIterator<Item = (String, String)>,
    ) -> Result<Self, ConfigError> {
        let mut values = HashMap::new();
        for (key, value) in pairs {
            let name = KEYS
                .iter()
                .copied()
                .find(|&known| known == key)
                .ok_or_else(|| ConfigError::Unknown(key.clone()))?;
            if values.insert(name, value).is_some() {
                return Err(ConfigError::Duplicate(key));
            }
        }
        Ok(Self(values))
    }

    pub(super) fn optional<T: FromStr>(
        &self,
        option: &'static str,
    ) -> Result<Option<T>, ConfigError> {
        self.0
            .get(option)
            .map(|value| {
                value.parse().map_err(|_| ConfigError::Invalid {
                    option,
                    value: value.clone(),
                })
            })
            .transpose()
    }

    pub(super) fn required<T: FromStr>(&self, option: &'static str) -> Result<T, ConfigError> {
        self.optional(option)?.ok_or(ConfigError::Missing(option))
    }

    fn in_range(
        &self,
        option: &'static str,
        range: RangeInclusive<usize>,
    ) -> Result<usize, ConfigError> {
        let value: usize = self.required(option)?;
        if range.contains(&value) {
            Ok(value)
        } else {
            Err(ConfigError::Invalid {
                option,
                value: value.to_string(),
            })
        }
    }

    pub(super) fn positive(&self, option: &'static str) -> Result<usize, ConfigError> {
        self.in_range(option, 1..=usize::MAX)
    }

    pub(super) fn optional_positive(
        &self,
        option: &'static str,
    ) -> Result<Option<usize>, ConfigError> {
        if self.0.contains_key(option) {
            self.positive(option).map(Some)
        } else {
            Ok(None)
        }
    }

    pub(super) fn input(&self) -> Result<InputKind, ConfigError> {
        let name: String = self.required("input")?;
        match name.as_str() {
            "noise" => match ["k", "palette"]
                .into_iter()
                .find_map(|option| self.0.get(option).map(|value| (option, value)))
            {
                Some((option, value)) => Err(ConfigError::Invalid {
                    option,
                    value: value.clone(),
                }),
                None => Ok(InputKind::Noise),
            },
            "few" => Ok(InputKind::FewColors {
                k: self.in_range("k", 1..=MAX_COLORS)?,
                palette: self.optional("palette")?.unwrap_or_default(),
            }),
            _ => Err(ConfigError::Invalid {
                option: "input",
                value: name,
            }),
        }
    }
}
