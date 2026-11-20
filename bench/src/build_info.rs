mod json;

use json::json_string;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BuildInfo {
    pub features: Vec<&'static str>,
    pub rustc: &'static str,
    pub wasm_bindgen: &'static str,
    pub rustflags: &'static str,
    pub clock_resolution_ns: Option<u64>,
}

impl BuildInfo {
    pub fn current() -> Self {
        let features = [("pad64", cfg!(feature = "pad64"))]
            .into_iter()
            .filter_map(|(name, enabled)| enabled.then_some(name))
            .collect();
        Self {
            features,
            rustc: env!("BENCH_RUSTC_VERSION"),
            wasm_bindgen: env!("BENCH_WASM_BINDGEN_VERSION"),
            rustflags: env!("BENCH_RUSTFLAGS"),
            clock_resolution_ns: None,
        }
    }

    pub fn with_clock_resolution(self, clock_resolution_ns: Option<u64>) -> Self {
        Self {
            clock_resolution_ns,
            ..self
        }
    }

    pub fn to_json(&self) -> String {
        let features = self
            .features
            .iter()
            .map(|feature| json_string(feature))
            .collect::<Vec<_>>()
            .join(",");
        let resolution = self
            .clock_resolution_ns
            .map_or_else(|| "null".to_string(), |ns| ns.to_string());
        format!(
            r#"{{"features":[{features}],"rustc":{},"wasmBindgen":{},"rustflags":{},"clockResolutionNs":{resolution}}}"#,
            json_string(self.rustc),
            json_string(self.wasm_bindgen),
            json_string(self.rustflags)
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reports_the_compiler_that_built_the_artifact() {
        assert!(BuildInfo::current().rustc.starts_with("rustc "));
    }

    #[test]
    fn reports_the_pinned_wasm_bindgen_version() {
        let pin = format!(r#"wasm-bindgen = "={}""#, BuildInfo::current().wasm_bindgen);
        assert!(include_str!("../Cargo.toml").contains(&pin));
    }

    #[test]
    fn reports_enabled_features() {
        let features = BuildInfo::current().features;
        assert_eq!(features.contains(&"pad64"), cfg!(feature = "pad64"));
    }

    #[test]
    fn serialises_as_json_with_escaped_strings() {
        let info = BuildInfo {
            features: vec!["pad64"],
            rustc: "rustc 1.0 \"x\"",
            wasm_bindgen: "0.2.1",
            rustflags: "-C a",
            clock_resolution_ns: Some(41),
        };
        assert_eq!(
            info.to_json(),
            r#"{"features":["pad64"],"rustc":"rustc 1.0 \"x\"","wasmBindgen":"0.2.1","rustflags":"-C a","clockResolutionNs":41}"#
        );
    }

    #[test]
    fn unknown_clock_resolution_is_null() {
        let info = BuildInfo {
            clock_resolution_ns: None,
            ..BuildInfo::current()
        };
        assert!(info.to_json().ends_with(r#""clockResolutionNs":null}"#));
    }
}
