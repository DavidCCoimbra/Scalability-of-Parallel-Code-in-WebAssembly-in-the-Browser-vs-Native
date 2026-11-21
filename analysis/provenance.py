from typing import Any

from analysis.campaign import REPOSITORY
from harness.context import git_commit, utc_now


GENERATED = ("data/tables", "paper/figures")


def provenance() -> dict[str, Any]:
    return {"commit": git_commit(REPOSITORY, GENERATED), "createdAt": utc_now()}
