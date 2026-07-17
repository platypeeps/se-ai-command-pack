"""Shared helpers for the installer test suite."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
