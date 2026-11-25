"""Writes the LaTeX tables of the extended report from the committed tables.

Run from the repository root: `python3 paper/extended/make_tables.py`.
Every number of a generated table is read from `data/tables/*-v3`,
`data/probes` or `data/raw/*-v3/campaign.jsonl`; none is typed here.
"""

from __future__ import annotations

import csv
import json
import re
import statistics
from collections.abc import Callable, Iterable, Sequence
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "data" / "tables"
RAW = ROOT / "data" / "raw"
PROBES = ROOT / "data" / "probes"
OUTPUT = Path(__file__).resolve().parent / "tables"

ENVIRONMENTS = ("native", "chrome", "firefox")
BROWSERS = ("chrome", "firefox")
ENVIRONMENT_LABEL = {"native": "Native", "chrome": "Chrome", "firefox": "Firefox"}
THREADS = ("1", "2", "4", "6", "7", "8")
CONTENTION = ("1", "4", "16", "256")
NS_PER_MS = 1e6
NS_PER_US = 1e3
SHORTEST_SPAN_HOURS = 0.1

Row = dict[str, str]
Cells = Sequence[str]


def read(relative: str, base: Path = TABLES) -> list[Row]:
    with (base / relative).open(newline="") as handle:
        return list(csv.DictReader(handle))


def pick(rows: Iterable[Row], **match: str) -> Row:
    found = [row for row in rows if all(row[key] == value for key, value in match.items())]
    if len(found) != 1:
        raise LookupError(f"{len(found)} rows match {match}")
    return found[0]


def interval(row: Row, value: str, low: str, high: str) -> str:
    return f"{row[value]} [{row[low]}, {row[high]}]"


def milliseconds(nanoseconds: str) -> str:
    value = float(nanoseconds) / NS_PER_MS
    return f"{value:.1f}" if value >= 100 else f"{value:.3f}"


def microseconds(nanoseconds: str) -> str:
    return f"{float(nanoseconds) / NS_PER_US:.1f}"


def workload_label(workload: str, k: str) -> str:
    names = {
        "filter": "filter",
        "hist-atomic": "atomic",
        "hist-local": "local",
        "hist-atomic-private": "private",
        "hist-atomic-packed": "packed",
        "sort": "sort",
        "sort-unstable": "sort-unstable",
        "filter-seq": "filter-seq",
        "hist-seq": "hist-seq",
    }
    name = names[workload]
    return f"{name}, $k$={k}" if k else name


def escape(text: str) -> str:
    return text.replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def render(
    name: str,
    caption: str,
    columns: str,
    header: Sequence[Cells],
    body: Sequence[Cells],
    long: bool = False,
    size: str = r"\small",
    fit: bool = False,
) -> None:
    """One file per table: a `table` float, or a `longtable` that may break across pages.

    `fit` scales a table float that is wider than the text down to the text width.
    """
    head = [" & ".join(line) + r" \\" for line in header]
    lines = [" & ".join(cells) + r" \\" if cells else r"\midrule" for cells in body]
    label = rf"\label{{tab:{name}}}"
    if long:
        text = [
            "{" + size,
            rf"\begin{{longtable}}{{{columns}}}",
            rf"\caption{{{caption}}}{label} \\",
            r"\toprule",
            *head,
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            *head,
            r"\midrule",
            r"\endhead",
            r"\bottomrule",
            r"\endfoot",
            *lines,
            r"\end{longtable}",
            "}",
        ]
    else:
        text = [
            r"\begin{table}[htbp]",
            rf"\caption{{{caption}}}{label}",
            r"\centering" + size,
            *([r"\resizebox{\linewidth}{!}{%"] if fit else []),
            rf"\begin{{tabular}}{{{columns}}}",
            r"\toprule",
            *head,
            r"\midrule",
            *lines,
            r"\bottomrule",
            r"\end{tabular}",
            *(["}"] if fit else []),
            r"\end{table}",
        ]
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / f"{name}.tex").write_text("\n".join(text) + "\n")


def configurations(rows: Iterable[Row]) -> list[tuple[str, str]]:
    """The (workload, k) pairs of a table, filter first, then by workload and numeric k."""
    seen = {(row["workload"], row["k"]) for row in rows}
    return sorted(seen, key=lambda pair: (pair[0] != "filter", pair[0], int(pair[1] or 0)))


def grouped(
    rows: list[Row],
    cells: Callable[[str, str, str], Cells],
    threads: Sequence[str] = THREADS,
) -> list[Cells]:
    """One block of lines per configuration, one line per thread count, a rule between blocks."""
    body: list[Cells] = []
    for workload, k in configurations(rows):
        if body:
            body.append(())
        for n in threads:
            body.append((workload_label(workload, k), n, *cells(workload, k, n)))
    return body


