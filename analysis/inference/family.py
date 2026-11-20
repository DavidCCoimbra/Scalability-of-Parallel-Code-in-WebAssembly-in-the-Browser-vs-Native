from analysis.configuration import Input, Workload
from analysis.inference.cells import Cells
from analysis.inference.question import Question

# Analysis plan D8: the primary family is RQ2 at the maximum N for every k and
# both browsers (4 x 2) plus RQ1 for the filter on noise at the maximum N (2), so m = 10, with Holm
# at alpha = 0.05 and Bonferroni intervals at 1 - alpha / m.
FAMILY_ALPHA = 0.05
PRIMARY_FAMILY_SIZE = 10
BONFERRONI_CONFIDENCE = 1 - FAMILY_ALPHA / PRIMARY_FAMILY_SIZE
PRIMARY_RQ1_WORKLOAD = Workload.FILTER
PRIMARY_RQ1_INPUT = Input.NOISE


class IncompleteFamily(ValueError):
    pass


def is_primary(cells: Cells, max_threads: int) -> bool:
    configuration = cells.configuration
    if cells.question is Question.ABSOLUTE or configuration.threads != max_threads:
        return False
    if cells.question is Question.RQ2:
        return True
    return configuration.workload == PRIMARY_RQ1_WORKLOAD and configuration.input == PRIMARY_RQ1_INPUT


# The maximum N is the pre-registered --max-threads, not the largest N in the data, so a campaign
# that lost a configuration fails here instead of silently testing a smaller family.
def primary_flags(all_cells: list[Cells], max_threads: int, partial: bool) -> list[bool]:
    flags = [not partial and is_primary(cells, max_threads) for cells in all_cells]
    if not partial and sum(flags) != PRIMARY_FAMILY_SIZE:
        raise IncompleteFamily(
            f"the planned primary family has {PRIMARY_FAMILY_SIZE} contrasts at N = {max_threads}, "
            f"the data gives {sum(flags)}; use partial for pilot data"
        )
    return flags
