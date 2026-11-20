"""Read a closed set of strings from a campaign spec into its enum."""

from enum import StrEnum
from typing import TypeVar

Choice = TypeVar("Choice", bound=StrEnum)


def parse_choice(kind: type[Choice], value: object, problem: str) -> Choice:
    if not isinstance(value, str) or value not in {member.value for member in kind}:
        raise ValueError(problem)
    return kind(value)