def scaling_tables() -> None:
    rows = read("campaign-v3/campaign-v3-scaling.csv")

    def per_environment(value: str) -> Callable[[str, str, str], Cells]:
        def cells(workload: str, k: str, n: str) -> Cells:
            return [
                interval(
                    pick(rows, environment=env, workload=workload, k=k, threads=n),
                    value,
                    f"{value}_low",
                    f"{value}_high",
                )
                for env in ENVIRONMENTS
            ]

        return cells

    header = [("Workload", "$N$", *(ENVIRONMENT_LABEL[env] for env in ENVIRONMENTS))]
    render(
        "speedup",
        "Main campaign: relative speedup $T_1/T_N$ with its 95\\,\\% bootstrap interval "
        "(30 runs per cell, geometric mean of the per-run medians).",
        "llccc",
        header,
        grouped(rows, per_environment("speedup")),
        long=True,
    )
    render(
        "efficiency",
        "Main campaign: efficiency $S_N/N$ with its 95\\,\\% bootstrap interval.",
        "llccc",
        header,
        grouped(rows, per_environment("efficiency")),
        long=True,
    )

    def times(workload: str, k: str, n: str) -> Cells:
        return [
            milliseconds(pick(rows, environment=env, workload=workload, k=k, threads=n)["center_ns"])
            for env in ENVIRONMENTS
        ]

    render(
        "times",
        "Main campaign: time of one iteration in ms (geometric mean over 30 runs of the per-run "
        "median of 10 measured iterations).",
        "llrrr",
        header,
        grouped(rows, times),
        long=True,
    )


def contrast_tables() -> None:
    rows = read("campaign-v3/campaign-v3-contrasts.csv")

    def question(name: str) -> Callable[[str, str, str], Cells]:
        def cells(workload: str, k: str, n: str) -> Cells:
            return [
                interval(
                    pick(rows, question=name, environment=env, workload=workload, k=k, threads=n),
                    "effect",
                    "low",
                    "high",
                )
                for env in BROWSERS
            ]

        return cells

    header = [("Workload", "$N$", "Chrome", "Firefox")]
    absolute = [row for row in rows if row["question"] == "ABS"]
    render(
        "absolute",
        "Main campaign: time in the browser over the native time at the same $N$, with its "
        "95\\,\\% bootstrap interval (exploratory).",
        "llcc",
        header,
        grouped(absolute, question("ABS")),
        long=True,
    )
    rq1 = [row for row in rows if row["question"] == "RQ1"]
    render(
        "rq1-ratios",
        "Main campaign: speedup in the browser over the native speedup, with its 95\\,\\% "
        "bootstrap interval. Only the filter at $N=8$ is primary; the rest is exploratory.",
        "llcc",
        header,
        grouped(rq1, question("RQ1"), threads=THREADS[1:]),
        long=True,
    )

    def rq2(k: str, n: str) -> Cells:
        return [
            interval(
                pick(rows, question="RQ2", environment=env, k=k, threads=n), "effect", "low", "high"
            )
            for env in BROWSERS
        ]

    body: list[Cells] = []
    for k in CONTENTION:
        if body:
            body.append(())
        body.extend((k, n, *rq2(k, n)) for n in THREADS)
    render(
        "rq2-all",
        "Main campaign: the RQ2 effect $\\exp(\\Delta r)$ for every $k$ and $N$, with its "
        "95\\,\\% bootstrap interval. Only $N=8$ is primary.",
        "llcc",
        [("$k$", "$N$", "Chrome", "Firefox")],
        body,
    )

    primary = [row for row in rows if row["primary"] == "yes"]
    primary.sort(key=lambda row: (row["question"] != "RQ1", row["environment"], int(row["k"] or 0)))
    render(
        "primary",
        "The ten primary contrasts at $N=8$: effect, 95\\,\\% interval, Bonferroni 99.5\\,\\% "
        "interval, bootstrap $p$, Holm-adjusted $p$ and the decision at $\\alpha=0.05$.",
        "lllccrrl",
        [("RQ", "Browser", "Cell", "Effect [95\\,\\%]", "[99.5\\,\\%]", "$p$", "Holm $p$", "Rejected")],
        [
            (
                row["question"],
                ENVIRONMENT_LABEL[row["environment"]],
                workload_label(row["workload"], row["k"]),
                interval(row, "effect", "low", "high"),
                f"[{row['primary_low']}, {row['primary_high']}]",
                row["p"],
                row["holm_p"],
                row["rejected"],
            )
            for row in primary
        ],
        size=r"\footnotesize",
    )


