import statistics

from analysis.pilot.warmup import Series, WorkloadKey

# Measured-iteration counts M tried, the agreement tolerances, and the share of runs that
# must agree.
ITERATION_SIZES = (1, 3, 5, 10, 15, 20, 30)
ITERATION_TOLERANCES = (0.01, 0.02)
AGREEING_SHARE = 0.95


def agrees(steady: list[float], size: int, tolerance: float) -> bool:
    return abs(statistics.median(steady[:size]) / statistics.median(steady[size:]) - 1) <= tolerance


# The first M iterations after W are compared with the iterations after them, never with
# themselves, so a short run cannot agree trivially.
def iteration_agreement(
    series: list[Series], warmups: dict[WorkloadKey, int], sizes: list[int], tolerance: float
) -> dict[int, float]:
    agreement = {}
    for size in sizes:
        within = []
        for run in series:
            steady = run.times[warmups[run.workload_key] :]
            if len(steady) > size:
                within.append(agrees(steady, size, tolerance))
        agreement[size] = sum(within) / len(within) if within else 0.0
    return agreement


def choose_iterations(agreement: dict[int, float], share: float) -> int | None:
    return next((size for size in sorted(agreement) if agreement[size] >= share), None)
