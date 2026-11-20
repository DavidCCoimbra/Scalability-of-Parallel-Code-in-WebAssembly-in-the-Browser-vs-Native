"""Command line of the campaign status report."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from harness.campaign.plan import plan
from harness.campaign.spec import CampaignSpec
from harness.campaign.status.journal_files import JournalFiles
from harness.campaign.status.progress import CampaignProgress
from harness.campaign.status.report import StatusReport


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python3 -m harness.campaign.status")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--results", type=Path, default=Path("data/raw"))
    return parser.parse_args(argv)


def campaign_progress(spec_path: Path, results: Path) -> CampaignProgress:
    spec = CampaignSpec.from_json(json.loads(spec_path.read_text()))
    return CampaignProgress(spec.name, tuple(plan(spec)), JournalFiles.read(results / spec.name))


def main(argv: list[str]) -> int:
    args = parse_arguments(argv)
    progress = campaign_progress(args.spec, args.results)
    print(StatusReport(progress, datetime.now(timezone.utc)).text)
    return 0