def decomposition_table() -> None:
    rows = read("campaign-v3/campaign-v3-rq2-decomposition.csv")

    def quantity(env: str, k: str, name: str) -> str:
        return interval(pick(rows, environment=env, k=k, quantity=name), "ratio", "low", "high")

    render(
        "decomposition",
        "The two factors of each primary RQ2 ratio at $N=8$ (post hoc, 95\\,\\% intervals): "
        "the atomic time and the local time in the browser over native, and the ratio of the "
        "excesses $(A_b-L_b)/(A_n-L_n)$.",
        "llcccc",
        [("Browser", "$k$", "$\\exp(\\Delta r)$", "Atomic $A_b/A_n$", "Local $L_b/L_n$", "Excess")],
        [
            (
                ENVIRONMENT_LABEL[env],
                k,
                *(quantity(env, k, name) for name in ("rq2", "atomic", "local", "excess")),
            )
            for env in BROWSERS
            for k in CONTENTION
        ],
        size=r"\footnotesize",
    )


def robustness_tables() -> None:
    rows = read("campaign-v3/campaign-v3-robustness.csv")
    render(
        "robustness",
        "Robustness of the ten primary contrasts: Mann-Whitney $U$ and Cliff's $\\delta$ on "
        "per-run ratios, Holm-adjusted, the share of 1000 random re-pairings with the same "
        "decision, and the agreement with the bootstrap decision.",
        "lllrrrrlrl",
        [("RQ", "Browser", "Cell", "$\\delta$", "$U$", "$p$", "Holm $p$", "Rej.", "Share", "Agree")],
        [
            (
                row["question"],
                ENVIRONMENT_LABEL[row["environment"]],
                workload_label(row["workload"], row["k"]),
                row["cliffs_delta"],
                row["u"],
                row["p"],
                row["holm_p"],
                row["rejected"],
                row["same_decision_share"],
                row["agree"],
            )
            for row in rows
        ],
        size=r"\footnotesize",
    )
    checks = read("campaign-v3/campaign-v3-sensitivity.csv")

    def check(row: Row, name: str) -> str:
        low, high = row[f"{name}_primary_low"], row[f"{name}_primary_high"]
        return f"{row[f'{name}_effect']} [{low}, {high}]"

    render(
        "sensitivity",
        "The plan's sensitivity checks on the ten primary contrasts (effect with its 99.5\\,\\% "
        "interval): as planned, with the per-run mean, with the median across runs, and with no "
        "foreign-CPU exclusion. A decision that changes under a check would be marked not robust.",
        "llcccl",
        [("Browser", "Cell", "As planned", "Per-run mean", "Median centre", "Robust")],
        [
            (
                ENVIRONMENT_LABEL[row["environment"]],
                workload_label(row["workload"], row["k"]),
                check(row, "primary"),
                check(row, "summary_mean"),
                check(row, "center_median"),
                row["robust"],
            )
            for row in checks
        ],
        size=r"\footnotesize",
    )


def sequential_table() -> None:
    rows = read("campaign-v3/campaign-v3-sequential.csv")
    parallel = [row for row in rows if row["workload"] != "hist-atomic"]

    def cells(workload: str, k: str) -> Cells:
        out: list[str] = []
        for env in ENVIRONMENTS:
            one = pick(parallel, environment=env, workload=workload, k=k, threads="1")
            eight = pick(parallel, environment=env, workload=workload, k=k, threads="8")
            out.append(milliseconds(one["sequential_ns"]))
            out.append(interval(one, "speedup_vs_sequential", "low", "high"))
            out.append(eight["speedup_vs_sequential"])
        return out

    header = [
        ("", *(rf"\multicolumn{{3}}{{c}}{{{ENVIRONMENT_LABEL[env]}}}" for env in ENVIRONMENTS)),
        ("Workload", *("$T_{seq}$", "$T_{seq}/T_1$", "$T_{seq}/T_8$") * 3),
    ]
    render(
        "sequential",
        "Sequential references: time of the kernel without Rayon in ms, the pool of one thread "
        "against it ($T_{seq}/T_1$ with its 95\\,\\% interval; 1 means the pool costs nothing), "
        "and the speedup of eight threads against it.",
        "l" + "rcr" * 3,
        header,
        [(workload_label(w, k), *cells(w, k)) for w, k in configurations(parallel)],
        size=r"\scriptsize",
        fit=True,
    )


def throughput_table() -> None:
    rows = read("campaign-v3/campaign-v3-throughput.csv")

    def cells(workload: str, k: str, n: str) -> Cells:
        out: list[str] = []
        for env in ENVIRONMENTS:
            row = pick(rows, environment=env, workload=workload, k=k, threads=n)
            out.extend((row["ns_per_pixel"], row["absolute_speedup"]))
        return out

    header = [
        ("", "", *(rf"\multicolumn{{2}}{{c}}{{{ENVIRONMENT_LABEL[env]}}}" for env in ENVIRONMENTS)),
        ("Workload", "$N$", *("ns/px", "abs.\\ $S$") * 3),
    ]
    render(
        "throughput",
        "Throughput: nanoseconds per pixel and the absolute speedup "
        "$T(\\mathrm{native},1)/T(\\mathrm{environment},N)$ at $N=1$ and 8.",
        "ll" + "rr" * 3,
        header,
        grouped(rows, cells, threads=("1", "8")),
        long=True,
    )


