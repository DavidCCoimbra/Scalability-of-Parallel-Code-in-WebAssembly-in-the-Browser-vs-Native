"""The options each workload accepts beyond the shared ones, declared once per workload.

The same table as `WorkloadKind::capabilities` in bench/src/experiment/workload_kind.rs.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Capabilities:
    # Several passes per timed sample only where each pass recomputes the same result
    # from the input; the atomic histograms accumulate across passes and a sort's second pass
    # sorts sorted data.
    repeats_identically: bool = False
    # A fixed task size (rows for the filter, KB for the atomic and local histograms) only where
    # the kernel takes one.
    takes_grain: bool = False
    # v2: the image rows stored with a pitch (row stride in bytes) wider than the width; the filter only.
    takes_pitch: bool = False
    # No Rayon call in the workload: it runs on one thread only, whatever the campaign's thread counts.
    sequential: bool = False


NONE = Capabilities()
FILTER = Capabilities(repeats_identically=True, takes_grain=True, takes_pitch=True)
LOCAL_HISTOGRAM = Capabilities(repeats_identically=True, takes_grain=True)
ATOMIC_HISTOGRAM = Capabilities(takes_grain=True)
SEQUENTIAL_FILTER = Capabilities(repeats_identically=True, takes_pitch=True, sequential=True)
SEQUENTIAL_HISTOGRAM = Capabilities(repeats_identically=True, sequential=True)
# The one thread count of a sequential workload.
SEQUENTIAL_THREADS = 1
