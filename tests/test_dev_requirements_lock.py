"""Regression tests for .github/scripts/check-dev-requirements-lock.py.

The checker gates requirements-dev.lock against its input requirements-dev.txt.
Every negative case builds a disposable fixture directory and passes --repo at
it; no test mutates the repository's own requirements files. One case asserts
the live repository still passes, which is the state CI depends on.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / ".github" / "scripts" / "check-dev-requirements-lock.py"

_spec = importlib.util.spec_from_file_location("check_dev_requirements_lock", SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)

HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64


def hashed(entry: str) -> str:
    """Render a lock entry with the hash continuation uv emits."""
    return f"{entry} \\\n    --hash={HASH_A} \\\n    --hash={HASH_B}"


DEFAULT_INPUT = "# comment\nPyYAML==6.0.3\nruff==0.16.1\n"
DEFAULT_LOCK = "\n".join(
    [
        hashed("pyyaml==6.0.3"),
        hashed("ruff==0.16.1"),
        hashed("tomli==2.4.1 ; python_full_version < '3.11'"),
        "",
    ]
)


class LockCheckerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def fixture(self, *, input_text: str = DEFAULT_INPUT, lock_text: str = DEFAULT_LOCK) -> None:
        (self.root / checker.INPUT_PATH).write_text(input_text, encoding="utf-8")
        (self.root / checker.LOCK_PATH).write_text(lock_text, encoding="utf-8")

    def run_checker(self, *args: str) -> tuple[int, str]:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            status = checker.main([*args])
        return status, stream.getvalue()

    def run_fixture(self) -> tuple[int, str]:
        return self.run_checker("--repo", str(self.root))

    # -- passing states ----------------------------------------------------

    def test_real_repository_passes(self) -> None:
        status, output = self.run_checker("--repo", str(REPO_ROOT))
        self.assertEqual(status, 0, output)
        self.assertEqual(output, "")

    def test_clean_fixture_passes(self) -> None:
        self.fixture()
        status, output = self.run_fixture()
        self.assertEqual(status, 0, output)

    def test_name_normalization_matches_across_forms(self) -> None:
        # Case and separator differ but PEP 503 normalizes both spellings to
        # the same distribution, so the pin comparison must not report a miss.
        self.fixture(
            input_text="PyYAML==6.0.3\nAST_Serialize==0.8.0\n",
            lock_text=hashed("pyyaml==6.0.3") + "\n" + hashed("ast-serialize==0.8.0") + "\n",
        )
        status, output = self.run_fixture()
        self.assertEqual(status, 0, output)

    # -- finding classes ---------------------------------------------------

    def test_pin_mismatch_is_reported(self) -> None:
        self.fixture(input_text="ruff==0.17.0\n")
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("pin-mismatch: ruff is 0.17.0", output)
        self.assertIn("but 0.16.1", output)

    def test_pin_missing_is_reported(self) -> None:
        self.fixture(input_text="mypy==2.3.0\n")
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("pin-missing: mypy==2.3.0", output)

    def test_loosened_lock_entry_is_reported_not_skipped(self) -> None:
        # The entry rule must not require "==". An earlier rule that did would
        # have skipped this line entirely and passed a lock with no pin at all.
        self.fixture(lock_text=hashed("ruff>=0.16") + "\n")
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("unpinned:", output)
        self.assertIn("ruff>=0.16", output)

    def test_indented_entry_is_still_an_entry(self) -> None:
        # pip strips each line before parsing, so an indented requirement
        # installs exactly like an unindented one. Treating indentation alone as
        # continuation text would let this requirement bypass the gate.
        self.fixture(input_text="  ruff>=0.16\n")
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("input-unpinned:", output)

    def test_indented_pin_is_read_not_skipped(self) -> None:
        self.fixture(input_text="   ruff==0.17.0\n")
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("pin-mismatch: ruff is 0.17.0", output)

    def test_every_finding_is_reported_not_just_the_first(self) -> None:
        self.fixture(
            input_text="ruff==0.17.0\nmypy==2.3.0\n",
            lock_text=hashed("ruff==0.16.1") + "\npyyaml==6.0.3\n",
        )
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        for expected in ("unhashed:", "pin-missing: mypy", "pin-mismatch: ruff"):
            self.assertIn(expected, output)
        self.assertEqual(len(output.strip().splitlines()), 3, output)

    def test_loosened_input_entry_is_reported(self) -> None:
        self.fixture(input_text="ruff>=0.16\n")
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("input-unpinned:", output)

    def test_unhashed_lock_entry_is_reported(self) -> None:
        self.fixture(
            input_text="ruff==0.16.1\n",
            lock_text=hashed("pyyaml==6.0.3") + "\nruff==0.16.1\n",
        )
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("unhashed:", output)
        self.assertIn("ruff", output)

    def test_unhashed_entry_names_the_right_entry(self) -> None:
        # hash blocks are matched to entries positionally; a misalignment would
        # blame the wrong distribution and send the reader to the wrong line.
        self.fixture(
            input_text="pyyaml==6.0.3\n",
            lock_text="pyyaml==6.0.3\n" + hashed("ruff==0.16.1") + "\n",
        )
        status, output = self.run_fixture()
        self.assertEqual(status, 1, output)
        self.assertIn("unhashed: requirements-dev.lock entry pyyaml", output)
        self.assertNotIn("entry ruff", output)

    # -- error paths -------------------------------------------------------

    def test_missing_lock_is_an_error(self) -> None:
        (self.root / checker.INPUT_PATH).write_text(DEFAULT_INPUT, encoding="utf-8")
        status, output = self.run_fixture()
        self.assertEqual(status, 2, output)
        self.assertIn("make lock", output)

    def test_missing_input_is_an_error(self) -> None:
        (self.root / checker.LOCK_PATH).write_text(DEFAULT_LOCK, encoding="utf-8")
        status, output = self.run_fixture()
        self.assertEqual(status, 2, output)
        self.assertIn(checker.INPUT_PATH, output)
        # `make lock` regenerates the lock, not its input, so offering it here
        # would point the reader at a command that cannot fix the problem.
        self.assertNotIn("make lock", output)
        self.assertIn("--repo", output)

    def test_empty_lock_is_an_error(self) -> None:
        self.fixture(lock_text="# only a comment\n")
        status, output = self.run_fixture()
        self.assertEqual(status, 2, output)
        self.assertIn("declares no requirements", output)

    def test_nonexistent_repo_is_an_error(self) -> None:
        status, output = self.run_checker("--repo", str(self.root / "absent"))
        self.assertEqual(status, 2, output)
        self.assertIn("not a directory", output)


class WiringTest(unittest.TestCase):
    """The checker is worthless unless the gates actually call it."""

    def test_makefile_installs_from_the_lock_with_hashes_and_wheels_only(self) -> None:
        makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("--require-hashes --only-binary :all: -r requirements-dev.lock", makefile)
        # --clear: a reused venv keeps packages the lock has since dropped.
        self.assertIn("venv --clear", makefile)
        self.assertIn("check-dev-requirements-lock.py", makefile)

    def test_ci_workflow_parses_and_installs_from_the_lock(self) -> None:
        # `--only-binary :all: ` ends in a colon followed by a space, which is
        # YAML's mapping indicator: unquoted, it makes the whole workflow file
        # unparseable and GitHub silently runs no jobs at all — a green-looking
        # PR with zero checks. Parsing here is what catches that.
        workflow = yaml.safe_load(
            (REPO_ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        )
        installs = [
            step["run"]
            for job in workflow["jobs"].values()
            for step in job.get("steps", [])
            if isinstance(step.get("run"), str) and "pip install" in step["run"]
        ]
        # Enumerated, not counted: a hardcoded number has to be edited every
        # time a lane is added, and the property is "every job that sets up
        # Python installs from the lock", not "there are N such jobs".
        setups = [
            job_name
            for job_name, job in workflow["jobs"].items()
            for step in job.get("steps", [])
            if str(step.get("uses", "")).startswith("actions/setup-python")
        ]
        self.assertEqual(len(installs), len(setups), (installs, setups))
        self.assertGreaterEqual(len(installs), 3, installs)
        for command in installs:
            self.assertIn("--require-hashes --only-binary :all:", command)
            self.assertIn("-r requirements-dev.lock", command)


if __name__ == "__main__":
    unittest.main()