def fork_join_table() -> None:
    rows = [row for row in read("campaign-v3/campaign-v3-fork-join.csv") if row["workload"] == "all"]

    def cells(probe: str, phase: str, n: str) -> Cells:
        out: list[str] = []
        for env in ENVIRONMENTS:
            row = pick(rows, environment=env, threads=n, probe=probe, phase=phase)
            out.extend((row["median_of_run_medians_us"], row["mean_of_run_means_us"]))
        return out

    body: list[Cells] = []
    for probe in ("broadcast", "par-iter"):
        for phase in ("warm", "cold"):
            if body:
                body.append(())
            body.extend((probe, phase, n, *cells(probe, phase, n)) for n in THREADS)
    header = [
        ("", "", "", *(rf"\multicolumn{{2}}{{c}}{{{ENVIRONMENT_LABEL[e]}}}" for e in ENVIRONMENTS)),
        ("Probe", "Phase", "$N$", *("median", "mean") * 3),
    ]
    render(
        "fork-join",
        "Fork-join calibration of the main campaign in \\textmu s, over the 270 runs of each "
        "environment and $N$: the median over runs of the per-run median, and the mean of the "
        "per-run means, of 20 empty regions. Warm: back to back; cold: after a pause that lets "
        "the workers sleep.",
        "lll" + "rr" * 3,
        header,
        body,
        long=True,
    )


def karp_flatt_table() -> None:
    rows = read("campaign-v3/campaign-v3-karp-flatt.csv")
    kept = [row for row in rows if row["workload"] != "hist-atomic"]

    def cells(workload: str, k: str, n: str) -> Cells:
        return [
            interval(
                pick(kept, environment=env, workload=workload, k=k, threads=n),
                "serial_fraction",
                "serial_fraction_low",
                "serial_fraction_high",
            )
            for env in ENVIRONMENTS
        ]

    render(
        "karp-flatt",
        "Karp-Flatt experimentally determined serial fraction "
        "$e=(1/S-1/N)/(1-1/N)$ with its 95\\,\\% interval, for the workloads without shared "
        "counters.",
        "llccc",
        [("Workload", "$N$", *(ENVIRONMENT_LABEL[env] for env in ENVIRONMENTS))],
        grouped(kept, cells, threads=("2", "4", "8")),
        long=True,
    )


def distributions_table() -> None:
    rows = read("campaign-v3/campaign-v3-distributions.csv")
    render(
        "distributions",
        "Spread of the 30 per-run values of the cells behind the primary contrasts' ends: "
        "quartiles in ms, interquartile range over the median, and the slowest run over the median.",
        "lllrrrrrrr",
        [("Environment", "Workload", "$N$", "min", "Q1", "median", "Q3", "max", "IQR/med.", "max/med.")],
        [
            (
                ENVIRONMENT_LABEL[row["environment"]],
                workload_label(row["workload"], row["k"]),
                row["threads"],
                row["min_ms"],
                row["q1_ms"],
                row["median_ms"],
                row["q3_ms"],
                row["max_ms"],
                row["iqr_over_median"],
                row["max_over_median"],
            )
            for row in rows
        ],
        size=r"\footnotesize",
        fit=True,
    )


def core_split_table() -> None:
    rows = [
        row
        for row in read("campaign-v3/campaign-v3-core-split.csv")
        if row["workload"] in ("filter", "filter-seq")
    ]
    render(
        "core-split",
        "One-thread filter runs of the main campaign split by the CPU with the most busy time: "
        "runs, their median and slowest run over the configuration's median, and that CPU's "
        "share of the run's busy time. CPU 12 is the degraded core.",
        "llrrrrr",
        [("Environment", "Workload", "CPU", "Runs", "Median", "Max", "Busy share")],
        [
            (
                ENVIRONMENT_LABEL[row["environment"]],
                workload_label(row["workload"], row["k"]),
                row["cpu"],
                row["runs"],
                row["median_over_configuration"],
                row["max_over_configuration"],
                row["median_busy_share"],
            )
            for row in rows
        ],
    )


CAMPAIGN_TABLES = {
    "campaign-v3": "campaign-v3",
    "tier-v3": "tier-v3",
    "perf-v3": "perf-v3",
    "simd-scalar-v3": "simd-v3",
    "simd-avx2-v3": "simd-v3",
    "cutoff-512-v3": "cutoff-v3",
    "cutoff-1024-v3": "cutoff-v3",
    "cutoff-2048-v3": "cutoff-v3",
    "cutoff-4096-v3": "cutoff-v3",
    "cutoff-8192-v3": "cutoff-v3",
    "cutoff-control-512-v3": "cutoff-v3",
    "cutoff-control-2048-v3": "cutoff-v3",
    "grain-threads-v3": "grain-threads-v3",
    "grain-1024-v3": "grain-v3",
    "grain-8192-v3": "grain-v3",
    "weak-v3": "weak-v3",
    "extras-v3": "extras-v3",
    "hybrid-v3": "hybrid-v3",
}
UNCHECKED_CAMPAIGNS = ("perf-loop1-v3", "perf-loop8-v3")


