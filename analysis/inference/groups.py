from typing import Generic, NamedTuple, TypeVar

Item = TypeVar("Item")


# The two groups of an absolute contrast: log numerator - log denominator.
class Pair(NamedTuple, Generic[Item]):
    numerator: Item
    denominator: Item


# The four groups of an RQ1 or RQ2 contrast: the browser's log ratio minus native's.
# RQ2: numerator = atomic histogram, denominator = local. RQ1: numerator = T1, denominator = TN.
# Both stay tuples, so the bootstrap resamples them group by group like any other sequence.
class Quad(NamedTuple, Generic[Item]):
    browser_numerator: Item
    browser_denominator: Item
    native_numerator: Item
    native_denominator: Item
