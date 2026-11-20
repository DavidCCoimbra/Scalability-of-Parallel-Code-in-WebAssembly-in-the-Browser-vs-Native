from typing import Any

from analysis.campaign import REPOSITORY
from harness.context import git_commit, utc_now


def provenance() -> dict[str, Any]:
    return {"commit": git_commit(REPOSITORY), "createdAt": utc_now()}
