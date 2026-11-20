use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ConfigError {
    Unknown(String),
    Duplicate(String),
    MissingValue(String),
    Missing(&'static str),
    Invalid {
        option: &'static str,
        value: String,
    },
    Unsupported {
        option: &'static str,
        workload: &'static str,
    },
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Unknown(option) => write!(f, "unknown option {option}"),
            Self::Duplicate(option) => write!(f, "option {option} given twice"),
            Self::MissingValue(option) => write!(f, "option {option} needs a value"),
            Self::Missing(option) => write!(f, "missing option {option}"),
            Self::Invalid { option, value } => write!(f, "invalid value `{value}` for {option}"),
            Self::Unsupported { option, workload } => {
                write!(f, "option {option} is not supported by workload {workload}")
            }
        }
    }
}

impl std::error::Error for ConfigError {}
