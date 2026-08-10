"""End-to-end coverage for `install.py update` (audit A-022).

`update_pack` is the one command that mutates a user's checkout, and until now
it was exercised only through mocks or through a stub `install.py` that
appended to a sentinel file. Those prove process pinning; none of them proves
the pull advanced the checkout *and* that the installed files were refreshed.

The shape here is the real handshake: a bare origin one commit ahead of a
recorded source checkout, a real install underneath it, and two assertions —
the pull landed, and the payload change reached the installed tree. The second
is the one with teeth: a pull that lands without a refresh satisfies the first
and leaves the user's tree stale.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from install_test_support import (
    PACK_ROOT,
    TempDirTestCase,
    git_env,
    make_home,
)

SENTINEL = "<!-- hermetic update e2e sentinel -->"


@unittest.skipUnless(shutil.which("git"), "requires git")
class UpdateEndToEndTest(TempDirTestCase):
    def git(self, repo: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=False,
            env=git_env(),
        )
        if result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)}: {result.stderr}")
        return result.stdout.strip()

    def _origin_from_working_tree(self) -> Path:
        """Build the origin from the tracked working tree, not from HEAD.

        A `git clone` of `PACK_ROOT` would carry the last commit, so a probe
        that edits `installer/management.py` in the working tree would be
        invisible to this test — it would "pass" against code it never ran. On
        CI the two are identical anyway.
        """
        seed = self.base / "seed"
        listing = subprocess.run(
            ["git", "-C", str(PACK_ROOT), "ls-files", "-z"],
            capture_output=True,
            text=True,
            check=True,
            env=git_env(),
        ).stdout
        for name in listing.split("\0"):
            if not name:
                continue
            target = seed / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PACK_ROOT / name, target)

        self.git(seed, "init", "-q", "-b", "main")
        self.git(seed, "add", "-A")
        self.git(seed, "commit", "-qm", "seed")

        origin = self.base / "origin.git"
        subprocess.run(
            ["git", "clone", "--quiet", "--bare", str(seed), str(origin)],
            capture_output=True,
            text=True,
            check=True,
            env=git_env(),
        )
        return origin

    def _installer_env(self) -> dict[str, str]:
        """Hermetic, minus the subprocess-coverage hook.

        The installs here run from a throwaway copy of the repository. Left
        enabled, the hook writes coverage data whose source paths disappear
        with the temp directory, and `coverage combine` then fails with
        "No source for code".

        The cost is real but small, and it is the deliberate half of the
        trade: this test's `install.py` is a copy of the repository's own, so
        its lines go unmeasured here. They are measured by every other test
        that runs the installer in place, and the alternative — loosening the
        coverage gate or teaching `[paths]` to alias a temp directory that no
        longer exists — buys a duplicate measurement at the price of a weaker
        gate.
        """
        env = git_env()
        env.pop("COVERAGE_PROCESS_START", None)
        return env

    def _markdown_target(self, src: Path) -> tuple[str, str]:
        """A `templates/**` row with a Markdown source, as (source, target).

        `generated/**` rows would also have to satisfy generator parity, and
        three `templates/**` rows point at a Python script where appending to
        "the Markdown body" is meaningless.
        """
        manifest = json.loads((src / "manifest.json").read_text(encoding="utf-8"))
        for row in manifest["files"]:
            source = row["source"]
            if source.startswith("templates/") and source.endswith(".md"):
                return source, row["target"]
        raise AssertionError("no templates/**.md row in manifest.json")

    def test_update_pulls_and_refreshes_the_installed_tree(self) -> None:
        origin = self._origin_from_working_tree()
        src = self.base / "src"
        subprocess.run(
            ["git", "clone", "--quiet", str(origin), str(src)],
            capture_output=True,
            text=True,
            check=True,
            env=git_env(),
        )

        home = make_home(self.base)
        installed = subprocess.run(
            [sys.executable, str(src / "install.py"), "--root", str(home), "--all"],
            capture_output=True,
            text=True,
            check=False,
            env=self._installer_env(),
        )
        self.assertEqual(installed.returncode, 0, installed.stderr)

        source_rel, target_rel = self._markdown_target(src)
        installed_file = home / target_rel
        self.assertTrue(installed_file.is_file(), target_rel)
        self.assertNotIn(SENTINEL, installed_file.read_text(encoding="utf-8"))

        # Advance the origin from a scratch clone: `update_pack` refuses a
        # source checkout with uncommitted changes, so the mutation must never
        # be applied inside `src`.
        scratch = self.base / "scratch"
        subprocess.run(
            ["git", "clone", "--quiet", str(origin), str(scratch)],
            capture_output=True,
            text=True,
            check=True,
            env=git_env(),
        )
        upstream_source = scratch / source_rel
        upstream_source.write_text(
            upstream_source.read_text(encoding="utf-8") + f"\n{SENTINEL}\n",
            encoding="utf-8",
        )
        self.git(scratch, "add", "-A")
        self.git(scratch, "commit", "-qm", "advance payload")
        self.git(scratch, "push", "--quiet", "origin", "main")

        update = subprocess.run(
            [sys.executable, str(src / "install.py"), "update", "--root", str(home)],
            capture_output=True,
            text=True,
            check=False,
            env=self._installer_env(),
        )
        self.assertEqual(update.returncode, 0, update.stderr)

        self.assertEqual(
            self.git(src, "rev-parse", "HEAD"),
            self.git(origin, "rev-parse", "HEAD"),
            "the recorded checkout did not fast-forward to the origin",
        )
        self.assertIn(
            SENTINEL,
            installed_file.read_text(encoding="utf-8"),
            "the pull landed but the installed tree was never refreshed",
        )


if __name__ == "__main__":
    unittest.main()