def journal(campaign: str) -> tuple[int, float, str]:
    """Planned runs logged in a campaign's journal, its span in hours and its first day."""
    stamps: list[datetime] = []
    with (RAW / campaign / "campaign.jsonl").open() as handle:
        for line in handle:
            entry = json.loads(line)
            if not entry.get("discarded"):
                stamps.append(datetime.fromisoformat(entry["loggedAt"]))
    hours = (max(stamps) - min(stamps)).total_seconds() / 3600
    return len(stamps), hours, min(stamps).date().isoformat()


def span(hours: float) -> str:
    return f"{hours:.1f}" if hours >= SHORTEST_SPAN_HOURS else f"<{SHORTEST_SPAN_HOURS}"


def quality_table() -> None:
    def first_number(text: str, pattern: str) -> str:
        found = re.search(pattern, text)
        if found is None:
            raise LookupError(pattern)
        return found.group(1)

    body: list[Cells] = []
    for campaign, folder in CAMPAIGN_TABLES.items():
        report = (TABLES / folder / f"{campaign}-quality.md").read_text()
        _, hours, day = journal(campaign)
        body.append(
            (
                escape(campaign.removesuffix("-v3")),
                day,
                span(hours),
                first_number(report, r"Runs done: (\d+)"),
                first_number(report, r"missing: (\d+)"),
                first_number(report, r"failed: (\d+)"),
                first_number(report, r"Checksum conflicts: (\d+)"),
                first_number(report, r"strict validation: (\d+)"),
                first_number(report, r"foreign CPU threshold \(0\.25 s\): (\d+)"),
                first_number(report, r"clock resolution: (\d+)"),
                first_number(report, r"at least 10 runs\): (\d+)"),
            )
        )
    for campaign in UNCHECKED_CAMPAIGNS:
        runs, hours, day = journal(campaign)
        body.append((escape(campaign.removesuffix("-v3")), day, span(hours), str(runs), *["-"] * 7))
    render(
        "quality",
        "Data quality of every campaign of \\texttt{measured/v3}, from each campaign's data "
        "check: first day and span of the journal in hours, runs done, missing, failed, checksum "
        "conflicts, runs failing strict validation, runs above the foreign-CPU threshold, "
        "configurations under 100 clock ticks, and configurations that trend with the execution "
        "order ($|\\rho|>0.5$). The grain campaigns pool every grain of a configuration, so "
        "their trend count mixes grains. The two counter campaigns of the loop have no data "
        "check report; their run count is that of the journal.",
        "llrrrrrrrrr",
        [("Campaign", "Start", "Hours", "Runs", "Miss.", "Fail.", "Chk.", "Strict", "CPU", "Clock", "Trend")],
        body,
        size=r"\footnotesize",
    )


def tier_table() -> None:
    rows = read("tier-v3/tier-v3-arms.csv")
    arms = {"native": ("-",), "chrome": ("default", "optimizing", "baseline")}
    arms["firefox"] = arms["chrome"]
    body: list[Cells] = []
    for workload, k in configurations(rows):
        if body:
            body.append(())
        for env in ENVIRONMENTS:
            for arm in arms[env]:
                one = pick(rows, environment=env, workload=workload, k=k, threads="1", variant=arm)
                eight = pick(rows, environment=env, workload=workload, k=k, threads="8", variant=arm)
                body.append(
                    (
                        workload_label(workload, k),
                        ENVIRONMENT_LABEL[env],
                        "" if arm == "-" else arm,
                        milliseconds(one["center_ns"]),
                        milliseconds(eight["center_ns"]),
                        interval(eight, "speedup", "speedup_low", "speedup_high"),
                        one["first_warmup_over_value"],
                    )
                )
    render(
        "tier",
        "Engine arms (tier campaign, 2100 runs): each browser as shipped (default), with its "
        "optimizing compiler only and with its baseline compiler only. Time in ms at $N=1$ and 8, "
        "speedup at $N=8$ with its 95\\,\\% interval, and the first warm-up iteration over the "
        "run's value at $N=1$.",
        "lllrrcr",
        [("Workload", "Environment", "Arm", "$T_1$", "$T_8$", "$S_8$ [95\\,\\%]", "First it.")],
        body,
        long=True,
    )


