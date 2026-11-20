"""Independent reference for the golden fingerprints in bench/src/input/generators.rs.

Reimplements SplitMix64, noise and few_colors in Python and prints the
FNV-1a fingerprints that the Rust test `images_match_golden_fingerprints`
expects. Run: python3 bench/tools/golden_inputs.py
"""

from collections.abc import Iterator

MASK = (1 << 64) - 1
SEED = 0x5EED


def splitmix64(seed: int) -> Iterator[int]:
    state = seed
    while True:
        state = (state + 0x9E3779B97F4A7C15) & MASK
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        yield z ^ (z >> 31)


def noise(width: int, height: int, seed: int) -> list[int]:
    rng = splitmix64(seed)
    return [next(rng) >> 56 for _ in range(width * height)]


def few_colors(width: int, height: int, seed: int, k: int, consecutive: bool = False) -> list[int]:
    palette = list(range(k)) if consecutive else [i * 256 // k for i in range(k)]
    rng = splitmix64(seed)
    return [palette[next(rng) % k] for _ in range(width * height)]


def fnv1a(pixels: list[int]) -> int:
    value = 0xCBF29CE484222325
    for byte in pixels:
        value = ((value ^ byte) * 0x100000001B3) & MASK
    return value


if __name__ == "__main__":
    print(f"noise(256, 256, SEED):         {fnv1a(noise(256, 256, SEED)):#018x}")
    print(f"few_colors(256, 256, SEED, 4): {fnv1a(few_colors(256, 256, SEED, 4)):#018x}")
    print(f"few_colors_with(256, 256, SEED, 4, Consecutive): {fnv1a(few_colors(256, 256, SEED, 4, True)):#018x}")
