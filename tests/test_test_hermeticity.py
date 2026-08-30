"""Guards that keep the suite's hermeticity from rotting.

Two shapes are checked, and they are exactly the two that produced real
failures: a `git` subprocess with no scrubbed environment, and a read of a
repository path a fresh clone does not have.

Both are structural checks over the tracked test modules, and their scope is
deliberately narrow in two ways. A path or an argv assembled at runtime is out
of reach. So is a subprocess that is not literally `git` but reaches git
underneath — a Python script under test, say — because the guard cannot tell
those from the many child processes with no business holding a git environment
(`run_installer`, `install_ok`), and a rule that demanded `env=` from all of
them would be noise rather than a gate.

Neither limit is unguarded. The `make test-hermetic` lane runs the whole suite
against a tracked-files-only tree under a hostile git configuration, so a child
process that inherits that configuration fails there empirically. These two are
the cheap structural half; that lane is the half with no blind spot.
"""

from __future__ import annotations

import ast
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from install_test_support import PACK_ROOT, git_env

SUBPROCESS_CALLS = frozenset(
    {"run", "Popen", "check_output", "check_call", "call"}
)

# Measured floors. They exist so a half-broken walk fails loudly instead of
# reporting zero violations over zero inspected sites.
MIN_GIT_CALL_SITES = 13
# 23 after the framework removal deleted the three test modules whose whole
# subject was the vendored install; lowered here, in the change that
# legitimately shrinks the surface, so the drop is visible to a reviewer.
MIN_PACK_ROOT_PATHS = 23


def tracked_test_modules() -> list[str]:
    """Enumerate from git, so a newly tracked module is covered on landing."""
    proc = subprocess.run(
        ["git", "-C", str(PACK_ROOT), "ls-files", "-z", "--", "tests/*.py"],
        capture_output=True,
        text=True,
        check=True,
        env=git_env(),
    )
    return [name for name in proc.stdout.split("\0") if name]


