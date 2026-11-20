"""What a campaign writes about itself: campaign.json (spec, build, plan) and campaign.jsonl (one line per run)."""

import json
from dataclasses import asdict
from pathlib import Path

from harness.campaign.executors import ExecutionResult
from harness.campaign.planned_run import PlannedRun
from harness.campaign.spec import CampaignSpec
from harness.context import JsonObject, RunFiles, utc_now, validate

METADATA_FILE = "campaign.json"
LOG_FILE = "campaign.jsonl"
JSON_INDENT = 2


class CampaignJournal:
    def __init__(self, spec: CampaignSpec, results: Path, build: JsonObject, pinned: dict[str, str]):
        self.spec = spec
        self.results = results
        self.build = build
        self.pinned = pinned

    @property
    def metadata_path(self) -> Path:
        return self.results / METADATA_FILE

    def start_session(self, runs: list[PlannedRun]) -> int:
        path = self.metadata_path
        meta = self.resumed(path) if path.exists() else self.created(runs)
        path.write_text(json.dumps(meta, indent=JSON_INDENT) + "\n")
        resumes = meta.get("resumedAt", [])
        return 1 + (len(resumes) if isinstance(resumes, list) else 0)

    def created(self, runs: list[PlannedRun]) -> JsonObject:
        return {
            "name": self.spec.name,
            "orderSeed": self.spec.order_seed,
            "plannedRuns": len(runs),
            "spec": self.spec.to_json(),
            "build": self.build,
            "startedAt": utc_now(),
            "runs": [run.run_id for run in runs],
        }

    def resumed(self, path: Path) -> JsonObject:
        meta: JsonObject = json.loads(path.read_text())
        if meta["spec"] != self.spec.to_json():
            raise ValueError(f"{path} belongs to a different campaign spec; use a new name")
        if meta.get("build") != self.build:
            raise ValueError(f"{path} was started with a different build or browsers; use a new name")
        earlier = meta.get("resumedAt", [])
        meta["resumedAt"] = [*(earlier if isinstance(earlier, list) else []), utc_now()]
        return meta

    def log(self, run: PlannedRun, result: ExecutionResult, results: Path) -> None:
        entry = {
            "position": run.position,
            "runId": run.run_id,
            "environment": run.environment,
            **asdict(run.workload),
            "threads": run.threads,
            "repetition": run.repetition,
            "query": self.spec.query(run),
            "status": result.status,
            "seconds": result.seconds,
            "message": result.message,
            "problems": self.problems(run, results),
            "discarded": run.discarded,
            "loggedAt": utc_now(),
        }
        with (self.results / LOG_FILE).open("a") as file:
            file.write(json.dumps(entry) + "\n")

    def problems(self, run: PlannedRun, results: Path) -> list[str]:
        files = RunFiles(results, run.run_id)
        for path in (files.metadata, files.error):
            if path.exists():
                context = json.loads(path.read_text())
                return validate(context, strict=self.spec.strict, pinned=self.pinned, hybrid=self.spec.hybrid)
        return ["no metadata file"]
