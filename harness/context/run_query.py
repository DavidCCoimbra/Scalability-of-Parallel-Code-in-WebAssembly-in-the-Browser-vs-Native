"""What the harness reads back from a run's query string."""

from urllib.parse import parse_qs

DEFAULT_PASSES = 1
PASSES_KEY = "passes"
GRAIN_KEY = "grain"


def passes_of_query(query: str) -> int:
    values = parse_qs(query).get(PASSES_KEY)
    return DEFAULT_PASSES if not values else int(values[-1])


# No grain means Rayon's adaptive split, the task size of every campaign before the grain sweep.
def grain_of_query(query: str) -> int | None:
    values = parse_qs(query).get(GRAIN_KEY)
    return None if not values else int(values[-1])
