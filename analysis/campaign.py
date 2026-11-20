import json
from pathlib import Path
from typing import Any

from harness.browsers import load_specs
from harness.context import DEFAULT_PASSES, validate

REPOSITORY = Path(__file__).resolve().parent.parent
BROWSER_PINS = REPOSITORY / "harness/browsers.json"
CAMPAIGN_FILE = "campaign.json"
Context = dict[str, Any]


def read_json(path: Path) -> Context:
    data: Context = json.loads(path.read_text())
    return data


def run_context(directory: Path, run_id: str) -> Context:
    return read_json(directory / f"{run_id}.json")


# The runs record their passes K; the runs stored before passes existed ran one.
def passes_of(context: Context) -> int:
    passes = context.get("passes", DEFAULT_PASSES)
    return passes if isinstance(passes, int) and not isinstance(passes, bool) else DEFAULT_PASSES


def campaign_metadata(directory: Path) -> Context | None:
    path = directory / CAMPAIGN_FILE
    return read_json(path) if path.exists() else None


def campaign_spec(directory: Path) -> Context:
    spec: Context = (campaign_metadata(directory) or {}).get("spec", {})
    return spec


def is_hybrid(directory: Path) -> bool:
    return bool(campaign_spec(directory).get("hybrid", False))


def image_side(directory: Path) -> int:
    side: int = campaign_spec(directory)["width"]
    return side


def order_seed_and_build(directory: Path) -> Context:
    metadata = campaign_metadata(directory)
    if metadata is None:
        return {}
    return {"campaignOrderSeed": metadata.get("orderSeed"), "campaignBuild": metadata.get("build")}


def pinned_browser_versions() -> dict[str, str]:
    return {name: spec.version for name, spec in load_specs(BROWSER_PINS).items()}


def strict_problems(context: Context, pinned: dict[str, str], hybrid: bool = False) -> list[str]:
    problems: list[str] = validate(context, strict=True, pinned=pinned, hybrid=hybrid)
    return problems

