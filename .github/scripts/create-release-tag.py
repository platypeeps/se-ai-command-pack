#!/usr/bin/env python3
"""Tag v<manifest version> at HEAD when the tag does not exist yet.

Idempotent: an existing tag is left untouched (a push without a version
bump simply reports it), and the script never moves a tag. Pass --push to
push the created tag to origin (CI does); local runs default to tag-only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[2]
GIT_TIMEOUT_SECONDS = 60


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
        timeout=GIT_TIMEOUT_SECONDS,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(PACK_ROOT))
    parser.add_argument("--push", action="store_true", help="Push the tag to origin.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    repo = Path(args.repo).resolve()

    manifest_path = repo / "manifest.json"
    try:
        version = json.loads(manifest_path.read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError) as error:
        print(f"error: cannot read version from {manifest_path}: {error}",
              file=sys.stderr)
        return 1
    tag = f"v{version}"

    # CI checkouts are shallow and tag-less, so a local ref check alone
    # would recreate an existing release tag at the new HEAD and fail on
    # push. When pushing, the remote is the authority.
    if args.push:
        remote = run_git(
            repo, "ls-remote", "--exit-code", "--tags", "origin",
            f"refs/tags/{tag}",
        )
        if remote.returncode == 0:
            print(f"tag {tag} already exists on origin; leaving it in place")
            return 0
        if remote.returncode != 2:
            print(
                f"error: cannot query origin for tag {tag}: "
                f"{remote.stderr.strip()}",
                file=sys.stderr,
            )
            return 1

    existing_locally = (
        run_git(repo, "rev-parse", "--verify", f"refs/tags/{tag}").returncode == 0
    )
    if existing_locally and not args.push:
        print(f"tag {tag} already exists; leaving it in place")
        return 0

    if args.dry_run:
        print(f"would create tag {tag} at HEAD" + (" and push" if args.push else ""))
        return 0

    if not existing_locally:
        created = run_git(repo, "tag", tag, "HEAD")
        if created.returncode != 0:
            print(f"error: cannot create tag {tag}: {created.stderr.strip()}",
                  file=sys.stderr)
            return 1
        print(f"created tag {tag} at HEAD")
    if args.push:
        pushed = run_git(repo, "push", "origin", tag)
        if pushed.returncode != 0:
            print(f"error: cannot push tag {tag}: {pushed.stderr.strip()}",
                  file=sys.stderr)
            return 1
        print(f"pushed tag {tag} to origin")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
