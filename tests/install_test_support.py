"""Shared helpers for the installer test suite."""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

PACK_ROOT = Path(__file__).resolve().parent.parent
if str(PACK_ROOT) not in sys.path:
    sys.path.insert(0, str(PACK_ROOT))

INSTALL_PY = PACK_ROOT / "install.py"

from installer.registry import (  # noqa: E402
    INSTALLED_TARGETS_FILE,
    PLATFORM_REGISTRY,
    PROVENANCE_FILE,
)

ALL_PLATFORMS = tuple(sorted(PLATFORM_REGISTRY))


def git_env(**overrides: str) -> dict[str, str]:
    """Environment for a git that must not see this machine's state.

    Built from a ``GIT_*``-stripped copy of ``os.environ``: pointing only the
    file scopes at ``os.devnull`` would leave ``GIT_CONFIG_COUNT``/``_KEY_n``/
    ``_VALUE_n`` and ``GIT_CONFIG_PARAMETERS`` live at command-line scope,
    which outranks every configuration file. Dropping the whole namespace also
    closes ``GIT_DIR``, ``GIT_WORK_TREE``, ``GIT_INDEX_FILE``, and any future
    sibling; a test has no legitimate use for an inherited ``GIT_*``.

    ``GIT_CONFIG_GLOBAL`` needs git 2.32 (see CONTRIBUTING.md).
    """
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    env.update(overrides)
    return env


@contextlib.contextmanager
def hermetic_git_environment(**overrides: str) -> Iterator[None]:
    """Apply :func:`git_env` to ``os.environ`` for the duration of the block.

    For the callers that reach git through a child script or through
    production code that passes no ``env=``, where there is no keyword
    argument to add.
    """
    with mock.patch.dict(os.environ, git_env(**overrides), clear=True):
        yield


def make_home(base: Path, anchors: tuple[str, ...] = ALL_PLATFORMS) -> Path:
    """Create a fake install root with the given platforms' anchor dirs."""
    home = base / "home"
    home.mkdir(parents=True, exist_ok=True)
    for platform in anchors:
        (home / PLATFORM_REGISTRY[platform].anchor).mkdir(
            parents=True, exist_ok=True
        )
    return home


def run_installer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(INSTALL_PY), *args],
        cwd=PACK_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def install_ok(*args: str) -> subprocess.CompletedProcess:
    result = run_installer(*args)
    if result.returncode != 0:
        raise AssertionError(
            f"installer failed ({result.returncode}):\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def read_receipt_targets(home: Path) -> set[str]:
    receipt = home / INSTALLED_TARGETS_FILE
    if not receipt.is_file():
        return set()
    return {
        line.strip()
        for line in receipt.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def read_provenance(home: Path) -> dict:
    return json.loads((home / PROVENANCE_FILE).read_text(encoding="utf-8"))


def tree_paths(home: Path) -> set[str]:
    return {
        path.relative_to(home).as_posix()
        for path in home.rglob("*")
        if path.is_file() or path.is_symlink()
    }


class TempDirTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name).resolve()
