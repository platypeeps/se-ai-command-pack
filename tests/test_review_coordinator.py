"""Regression tests for the sd-review coordinator's deterministic-check gate.

These cover the nested-check false-block fix: the coordinator memoized the whole
typed sd-check report in durable per-attempt state and served it as the gate on
later runs at the same head, even though two checks (knowledge.obsidian-kb,
pack.review-scope) read live inputs the state identity does not capture (a
gitignored .obsidian-kb symlink target and the live PR body). The fix
recomputes the check on every invocation via ``_resolve_check``. See
.trellis/tasks/08-04-audit-review-nested-check-falseblock.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from install_test_support import PACK_ROOT

# review.py imports sd_ai_command_pack_lib, which lives under scripts/.
SCRIPTS_DIR = PACK_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REVIEW_PATH = SCRIPTS_DIR / "sd-ai-command-pack-review.py"
spec = importlib.util.spec_from_file_location("sd_review_coordinator", REVIEW_PATH)
assert spec is not None and spec.loader is not None
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def _passed_report() -> dict[str, object]:
    return {"schemaVersion": 1, "status": "passed", "checks": [{"id": "knowledge.obsidian-kb", "status": "passed"}]}


def _failed_report() -> dict[str, object]:
    return {"schemaVersion": 1, "status": "failed", "checks": [{"id": "knowledge.obsidian-kb", "status": "failed"}]}


class ResolveCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self._original_run_check = review._run_check
        self._tmp = tempfile.TemporaryDirectory()
        self.state_path = Path(self._tmp.name) / "attempt.json"

    def tearDown(self) -> None:
        review._run_check = self._original_run_check
        self._tmp.cleanup()

    def _stub_run_check(self, report: dict[str, object]) -> None:
        review._run_check = lambda repo: report

    def _write_state(self, state: dict[str, object]) -> None:
        self.state_path.write_text(json.dumps(state), encoding="utf-8")

    def test_stale_cached_failure_is_recomputed_fresh(self) -> None:
        # AC1: pre-fix, review.py served this cached failing report as the gate
        # while a direct check.py run on the identical tree passed. The live
        # tree now passes (stubbed), so _resolve_check must return the fresh
        # passed report, not the cached failure.
        state = {
            "phase": "remote",
            "check": _failed_report(),
            "local": {"status": "clean"},
            "remote": {"observation": None},
        }
        self._write_state(state)
        self._stub_run_check(_passed_report())

        result = review._resolve_check(Path("."), state, self.state_path)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(state["check"]["status"], "passed")
        # persisted to disk
        on_disk = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["check"]["status"], "passed")

    def test_nested_result_matches_direct_for_pass_and_fail(self) -> None:
        # AC2: the coordinator's gate mirrors a direct check.py run in both
        # directions -- no cache can diverge them.
        for report in (_passed_report(), _failed_report()):
            state = {"phase": "check", "check": _failed_report()}
            self._write_state(state)
            self._stub_run_check(report)
            result = review._resolve_check(Path("."), state, self.state_path)
            self.assertEqual(result["status"], report["status"])

    def test_genuine_failure_still_blocks(self) -> None:
        # AC3: a genuinely failing check (stale KB / absent scope section) still
        # fails in the nested path -- recompute never masks a real failure.
        state = {"phase": "remote", "check": _passed_report(), "local": {"x": 1}}
        self._write_state(state)
        self._stub_run_check(_failed_report())
        result = review._resolve_check(Path("."), state, self.state_path)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(state["check"]["status"], "failed")

    def test_resume_does_not_regress_phase_or_cached_stages(self) -> None:
        # Recomputing check on resume must not roll the phase back to "check"
        # nor disturb the memoized local/remote stages.
        local = {"status": "clean", "receipt": {"id": "abc"}}
        remote = {"observation": {"state": "pending"}}
        state = {"phase": "remote", "check": _failed_report(), "local": local, "remote": remote}
        self._write_state(state)
        self._stub_run_check(_passed_report())
        review._resolve_check(Path("."), state, self.state_path)
        self.assertEqual(state["phase"], "remote")
        self.assertEqual(state["local"], local)
        self.assertEqual(state["remote"], remote)

    def test_first_entry_advances_phase_and_persists(self) -> None:
        # With no prior check, _resolve_check advances the phase to "check" and
        # writes the fresh report -- the unchanged first-run behavior.
        state: dict[str, object] = {"phase": "capability", "capability": {"state": "skipped"}}
        self._write_state(state)
        self._stub_run_check(_passed_report())
        result = review._resolve_check(Path("."), state, self.state_path)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(state["phase"], "check")
        on_disk = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["check"]["status"], "passed")


class _TmpDir:
    """Minimal context manager yielding a TemporaryDirectory path string."""

    def __enter__(self) -> str:
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        return self._tmp.name

    def __exit__(self, *exc: object) -> None:
        self._tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
