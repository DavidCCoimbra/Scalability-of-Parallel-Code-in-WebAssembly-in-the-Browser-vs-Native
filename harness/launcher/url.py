"""The URL that tells the benchmark page what to run."""

from urllib.parse import parse_qs

from harness.server import HOST

PAGE = "index.html"
RESERVED_KEYS = ("run", "env", "startDelayMs")


def run_url(port: int, run_id: str, environment: str, query: str, start_delay_ms: int) -> str:
    clashes = [key for key in RESERVED_KEYS if key in parse_qs(query, keep_blank_values=True)]
    if clashes:
        raise ValueError(f"query must not set {', '.join(clashes)}; the launcher sets them")
    return f"http://{HOST}:{port}/{PAGE}?run={run_id}&env={environment}&startDelayMs={start_delay_ms}&{query}"
