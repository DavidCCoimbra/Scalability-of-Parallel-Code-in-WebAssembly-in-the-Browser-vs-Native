import json
from pathlib import Path
from typing import Any

from harness.browsers import load_specs

REPOSITORY = Path(__file__).resolve().parent.parent
BROWSER_PINS = REPOSITORY / "harness/browsers.json"
CAMPAIGN_FILE = "campaign.json"
Context = dict[str, Any]


def read_json(path: Path) -> Context:
    data: Context = json.loads(path.read_text())
    return data


def campaign_metadata(directory: Path) -> Context | None:
    path = directory / CAMPAIGN_FILE
    return read_json(path) if path.exists() else None


def campaign_spec(directory: Path) -> Context:
    spec: Context = (campaign_metadata(directory) or {}).get("spec", {})
    return spec


def is_hybrid(directory: Path) -> bool:
    return bool(campaign_spec(directory).get("hybrid", False))


def order_seed_and_build(directory: Path) -> Context:
    metadata = campaign_metadata(directory)
    if metadata is None:
        return {}
    return {"campaignOrderSeed": metadata.get("orderSeed"), "campaignBuild": metadata.get("build")}


def pinned_browser_versions() -> dict[str, str]:
    return {name: spec.version for name, spec in load_specs(BROWSER_PINS).items()}

