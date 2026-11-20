use std::process::Command;

use bench::workloads::histogram::CHUNK_BYTES;

const WIDTH: usize = 1024;
const HEIGHT: usize = 1024;
const MAX_THREADS: usize = 8;

const _: () = assert!(WIDTH * HEIGHT / CHUNK_BYTES > MAX_THREADS);

const PROBES: usize = 2;

const HISTOGRAM_KS: [&str; 4] = ["1", "4", "16", "256"];

fn run(workload: &str, input: &[&str], threads: usize) -> String {
    let output = Command::new(env!("CARGO_BIN_EXE_native"))
        .args(["--workload", workload])
        .args(input)
        .args(["--threads", &threads.to_string()])
        .args([
            "--width",
            &WIDTH.to_string(),
            "--height",
            &HEIGHT.to_string(),
            "--warmup",
            "1",
            "--iters",
            "2",
        ])
        .output()
        .expect("runner starts");
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).expect("utf-8 output")
}

fn column<'a>(csv: &'a str, name: &str) -> Vec<&'a str> {
    let mut lines = csv.lines();
    let header = lines.next().expect("header");
    let index = header
        .split(',')
        .position(|column| column == name)
        .unwrap_or_else(|| panic!("no column {name} in {header}"));
    lines
        .map(|line| line.split(',').nth(index).expect("full row"))
        .collect()
}

fn checksum(csv: &str) -> String {
    let checksums = column(csv, "checksum");
    assert!(checksums.windows(2).all(|pair| pair[0] == pair[1]));
    checksums[0].to_string()
}

#[test]
fn prints_header_and_one_row_per_iteration() {
    let csv = run(
        "hist-atomic",
        &["--input", "few", "--k", "4", "--calibration", "3"],
        2,
    );
    let mut lines = csv.lines();
    assert_eq!(lines.next(), Some(bench::results::CSV_HEADER));
    let (calibration, rows): (Vec<_>, Vec<_>) =
        lines.partition(|line| line.contains(",calibration-"));
    assert_eq!(calibration.len(), 1 + PROBES * (3 + 3));
    let probes = column(&csv, "probe");
    assert!(probes.contains(&"broadcast") && probes.contains(&"par-iter"));
    assert_eq!(rows.len(), 3);
    assert!(rows[0].starts_with(&format!(
        "native,hist-atomic,few,4,{WIDTH},{HEIGHT},24301,2,warmup,0,"
    )));
    assert!(rows[2].starts_with(&format!(
        "native,hist-atomic,few,4,{WIDTH},{HEIGHT},24301,2,measured,1,"
    )));
}

fn campaign_inputs() -> Vec<(&'static str, Vec<&'static str>)> {
    let filter = ("filter", vec!["--input", "noise"]);
    let histograms = ["hist-atomic", "hist-local"]
        .into_iter()
        .flat_map(|workload| HISTOGRAM_KS.map(|k| (workload, vec!["--input", "few", "--k", k])));
    std::iter::once(filter).chain(histograms).collect()
}

#[test]
fn checksum_is_the_same_for_every_thread_count() {
    for (workload, input) in campaign_inputs() {
        let reference = checksum(&run(workload, &input, 1));
        for threads in 2..=MAX_THREADS {
            assert_eq!(
                checksum(&run(workload, &input, threads)),
                reference,
                "{workload} {input:?} threads = {threads}"
            );
        }
    }
}

#[test]
fn both_histogram_variants_give_the_same_checksum() {
    for k in HISTOGRAM_KS {
        let input = ["--input", "few", "--k", k];
        assert_eq!(
            checksum(&run("hist-atomic", &input, 4)),
            checksum(&run("hist-local", &input, 4)),
            "k = {k}"
        );
    }
}

#[test]
fn build_info_reports_compiler_features_and_clock_resolution() {
    let output = Command::new(env!("CARGO_BIN_EXE_native"))
        .arg("--build-info")
        .output()
        .expect("runner starts");
    assert!(output.status.success());
    let json = String::from_utf8(output.stdout).expect("utf-8 output");
    assert!(json.contains(r#""rustc":"rustc "#), "{json}");
    assert!(json.contains(r#""features":["#), "{json}");
    assert!(!json.contains(r#""clockResolutionNs":null"#), "{json}");
}

#[test]
fn rejects_bad_arguments_with_a_failure_exit() {
    let status = Command::new(env!("CARGO_BIN_EXE_native"))
        .args(["--workload", "blur"])
        .output()
        .expect("runner starts")
        .status;
    assert!(!status.success());
}

#[test]
fn passes_keep_the_checksum_of_one_pass() {
    for (workload, input) in [
        ("filter", vec!["--input", "noise"]),
        ("hist-local", vec!["--input", "few", "--k", "256"]),
    ] {
        let with_passes: Vec<&str> = input.iter().copied().chain(["--passes", "3"]).collect();
        assert_eq!(
            checksum(&run(workload, &with_passes, 4)),
            checksum(&run(workload, &input, 4)),
            "{workload}"
        );
    }
}

#[test]
fn rejects_several_passes_of_the_atomic_histogram() {
    let output = Command::new(env!("CARGO_BIN_EXE_native"))
        .args(["--workload", "hist-atomic", "--input", "few", "--k", "4"])
        .args(["--threads", "1", "--width", "8", "--height", "8"])
        .args(["--warmup", "0", "--iters", "1", "--passes", "2"])
        .output()
        .expect("runner starts");
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("passes"),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
}
