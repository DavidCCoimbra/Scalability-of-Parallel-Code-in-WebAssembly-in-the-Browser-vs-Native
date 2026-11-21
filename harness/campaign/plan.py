"""The campaign order: every configuration and repetition, shuffled with the recorded seed."""

import random

from harness.campaign.planned_run import DISCARDED_POSITION, PlannedRun
from harness.campaign.spec import CampaignSpec


def plan(spec: CampaignSpec) -> list[PlannedRun]:
    combinations = [
        (environment, arm, workload, threads, repetition)
        for repetition in range(spec.repetitions)
        for environment in spec.environments
        for arm in spec.arms_of(environment)
        for workload in spec.workloads
        for threads in spec.threads_of(workload)
    ]
    random.Random(spec.order_seed).shuffle(combinations)
    return [
        PlannedRun(position, environment, workload, threads, repetition, spec.name, arm=arm)
        for position, (environment, arm, workload, threads, repetition) in enumerate(combinations)
    ]


def discarded_runs(spec: CampaignSpec, session: int) -> list[PlannedRun]:
    # The first launch of a browser on a machine is much slower; it runs once per session and is not kept.
    if not spec.discard_first_launch:
        return []
    return [
        PlannedRun(DISCARDED_POSITION, environment, spec.workloads[0], spec.threads_of(spec.workloads[0])[0], 0, spec.name, discarded=True, session=session)
        for environment in spec.environments
        if environment.is_browser
    ]
