use std::env;
use std::fs;
use std::process::Command;

fn main() {
    let rustc = env::var("RUSTC").unwrap_or_else(|_| "rustc".into());
    let version = Command::new(rustc)
        .arg("-V")
        .output()
        .ok()
        .and_then(|output| String::from_utf8(output.stdout).ok())
        .map(|text| text.trim().to_string())
        .unwrap_or_else(|| "unavailable".into());
    let rustflags = env::var("CARGO_ENCODED_RUSTFLAGS")
        .map(|flags| flags.replace('\x1f', " "))
        .unwrap_or_default();
    println!("cargo:rustc-env=BENCH_RUSTC_VERSION={version}");
    println!(
        "cargo:rustc-env=BENCH_WASM_BINDGEN_VERSION={}",
        locked_version("wasm-bindgen")
    );
    println!("cargo:rustc-env=BENCH_RUSTFLAGS={rustflags}");
    println!("cargo:rerun-if-env-changed=CARGO_ENCODED_RUSTFLAGS");
    println!("cargo:rerun-if-env-changed=RUSTC");
    println!("cargo:rerun-if-changed=Cargo.lock");
}

fn locked_version(package: &str) -> String {
    let lock = fs::read_to_string("Cargo.lock").unwrap_or_default();
    let name = format!("name = \"{package}\"");
    let mut lines = lock.lines();
    lines
        .find(|line| *line == name)
        .and_then(|_| lines.next())
        .and_then(|line| line.strip_prefix("version = \""))
        .and_then(|rest| rest.strip_suffix('"'))
        .unwrap_or("unavailable")
        .to_string()
}
