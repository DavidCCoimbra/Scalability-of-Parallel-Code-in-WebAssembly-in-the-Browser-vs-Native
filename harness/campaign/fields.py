"""Typed reads of the values in a campaign spec object, which json.loads leaves untyped."""

from collections.abc import Mapping


class SpecFields:
    def __init__(self, data: Mapping[str, object]):
        self.data = data

    def integer(self, key: str) -> int:
        return expect_int(key, self.data[key])

    def integer_or(self, key: str, default: int) -> int:
        return expect_int(key, self.data.get(key, default))

    def optional_integer(self, key: str) -> int | None:
        value = self.data.get(key)
        return None if value is None else expect_int(key, value)

    def number(self, key: str, default: float) -> float:
        value = self.data.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"{key} must be a number, found {value!r}")
        return value

    def text(self, key: str) -> str:
        value = self.data[key]
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string, found {value!r}")
        return value

    def optional_text(self, key: str) -> str | None:
        value = self.data.get(key)
        return None if value is None else self.text(key)

    def flag(self, key: str, default: bool) -> bool:
        value = self.data.get(key, default)
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be true or false, found {value!r}")
        return value

    def items(self, key: str) -> list[object]:
        value = self.data[key]
        if not isinstance(value, list):
            raise ValueError(f"{key} must be a list, found {value!r}")
        return value

    def integers(self, key: str) -> tuple[int, ...]:
        return tuple(expect_int(key, value) for value in self.items(key))

    def objects(self, key: str) -> list[Mapping[str, object]]:
        return [expect_object(key, value) for value in self.items(key)]

    def raw(self, key: str, default: object) -> object:
        return self.data.get(key, default)


def expect_int(key: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer, found {value!r}")
    return value


def expect_object(key: str, value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"each entry of {key} must be an object, found {value!r}")
    return value
