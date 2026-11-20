"""How the harness talks to the Rust native runner: flags in, CSV out."""

from urllib.parse import parse_qsl

CSV_HEADER = "env,workload,input,k,width,height,seed,threads,phase,iter,ns,input_fingerprint,checksum,probe,mem_before_bytes,mem_after_bytes,input_addr_mod4096,input_addr_mod64,output_addr_mod4096,output_addr_mod64,pitch,palette,schema,passes,grain"
# The version written in the schema column of every row (bench/src/results.rs SCHEMA_VERSION).
SCHEMA_VERSION = 2
BUILD_INFO_FLAG = "--build-info"
RESERVED_KEYS = ("run", "env")


def query_to_flags(query: str) -> list[str]:
    pairs = parse_qsl(query, keep_blank_values=True)
    clashes = [key for key, _ in pairs if key in RESERVED_KEYS]
    if clashes:
        raise ValueError(f"query must not set {', '.join(clashes)}")
    return [item for key, value in pairs for item in (f"--{key}", value)]


def starts_with_header(output: str) -> bool:
    return output.split("\n", 1)[0] == CSV_HEADER
