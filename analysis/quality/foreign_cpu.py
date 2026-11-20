from analysis.campaign import Context

# Twice the largest foreign CPU time of the strict pilots (0.125 s, Chrome).
FOREIGN_CPU_THRESHOLD = 0.25
FOREIGN_CPU_KEY = "foreignCpuSeconds"


def foreign_cpu_seconds(context: Context) -> float | None:
    value = context.get(FOREIGN_CPU_KEY)
    return value if isinstance(value, (int, float)) else None


def above_threshold(context: Context, threshold: float) -> bool:
    seconds = foreign_cpu_seconds(context)
    return seconds is not None and seconds > threshold
