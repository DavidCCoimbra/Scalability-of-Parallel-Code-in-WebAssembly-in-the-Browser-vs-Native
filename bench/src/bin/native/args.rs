use bench::config::{ConfigError, RunConfig};

pub fn parse(args: impl IntoIterator<Item = String>) -> Result<RunConfig, ConfigError> {
    let mut pairs = vec![("env".to_string(), "native".to_string())];
    let mut args = args.into_iter();
    while let Some(flag) = args.next() {
        let key = flag
            .strip_prefix("--")
            .filter(|key| *key != "env")
            .ok_or_else(|| ConfigError::Unknown(flag.clone()))?
            .to_string();
        let value = args.next().ok_or(ConfigError::MissingValue(flag))?;
        pairs.push((key, value));
    }
    RunConfig::from_pairs(pairs)
}

#[cfg(test)]
mod tests {
    use super::*;
    use bench::experiment::{Environment, InputKind, WorkloadKind};

    fn parse_line(line: &str) -> Result<RunConfig, ConfigError> {
        parse(line.split_whitespace().map(String::from))
    }

    const FULL: &str = "--workload hist-atomic --input few --k 4 --threads 8 --width 64 --height 32 --warmup 2 --iters 5";

    #[test]
    fn flags_become_a_native_run_config() {
        let config = parse_line(FULL).unwrap();
        assert_eq!(config.environment, Environment::Native);
        assert_eq!(config.workload, WorkloadKind::HistogramAtomic);
        assert_eq!(config.image.input, InputKind::few(4));
        assert_eq!(config.threads.get(), 8);
    }

    #[test]
    fn argument_without_dashes_is_rejected() {
        assert_eq!(
            parse_line(&format!("{FULL} stray")).unwrap_err(),
            ConfigError::Unknown("stray".into())
        );
    }

    #[test]
    fn environment_cannot_be_overridden() {
        assert_eq!(
            parse_line(&format!("{FULL} --env chrome")).unwrap_err(),
            ConfigError::Unknown("--env".into())
        );
    }

    #[test]
    fn flag_without_value_is_rejected() {
        assert_eq!(
            parse_line(&format!("{FULL} --seed")).unwrap_err(),
            ConfigError::MissingValue("--seed".into())
        );
    }

    #[test]
    fn config_errors_pass_through() {
        assert_eq!(
            parse_line(&format!("{FULL} --threads 2")).unwrap_err(),
            ConfigError::Duplicate("threads".into())
        );
    }
}