def probe_table() -> None:
    rows = read("atomic-increment/passes.csv", base=PROBES)
    sequences = ("lock-inc", "compare-and-swap", "lock-xadd", "lock-inc-checked", "lock-xadd-checked")
    cells = [(k, n) for k in ("1", "16", "256") for n in ("1", "8")]

    def median(sequence: str, k: str, n: str) -> str:
        passes = [
            float(row["ns"])
            for row in rows
            if (row["sequence"], row["k"], row["threads"]) == (sequence, k, n)
        ]
        return f"{statistics.median(passes) / NS_PER_MS:.1f}"

    render(
        "probe",
        "Native atomic-increment probe: median time of a pass in ms over 10 timed passes, by "
        "increment sequence. Only the instructions of the increment change between rows.",
        "l" + "r" * len(cells),
        [("Sequence", *(f"$k$={k}, $N$={n}" for k, n in cells))],
        [(rf"\texttt{{{seq}}}", *(median(seq, k, n) for k, n in cells)) for seq in sequences],
    )


def counter_tables() -> None:
    rows = [row for row in read("perf-v3/perf-v3-counters.csv") if row["workload"] == "hist-atomic"]
    counters = ("cycles", "instructions", "lock_loads", "rfo_hitm", "read_hitm", "l2_misses")
    body: list[Cells] = []
    for k in ("1", "256"):
        for n in ("1", "8"):
            if body:
                body.append(())
            for env in ENVIRONMENTS:
                values = [
                    pick(rows, environment=env, k=k, threads=n, counter=counter)["mean"]
                    for counter in counters
                ]
                body.append((k, n, ENVIRONMENT_LABEL[env], *values))
    render(
        "counters-atomic",
        "Hardware counters of the atomic histogram per atomic add (means of 30 runs, counted "
        "system-wide on the P-cores for the whole run): cycles, instructions, locked loads, lines "
        "taken for writing from another core (RFO HITM), lines read from another core (read "
        "HITM) and L2 misses.",
        "lllrrrrrr",
        [("$k$", "$N$", "Environment", "Cycles", "Instr.", "Lock loads", "RFO HITM", "Read HITM", "L2 miss.")],
        body,
    )
    retries = read("perf-v3/perf-v3-retries.csv")
    render(
        "retries",
        "Locked loads per operation at $N=8$ above the one-thread count, with its 95\\,\\% "
        "interval. For the atomic histogram in Chrome each is a retried compare-and-swap.",
        "llccc",
        [("Workload", "", *(ENVIRONMENT_LABEL[env] for env in ENVIRONMENTS))],
        [
            (
                workload_label(workload, k),
                "",
                *(
                    interval(
                        pick(retries, environment=env, workload=workload, k=k),
                        "excess_lock_loads",
                        "low",
                        "high",
                    )
                    for env in ENVIRONMENTS
                ),
            )
            for workload, k in configurations(retries)
        ],
    )

    loop = read("perf-loop-v3/perf-loop-v3-counters.csv")
    rises = read("perf-loop-v3/perf-loop-v3-rises.csv")
    shown = ("instructions", "cycles", "llc_misses", "l2_misses")
    body = []
    for workload, k in configurations(loop):
        if body:
            body.append(())
        for env in ENVIRONMENTS:
            one = [
                pick(loop, environment=env, workload=workload, k=k, threads="1", counter=c)["per_pixel"]
                for c in shown
            ]
            rise = [
                interval(
                    pick(rises, environment=env, workload=workload, k=k, counter=c),
                    "over_one_thread",
                    "low",
                    "high",
                )
                for c in ("instructions", "cycles", "llc_misses", "l2_misses")
            ]
            body.append((workload_label(workload, k), ENVIRONMENT_LABEL[env], *one, *rise))
    header = [
        ("", "", r"\multicolumn{4}{c}{Per pixel at $N=1$}", r"\multicolumn{4}{c}{$N=8$ over $N=1$ [95\,\%]}"),
        ("Workload", "Env.", "Instr.", "Cycles", "LLC", "L2", "Instr.", "Cycles", "LLC", "L2"),
    ]
    render(
        "counters-loop",
        "Counters of the loop alone, by the difference of two pass counts (10 runs with one "
        "pass and 10 with eight): per pixel at one thread, and the ratio of eight threads to one "
        "with its 95\\,\\% bootstrap interval. LLC and L2 are cache misses.",
        "ll" + "r" * 4 + "c" * 4,
        header,
        body,
        size=r"\scriptsize",
        fit=True,
    )


