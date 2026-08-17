#!/usr/bin/env python3
"""Tag every version this push released, at HEAD, when the tag does not exist.

Usually that is just v<manifest version>. It is more when one branch bumps the
version several times: the changelog then gains several headings that all ship
in a single merge, and tagging only the manifest's final value silently drops
the intermediates. That is how v0.53.0 went missing (audit A-041) -- 0.53.0 and
0.53.1 landed together and only 0.53.1 was tagged.

"Released by this push" means: present in CHANGELOG.md and higher than the
highest tag that already exists. Deliberately not "any untagged changelog
version" -- that would backfill historical holes like v0.53.0 onto today's
HEAD, which is a different and much worse claim than leaving them missing. A
hole is repaired by tagging the commit that actually shipped it, which this
script cannot know.

The comparison is against existing tags rather than against the previous
commit's changelog because CI checks out at depth 1: HEAD^ does not exist
there, but `git ls-remote --tags` works regardless of clone depth.

Idempotent: an existing tag is left untouched (a push without a version
bump simply reports it), and the script never moves a tag. Pass --push to
push the created tag to origin (CI does); local runs default to tag-only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[2]
GIT_TIMEOUT_SECONDS = 60
# Matches the changelog's only heading form, e.g. `## 0.70.0 - 2026-08-16`.
# Anchored and strict: a heading that does not match is not a release, and
# guessing at a looser shape would invent tags for prose headings.
CHANGELOG_VERSION = re.compile(r"^## (\d+\.\d+\.\d+) - ", re.MULTILINE)
TAG_VERSION = re.compile(r"^v(\d+\.\d+\.\d+)$")


class ReleaseTagError(Exception):
    """A git invocation could not run to completion (missing or timed out)."""


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            capture_output=True,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        raise ReleaseTagError("git not found") from None
    except subprocess.TimeoutExpired:
        raise ReleaseTagError(f"git {' '.join(args)} timed out") from None


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _existing_tag_versions(repo: Path, use_remote: bool) -> set[str]:
    """Versions that already carry a tag.

    Reads origin when pushing, because a CI checkout is shallow and carries no
    local tags -- asking the local repo there would report "nothing tagged" and
    make every changelog version look new.
    """
    if use_remote:
        result = run_git(repo, "ls-remote", "--tags", "origin")
        if result.returncode != 0:
            # Phrased to match the per-tag check below: an unreachable origin
            # now surfaces here first, and test_push_without_origin_fails_cleanly
            # pins that wording as the user-facing contract.
            raise ReleaseTagError(
                f"cannot query origin for tags: {result.stderr.strip()}"
            )
        names = [
            line.rsplit("/", 1)[-1]
            for line in result.stdout.splitlines()
            if "\trefs/tags/" in line
        ]
        # Peeled entries (`refs/tags/v1.0.0^{}`) name the same version; the set
        # collapses them.
        names = [name.removesuffix("^{}") for name in names]
    else:
        result = run_git(repo, "tag", "--list")
        if result.returncode != 0:
            raise ReleaseTagError(f"cannot list tags: {result.stderr.strip()}")
        names = result.stdout.split()
    return {m.group(1) for m in (TAG_VERSION.match(n) for n in names) if m}


def _versions_to_tag(
    changelog_versions: list[str], existing: set[str], manifest_version: str
) -> list[str]:
    """Versions this push released, oldest first.

    The manifest version is always included: it is the release being made, and
    a changelog that somehow omits it must still get its tag.
    """
    if existing:
        highest = max(_version_key(v) for v in existing)
        released = {v for v in changelog_versions if _version_key(v) > highest}
    else:
        # No tags at all: the whole changelog is history that predates tagging,
        # so claim only the version actually being released rather than
        # retroactively tagging every past release at HEAD.
        released = set()
    released.add(manifest_version)
    # Not filtered against `existing`: an already-tagged manifest version must
    # still reach _create_release_tag so a push without a bump keeps reporting
    # "already exists; leaving it in place" rather than going silent.
    return sorted(released, key=_version_key)


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
    changelog_path = repo / "CHANGELOG.md"
    try:
        changelog_text = changelog_path.read_text(encoding="utf-8")
    except OSError:
        # A missing changelog is not fatal: fall back to the manifest version,
        # which is exactly the pre-A-041 behaviour.
        changelog_text = ""
    changelog_versions = CHANGELOG_VERSION.findall(changelog_text)

    try:
        existing = _existing_tag_versions(repo, args.push)
        versions = _versions_to_tag(changelog_versions, existing, version)
        if len(versions) > 1:
            print(
                "this push releases "
                + ", ".join(f"v{v}" for v in versions)
                + f" (manifest is v{version}); tagging each at HEAD"
            )
        status = 0
        for released in versions:
            result = _create_release_tag(repo, f"v{released}", args)
            # Keep going after a failure so one bad tag does not strand the
            # rest untagged, which is the failure mode this change exists to
            # prevent.
            status = status or result
        return status
    except ReleaseTagError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


def _create_release_tag(repo: Path, tag: str, args: argparse.Namespace) -> int:
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
