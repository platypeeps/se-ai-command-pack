#!/usr/bin/env python3
"""Release payload gate.

Enforces the pack's release discipline against a base revision:

1. any change under templates/**, generated/**, or to manifest.json requires the manifest
   version to differ from the base revision's, and
2. whenever the version changed, CHANGELOG.md's first heading must be
   `## <version> - YYYY-MM-DD` with a real date.

Changes are measured from the merge-base of --base and HEAD to the working
tree (uncommitted and untracked files included), so the gate works both
locally before a commit and in CI against the PR base.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_PREFIXES = ("templates/", "generated/")
MANIFEST_NAME = "manifest.json"
CHANGELOG_NAME = "CHANGELOG.md"
HEADING_PATTERN = re.compile(r"^## (?P<version>\S+) - (?P<date>\d{4}-\d{2}-\d{2})$")
GIT_TIMEOUT_SECONDS = 60


class GateError(Exception):
    pass


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
        raise GateError("git not found") from None
    except subprocess.TimeoutExpired:
        raise GateError(f"git {' '.join(args)} timed out") from None


def manifest_version(text: str, label: str) -> str:
    try:
        data = json.loads(text)
    except ValueError as error:
        raise GateError(f"{label} is not valid JSON: {error}") from None
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(version, str) or not version.strip():
        raise GateError(f"{label} has no version field")
    return version


def working_tree_version(repo: Path) -> str:
    manifest_path = repo / MANIFEST_NAME
    if not manifest_path.is_file():
        raise GateError(f"{MANIFEST_NAME} not found in {repo}")
    return manifest_version(
        manifest_path.read_text(encoding="utf-8"), MANIFEST_NAME
    )


def base_manifest_version(repo: Path, merge_base: str) -> str | None:
    result = run_git(repo, "show", f"{merge_base}:{MANIFEST_NAME}")
    if result.returncode != 0:
        return None
    return manifest_version(result.stdout, f"{merge_base}:{MANIFEST_NAME}")


def changed_paths(repo: Path, merge_base: str) -> set[str]:
    diff = run_git(repo, "diff", "--name-only", merge_base, "--")
    if diff.returncode != 0:
        raise GateError(f"git diff failed: {diff.stderr.strip()}")
    untracked = run_git(
        repo, "ls-files", "--others", "--exclude-standard"
    )
    if untracked.returncode != 0:
        raise GateError(f"git ls-files failed: {untracked.stderr.strip()}")
    paths = set(diff.stdout.splitlines()) | set(untracked.stdout.splitlines())
    return {path.strip() for path in paths if path.strip()}


def check_changelog_heading(repo: Path, version: str) -> None:
    changelog = repo / CHANGELOG_NAME
    if not changelog.is_file():
        raise GateError(f"{CHANGELOG_NAME} not found in {repo}")
    for line in changelog.read_text(encoding="utf-8").splitlines():
        if not line.startswith("## "):
            continue
        match = HEADING_PATTERN.match(line)
        if not match:
            raise GateError(
                f"{CHANGELOG_NAME} top heading {line!r} must be "
                f"'## {version} - YYYY-MM-DD'"
            )
        if match.group("version") != version:
            raise GateError(
                f"{CHANGELOG_NAME} top heading is for "
                f"{match.group('version')}, but the manifest version is "
                f"{version}; add a '## {version} - YYYY-MM-DD' entry on top"
            )
        try:
            datetime.date.fromisoformat(match.group("date"))
        except ValueError:
            raise GateError(
                f"{CHANGELOG_NAME} top heading date {match.group('date')!r} "
                "is not a real date"
            ) from None
        return
    raise GateError(f"{CHANGELOG_NAME} has no '## ' heading")


def run_gate(repo: Path, base: str) -> str:
    head = run_git(repo, "rev-parse", "--verify", "HEAD")
    if head.returncode != 0:
        # Repo without commits: everything is new; just require a matching
        # changelog heading for the current version.
        version = working_tree_version(repo)
        check_changelog_heading(repo, version)
        return f"no commits yet; changelog heading matches {version}"

    base_commit = run_git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
    if base_commit.returncode != 0:
        raise GateError(f"cannot resolve base revision {base!r}")
    merge_base = run_git(repo, "merge-base", base_commit.stdout.strip(), "HEAD")
    if merge_base.returncode != 0:
        raise GateError(
            f"cannot compute merge-base of {base!r} and HEAD: "
            f"{merge_base.stderr.strip()}"
        )
    merge_base_sha = merge_base.stdout.strip()

    changed = changed_paths(repo, merge_base_sha)
    payload_changed = sorted(
        path
        for path in changed
        if path == MANIFEST_NAME or path.startswith(PAYLOAD_PREFIXES)
    )
    current_version = working_tree_version(repo)
    base_version = base_manifest_version(repo, merge_base_sha)
    version_changed = base_version != current_version

    if payload_changed and not version_changed:
        raise GateError(
            "payload changed without a version bump "
            f"(version is still {current_version}); changed: "
            + ", ".join(payload_changed[:10])
        )
    if version_changed:
        check_changelog_heading(repo, current_version)
        return (
            f"version {base_version or '(new)'} -> {current_version}; "
            "changelog heading matches"
        )
    return "no payload change; no version bump required"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        default=str(PACK_ROOT),
        help="Repository to check (default: this pack checkout).",
    )
    parser.add_argument(
        "--base",
        default="HEAD",
        help=(
            "Base revision to measure changes from (CI passes the PR base "
            "SHA; the default HEAD checks uncommitted work only)."
        ),
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    repo = Path(args.repo).resolve()
    try:
        summary = run_gate(repo, args.base)
    except GateError as error:
        print(f"error: release payload gate: {error}", file=sys.stderr)
        return 1
    print(f"release payload gate: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