def simd_table() -> None:
    rows = read("simd-v3/simd-v3-variants.csv")
    order = [("scalar", env) for env in ENVIRONMENTS]
    order += [("baseline", env) for env in ENVIRONMENTS] + [("avx2", "native")]
    megabytes = 8192 * 8192 / 1e6
    body: list[Cells] = []
    for build, env in order:
        one = pick(rows, build=build, environment=env, threads="1")
        eight = pick(rows, build=build, environment=env, threads="8")
        rate = megabytes / (float(one["center_ns"]) / 1e9)
        body.append(
            (
                build,
                ENVIRONMENT_LABEL[env],
                milliseconds(one["center_ns"]),
                milliseconds(eight["center_ns"]),
                f"{rate:.0f}",
                interval(eight, "efficiency", "efficiency_low", "efficiency_high"),
                microseconds(eight["excess_ns"]),
                one["over_native"],
                eight["over_native"],
            )
        )
    render(
        "simd",
        "SIMD variants of the filter: time in ms at $N=1$ and 8, megabytes read per second by "
        "one thread, efficiency at $N=8$ with its 95\\,\\% interval, the excess "
        "$T_8-T_1/8$ in \\textmu s, and the time over native of the same build at $N=1$ and 8.",
        "llrrrcrrr",
        [("Build", "Environment", "$T_1$", "$T_8$", "MB/s", "Eff.\\ $N$=8", "Excess", "/nat.\\ 1", "/nat.\\ 8")],
        body,
        size=r"\footnotesize",
    )


def cutoff_tables() -> None:
    rows = read("cutoff-v3/cutoff-table.csv")
    sides = ("512", "1024", "2048", "4096", "8192")
    body: list[Cells] = []
    for workload, k in configurations(rows):
        for n in ("2", "4", "8"):
            if body and n == "2":
                body.append(())
            for env in ENVIRONMENTS:
                cells = [
                    pick(rows, environment=env, workload=workload, k=k, threads=n, side=side)
                    for side in sides
                ]
                body.append(
                    (
                        workload_label(workload, k),
                        n,
                        ENVIRONMENT_LABEL[env],
                        *(f"{cell['speedup']} ({cell['efficiency']})" for cell in cells),
                    )
                )
    render(
        "cutoff",
        "Cutoff campaigns: speedup (efficiency) by image side, with repeated passes per timed "
        "sample so that small images clear the clock.",
        "lll" + "c" * len(sides),
        [("Workload", "$N$", "Environment", *(f"{side}$^2$" for side in sides))],
        body,
        size=r"\footnotesize",
    )
    estimates = [row for row in read("cutoff-v3/cutoff-estimates.csv") if row["placement"] == "crossed"]
    model = read("cutoff-v3/cutoff-model.csv")
    body = []
    for row in estimates:
        fit = pick(model, environment=row["environment"], workload=row["workload"], k=row["k"])
        body.append(
            (
                workload_label(row["workload"], row["k"]),
                ENVIRONMENT_LABEL[row["environment"]],
                f"{row['side']} [{row['side_low']}, {row['side_high']}]",
                row["work_us"],
                fit["fork_join_us"],
                fit["model_worth_it_us"],
                fit["side_1pct"],
                fit["side_5pct"],
            )
        )
    render(
        "cutoff-estimates",
        "Cutoff at $N=8$: the image side at which the efficiency crosses 0.5 (interpolated, "
        "95\\,\\% interval) and the sequential work of that image in \\textmu s; then the "
        "fork-join model $T_N=W/N+F$ with this campaign's warm fork-join $F$ in \\textmu s: "
        "the work it predicts for efficiency 0.5, and the side at which $F$ is 1\\,\\% and "
        "5\\,\\% of $T_N$.",
        "llcrrrrr",
        [("Workload", "Environment", "Side at 0.5", "Work", "$F$", "Model", "Side 1\\,\\%", "Side 5\\,\\%")],
        body,
        size=r"\footnotesize",
    )


def grain_tables() -> None:
    best = read("grain-v3/grain-best.csv")
    render(
        "grain-best",
        "Grain sweeps at $N=8$: the best fixed grain (rows for the filter, KB for the "
        "histograms), its time per pass in \\textmu s, the flat region (grains whose interval "
        "overlaps the best), Rayon's adaptive split over the best, and the cost of one task in ns "
        "with its 95\\,\\% interval.",
        "lllrrcrc",
        [("Side", "Workload", "Environment", "Best", "Time", "Flat", "Adaptive", "Task cost")],
        [
            (
                f"{row['side']}$^2$",
                workload_label(row["workload"], row["k"]),
                ENVIRONMENT_LABEL[row["environment"]],
                row["best_grain"],
                row["best_us"],
                f"{row['flat_from']} to {row['flat_to']}",
                row["adaptive_over_best"],
                f"{row['task_cost_ns']} [{row['task_cost_low_ns']}, {row['task_cost_high_ns']}]"
                if row["task_cost_ns"]
                else "-",
            )
            for row in sorted(best, key=lambda r: (int(r["side"]), r["workload"], r["environment"]))
        ],
        size=r"\footnotesize",
    )
    threads = read("grain-threads-v3/grain-threads-v3-grains.csv")
    variants = ("adaptive", "256", "1024")
    body: list[Cells] = []
    for env in ENVIRONMENTS:
        if body:
            body.append(())
        for variant in variants:
            cells: list[str] = []
            for n in ("1", "6", "7", "8"):
                row = pick(threads, environment=env, variant=variant, threads=n)
                cells.append(milliseconds(row["center_ns"]))
                if n != "1":
                    cells.append(row["efficiency"])
            body.append((ENVIRONMENT_LABEL[env], variant if variant == "adaptive" else f"{variant} KB", *cells))
    render(
        "grain-threads",
        "Grain by threads: the local histogram at $k=16$ with Rayon's adaptive split and two "
        "fixed grains. Time in ms and efficiency against the one-thread run of the same grain.",
        "llrrrrrrr",
        [("Environment", "Grain", "$T_1$", "$T_6$", "$E_6$", "$T_7$", "$E_7$", "$T_8$", "$E_8$")],
        body,
    )


