"""Run a whole campaign: every configuration and repetition, in one shuffled order.

Usage: python3 -m harness.campaign SPEC.json [--results data/raw]
       [--native PATH] [--browsers harness/browsers]
       [--chrome PATH] [--firefox PATH] [--retry-failed]
Results go to <results>/<campaign name>/; rerunning the same spec resumes.
The native binary defaults to the one of the spec's build variant
(bench/target/release/native for baseline, bench/target/<build>/release/native
otherwise); the variant is recorded with the build identity.
"""

from harness.campaign.executors import BrowserExecutor, ExecutionResult, Executor, NativeExecutor, ResultServer
from harness.campaign.gate import EnvironmentGate, EnvironmentNotReady, HostEnvironment
from harness.campaign.identity import build_identity
from harness.campaign.journal import CampaignJournal
from harness.campaign.plan import discarded_runs, plan
from harness.campaign.planned_run import PlannedRun
from harness.campaign.runner import Campaign, Summary, keep_failure
from harness.campaign.spec import BuildVariant, CampaignSpec
from harness.campaign.workload import InputKind, Workload, WorkloadSpec

__all__ = [
    "BrowserExecutor",
    "BuildVariant",
    "Campaign",
    "CampaignJournal",
    "CampaignSpec",
    "EnvironmentGate",
    "EnvironmentNotReady",
    "ExecutionResult",
    "Executor",
    "HostEnvironment",
    "InputKind",
    "NativeExecutor",
    "PlannedRun",
    "ResultServer",
    "Summary",
    "Workload",
    "WorkloadSpec",
    "build_identity",
    "discarded_runs",
    "keep_failure",
    "plan",
]
