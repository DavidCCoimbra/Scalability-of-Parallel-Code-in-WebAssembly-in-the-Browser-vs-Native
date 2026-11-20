import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from analysis.inference.exclusion import Reason, excluded_runs

MODULE = "analysis.inference.exclusion"


class HybridFlagTest(unittest.TestCase):
    def excluded_with(self, spec: dict[str, object]) -> list[bool]:
        seen: list[bool] = []

        def problems(context: object, pinned: object, hybrid: bool = False) -> list[str]:
            seen.append(hybrid)
            return []

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "campaign.json").write_text(json.dumps({"spec": spec}))
            with (
                mock.patch(f"{MODULE}.run_context", return_value={}),
                mock.patch(f"{MODULE}.pinned_browser_versions", return_value={}),
                mock.patch(f"{MODULE}.strict_problems", side_effect=problems),
            ):
                exclusions = excluded_runs(directory, {"run-1"}, None, strict=True)
        self.assertEqual(exclusions.counts()[Reason.STRICT_VALIDATION], 0)
        return seen

    def test_a_hybrid_campaign_is_validated_as_hybrid(self) -> None:
        self.assertEqual(self.excluded_with({"hybrid": True}), [True])

    def test_a_p_core_campaign_is_validated_strictly(self) -> None:
        self.assertEqual(self.excluded_with({}), [False])


if __name__ == "__main__":
    unittest.main()