def extras_tables() -> None:
    rows = read("extras-v3/extras-v3-scaling.csv")
    body: list[Cells] = []
    last = ""
    for workload, k in sorted(configurations(rows), key=lambda pair: (pair[1] == "", int(pair[1] or 0))):
        if body and k != last:
            body.append(())
        last = k
        native = pick(rows, environment="native", workload=workload, k=k, threads="8")
        cells: list[str] = []
        for env in ENVIRONMENTS:
            one = pick(rows, environment=env, workload=workload, k=k, threads="1")
            eight = pick(rows, environment=env, workload=workload, k=k, threads="8")
            cells.extend((milliseconds(one["center_ns"]), milliseconds(eight["center_ns"])))
            cells.append(interval(eight, "speedup", "speedup_low", "speedup_high"))
            if env != "native":
                cells.append(f"{float(eight['center_ns']) / float(native['center_ns']):.2f}")
        body.append((workload_label(workload, k), *cells))
    header = [
        (
            "",
            r"\multicolumn{3}{c}{Native}",
            r"\multicolumn{4}{c}{Chrome}",
            r"\multicolumn{4}{c}{Firefox}",
        ),
        ("Workload", "$T_1$", "$T_8$", "$S_8$", *("$T_1$", "$T_8$", "$S_8$", "/nat.") * 2),
    ]
    render(
        "extras",
        "Extras campaign (5400 runs): time in ms at $N=1$ and 8, speedup at $N=8$ with its "
        "95\\,\\% interval, and the time at $N=8$ over the native one.",
        "l" + "rrc" + "rrcr" * 2,
        header,
        body,
        size=r"\scriptsize",
        fit=True,
    )

    weak = read("weak-v3/weak-v3-scaling.csv")

    def weak_cells(workload: str, k: str, n: str) -> Cells:
        out: list[str] = []
        for env in ENVIRONMENTS:
            row = pick(weak, environment=env, workload=workload, k=k, threads=n)
            out.append(milliseconds(row["center_ns"]))
            out.append(interval(row, "weak_efficiency", "weak_efficiency_low", "weak_efficiency_high"))
        return out

    render(
        "weak",
        "Weak scaling (1080 runs): the image is 8192 pixels wide and $1024N$ rows high. Time "
        "in ms and weak efficiency $T_1/T_N$ with its 95\\,\\% interval.",
        "ll" + "rc" * 3,
        [
            ("", "", *(rf"\multicolumn{{2}}{{c}}{{{ENVIRONMENT_LABEL[e]}}}" for e in ENVIRONMENTS)),
            ("Workload", "$N$", *("$T_N$", "$T_1/T_N$") * 3),
        ],
        grouped(weak, weak_cells),
        size=r"\footnotesize",
    )

    hybrid = read("hybrid-v3/hybrid-v3-scaling.csv")

    def hybrid_cells(workload: str, k: str, n: str) -> Cells:
        out: list[str] = []
        for env in ENVIRONMENTS:
            row = pick(hybrid, environment=env, workload=workload, k=k, threads=n)
            out.append(milliseconds(row["center_ns"]))
            out.append(interval(row, "speedup", "speedup_low", "speedup_high"))
        return out

    render(
        "hybrid",
        "Hybrid campaign (900 runs): 8 P-cores and 12 E-cores in the mask. Time in ms and "
        "speedup $T_1/T_N$ with its 95\\,\\% interval.",
        "ll" + "rc" * 3,
        [
            ("", "", *(rf"\multicolumn{{2}}{{c}}{{{ENVIRONMENT_LABEL[e]}}}" for e in ENVIRONMENTS)),
            ("Workload", "$N$", *("$T_N$", "$S_N$") * 3),
        ],
        grouped(hybrid, hybrid_cells, threads=("1", "8", "12", "16", "20")),
        size=r"\footnotesize",
        fit=True,
    )


def main() -> None:
    scaling_tables()
    contrast_tables()
    decomposition_table()
    robustness_tables()
    sequential_table()
    throughput_table()
    fork_join_table()
    karp_flatt_table()
    distributions_table()
    core_split_table()
    quality_table()
    tier_table()
    probe_table()
    counter_tables()
    simd_table()
    cutoff_tables()
    grain_tables()
    extras_tables()


if __name__ == "__main__":
    main()
