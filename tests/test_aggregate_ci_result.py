"""CI aggregate policy tests against synthetic `needs` payloads.

These exercise the exact logic the `ci-result` lane runs: the script is
imported in-process (hyphenated filename, so via importlib, following
test_release_gate.py) and fed synthetic payloads. The required-lane-skipped
case is the PRD's dynamic proof that a skipped required lane fails the
aggregate.
"""

from __future__ import annotations

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from types import ModuleType
from unittest.mock import patch

from install_test_support import PACK_ROOT

AGGREGATE_SCRIPT = PACK_ROOT / ".github" / "scripts" / "aggregate-ci-result.py"


def load_aggregate_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "aggregate_ci_result", AGGREGATE_SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


aggregate = load_aggregate_module()


def payload(**overrides: str) -> dict[str, dict[str, str]]:
    """An all-acceptable needs payload; keyword overrides replace results."""
    lanes = {
        "unittest": "success",
        "lint": "success",
        "release-payload-gate": "success",
        "auto-tag-release": "skipped",
    }
    for lane, result in overrides.items():
        key = lane.replace("_", "-")
        if key not in lanes:
            raise KeyError(f"override names unknown lane: {lane}")
        lanes[key] = result
    return {lane: {"result": result} for lane, result in lanes.items()}


def run_main(env_value: str | None) -> tuple[int, str, str]:
    env = {} if env_value is None else {"NEEDS_JSON": env_value}
    out, err = io.StringIO(), io.StringIO()
    with patch.dict("os.environ", env, clear=True):
        with redirect_stdout(out), redirect_stderr(err):
            code = aggregate.main()
    return code, out.getvalue(), err.getvalue()


class EvaluateTests(unittest.TestCase):
    def test_all_success_passes(self) -> None:
        code, messages = aggregate.evaluate(payload())
        self.assertEqual(code, 0)
        self.assertIn("all lanes green", messages)

    def test_required_lane_skipped_fails(self) -> None:
        code, messages = aggregate.evaluate(payload(unittest="skipped"))
        self.assertEqual(code, 1)
        self.assertIn("failed lanes: unittest", messages)

    def test_conditional_lane_skipped_passes(self) -> None:
        code, _ = aggregate.evaluate(payload(auto_tag_release="skipped"))
        self.assertEqual(code, 0)

    def test_conditional_lane_success_passes(self) -> None:
        code, _ = aggregate.evaluate(payload(auto_tag_release="success"))
        self.assertEqual(code, 0)

    def test_conditional_lane_failure_fails(self) -> None:
        code, messages = aggregate.evaluate(payload(auto_tag_release="failure"))
        self.assertEqual(code, 1)
        self.assertIn("failed lanes: auto-tag-release", messages)

    def test_required_lane_cancelled_fails(self) -> None:
        code, messages = aggregate.evaluate(payload(lint="cancelled"))
        self.assertEqual(code, 1)
        self.assertIn("failed lanes: lint", messages)

    def test_undeclared_extra_lane_fails(self) -> None:
        needs = payload()
        needs["mystery-lane"] = {"result": "success"}
        code, messages = aggregate.evaluate(needs)
        self.assertEqual(code, 2)
        self.assertTrue(any("undeclared lane" in m for m in messages))

    def test_declared_lane_absent_fails(self) -> None:
        needs = payload()
        del needs["release-payload-gate"]
        code, messages = aggregate.evaluate(needs)
        self.assertEqual(code, 2)
        self.assertTrue(any("missing from needs" in m for m in messages))

    def test_lane_entry_without_result_fails(self) -> None:
        needs = payload()
        needs["unittest"] = {}
        code, _ = aggregate.evaluate(needs)
        self.assertEqual(code, 1)


class MainTests(unittest.TestCase):
    def test_malformed_json_fails(self) -> None:
        code, _, err = run_main("{not json")
        self.assertEqual(code, 2)
        self.assertIn("not valid JSON", err)

    def test_missing_env_fails(self) -> None:
        code, _, err = run_main(None)
        self.assertEqual(code, 2)
        self.assertIn("NEEDS_JSON is not set", err)

    def test_non_object_payload_fails(self) -> None:
        code, _, err = run_main(json.dumps(["unittest"]))
        self.assertEqual(code, 2)
        self.assertIn("JSON object", err)

    def test_all_success_via_main(self) -> None:
        code, out, _ = run_main(json.dumps(payload()))
        self.assertEqual(code, 0)
        self.assertIn("all lanes green", out)

    def test_workflow_needs_matches_declared_lanes(self) -> None:
        """The ci-result needs list in tests.yml must equal the script's
        declared lane sets — rename drift should be caught here, not only
        at runtime."""
        workflow = (PACK_ROOT / ".github" / "workflows" / "tests.yml").read_text(
            encoding="utf-8"
        )
        declared = aggregate.REQUIRED_LANES | aggregate.CONDITIONAL_LANES
        marker = "ci-result:"
        self.assertIn(marker, workflow, "ci-result job renamed or removed")
        section = workflow[workflow.index(marker) :]
        needs_line = next(
            (
                line
                for line in section.splitlines()
                if line.strip().startswith("needs:")
            ),
            None,
        )
        self.assertIsNotNone(needs_line, "ci-result has no needs: line")
        assert needs_line is not None
        self.assertIn(
            "[",
            needs_line,
            "ci-result needs: is no longer an inline list; update this parser",
        )
        lanes = {
            lane.strip()
            for lane in needs_line.split("[", 1)[1].rsplit("]", 1)[0].split(",")
        }
        self.assertEqual(lanes, declared)


if __name__ == "__main__":
    unittest.main()