def tracked_paths() -> frozenset[str]:
    proc = subprocess.run(
        ["git", "-C", str(PACK_ROOT), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
        env=git_env(),
    )
    return frozenset(name for name in proc.stdout.split("\0") if name)


def _argv_candidates(node: ast.expr) -> list[ast.expr]:
    """Both arms of a conditional argv, not just the first.

    `tests/test_repo_tooling_ownership.py` writes its argv as
    `[...] if paths else [...]`; a list-literal-only rule silently skips it.
    """
    if isinstance(node, ast.IfExp):
        return [node.body, node.orelse]
    return [node]


def _starts_with_git(node: ast.expr) -> bool:
    if not isinstance(node, (ast.List, ast.Tuple)) or not node.elts:
        return False
    first = node.elts[0]
    return isinstance(first, ast.Constant) and first.value == "git"


def git_call_sites() -> list[tuple[str, int, bool]]:
    """Every `subprocess.*` call whose argv begins with the literal `git`."""
    sites: list[tuple[str, int, bool]] = []
    for name in tracked_test_modules():
        tree = ast.parse((PACK_ROOT / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            func = node.func
            attr = func.attr if isinstance(func, ast.Attribute) else None
            plain = func.id if isinstance(func, ast.Name) else None
            if (attr or plain) not in SUBPROCESS_CALLS:
                continue
            if not any(_starts_with_git(a) for a in _argv_candidates(node.args[0])):
                continue
            has_env = any(kw.arg == "env" for kw in node.keywords)
            sites.append((name, node.lineno, has_env))
    return sites


def _chain_parts(node: ast.expr) -> list[str] | None:
    """Literal path components of a `PACK_ROOT / "a" / "b"` chain."""
    parts: list[str] = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not isinstance(node.right, ast.Constant) or not isinstance(
            node.right.value, str
        ):
            return None
        parts.append(node.right.value)
        node = node.left
    if not (isinstance(node, ast.Name) and node.id == "PACK_ROOT"):
        return None
    return list(reversed(parts))


def pack_root_paths() -> list[tuple[str, int, str]]:
    """Maximal `PACK_ROOT / ...` chains, as (module, line, relative path).

    Maximal means the chain is not itself the left operand of another `/`, so
    the directory prefixes inside a longer path are not reported as their own
    reads.
    """
    found: list[tuple[str, int, str]] = []
    for name in tracked_test_modules():
        tree = ast.parse((PACK_ROOT / name).read_text(encoding="utf-8"))
        inner = {
            id(node.left)
            for node in ast.walk(tree)
            if isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Div)
            and isinstance(node.left, ast.BinOp)
        }
        for node in ast.walk(tree):
            if (
                not isinstance(node, ast.BinOp)
                or not isinstance(node.op, ast.Div)
                or id(node) in inner
            ):
                continue
            parts = _chain_parts(node)
            if parts:
                found.append((name, node.lineno, "/".join(parts)))
    return found


def declared_untracked_paths(module: str) -> frozenset[str]:
    """`HERMETICITY_UNTRACKED_PATHS` as written, without importing the module."""
    tree = ast.parse((PACK_ROOT / module).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "HERMETICITY_UNTRACKED_PATHS" not in names:
            continue
        if isinstance(node.value, (ast.Tuple, ast.List)):
            return frozenset(
                element.value
                for element in node.value.elts
                if isinstance(element, ast.Constant) and isinstance(element.value, str)
            )
    return frozenset()


class GitSubprocessEnvironmentTest(unittest.TestCase):
    """Every direct `git` call in the suite passes an explicit environment."""

    def test_every_git_call_site_passes_an_environment(self) -> None:
        unscrubbed = [
            f"{name}:{line}" for name, line, has_env in git_call_sites() if not has_env
        ]
        self.assertEqual(
            unscrubbed,
            [],
            "git subprocess call without env=git_env(): " + ", ".join(unscrubbed),
        )

    def test_the_scan_is_not_vacuous(self) -> None:
        """A rule that matches nothing would pass the assertion above."""
        self.assertGreaterEqual(len(git_call_sites()), MIN_GIT_CALL_SITES)



class UntrackedPathReadTest(unittest.TestCase):
    """No module reads a path that exists here and not in a fresh clone.

    PR #206: `.trellis/.template-hashes.json` is gitignored, so `make check`
    was green locally while every CI lane failed. A path may be read only when
    the reading module declares it and tolerates its absence.
    """

    def test_untracked_reads_are_declared(self) -> None:
        tracked = tracked_paths()
        undeclared = [
            f"{module}:{line} reads {rel}"
            for module, line, rel in pack_root_paths()
            if (PACK_ROOT / rel).is_file()
            and rel not in tracked
            and rel not in declared_untracked_paths(module)
        ]
        self.assertEqual(
            undeclared,
            [],
            "untracked path read without a HERMETICITY_UNTRACKED_PATHS entry: "
            + ", ".join(undeclared),
        )

    def test_declared_paths_are_genuinely_untracked(self) -> None:
        """Otherwise the tuple becomes a bypass for tracked paths."""
        tracked = tracked_paths()
        wrong = [
            f"{module}:{rel}"
            for module in tracked_test_modules()
            for rel in declared_untracked_paths(module)
            if rel in tracked
        ]
        self.assertEqual(wrong, [], "tracked path declared as untracked: " + ", ".join(wrong))

    def test_the_scan_is_not_vacuous(self) -> None:
        """The floor is on distinct paths, deduplicated lexically — not on
        chain occurrences, of which there are more than twice as many."""
        distinct = {rel for _, _, rel in pack_root_paths()}
        self.assertGreaterEqual(len(distinct), MIN_PACK_ROOT_PATHS)


class HermeticGitEnvironmentTest(unittest.TestCase):
    """`git_env` survives a configuration built to break it."""

    def test_command_scope_injection_is_dropped(self) -> None:
        """`GIT_CONFIG_COUNT` enters at command-line scope, which outranks
        every configuration file, so scrubbing the file scopes is not enough."""
        hostile = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": "/hostile/from-env",
        }
        with mock.patch.dict(os.environ, hostile):
            result = subprocess.run(
                ["git", "config", "--get", "core.hooksPath"],
                capture_output=True,
                text=True,
                check=False,
                env=git_env(),
            )
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_no_git_variable_is_inherited(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_DIR": "/hostile/git-dir"}):
            self.assertNotIn("/hostile/git-dir", git_env().values())


class HostileConfigurationTest(unittest.TestCase):
    """A matched pair: the same commit sequence fails inherited and succeeds
    scrubbed, under a configuration built to break it.

    The hostility arrives through two channels because they pin different
    things. `HOME` survives `git_env`'s `GIT_*` strip, so it is what pins
    `GIT_CONFIG_GLOBAL=os.devnull`; the command-scope triple is what pins the
    strip itself. An ambient `GIT_CONFIG_GLOBAL` would pin neither — the strip
    removes it whether or not the assignment survives.

    `core.hooksPath` is the knob rather than `commit.gpgsign`: a missing
    signing key is not universal, so `gpgsign` passes vacuously (or hangs) on a
    machine that has one. A `pre-commit` that exits 1 fails identically
    everywhere.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)

        hooks = base / "hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)

        self.home = base / "home"
        self.home.mkdir()
        (self.home / ".gitconfig").write_text(
            f"[core]\n\thooksPath = {hooks}\n", encoding="utf-8"
        )

        self.repo = base / "repo"
        self.repo.mkdir()
        (self.repo / "f.txt").write_text("x\n", encoding="utf-8")

        # Explicit and cleared: an inherited GIT_DIR or GIT_INDEX_FILE could
        # fail the negative half even with a broken hook fixture.
        self.hostile = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.home),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": str(hooks),
        }

    def _commit(self, env: dict[str, str] | None) -> int:
        for args in (
            ["init", "-q", "-b", "main"],
            ["add", "f.txt"],
            ["commit", "-qm", "x"],
        ):
            result = subprocess.run(
                ["git", "-C", str(self.repo), *args],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            if result.returncode != 0:
                return result.returncode
        return 0

    def test_git_is_new_enough_for_the_scrub(self) -> None:
        """`GIT_CONFIG_GLOBAL` needs git 2.32; older git would run unscrubbed."""
        raw = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True,
            env=git_env(),
        ).stdout.split()[2]
        version = tuple(int(part) for part in raw.split(".")[:2] if part.isdigit())
        self.assertGreaterEqual(version, (2, 32), f"git {raw} predates GIT_CONFIG_GLOBAL")

    def test_inherited_environment_is_poisoned(self) -> None:
        """Without this half the positive one could pass vacuously."""
        with mock.patch.dict(os.environ, self.hostile, clear=True):
            self.assertNotEqual(self._commit(env=None), 0)

    def test_scrubbed_environment_survives(self) -> None:
        with mock.patch.dict(os.environ, self.hostile, clear=True):
            self.assertEqual(self._commit(env=git_env()), 0)


if __name__ == "__main__":
    unittest.main()
