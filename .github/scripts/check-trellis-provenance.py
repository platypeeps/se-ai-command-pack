#!/usr/bin/env python3
"""Coverage and integrity gate for platform files without an upstream receipt.

Trellis init writes no provenance record, so 53 tracked ``.agents``/``.codex``
files (plus ``.gitignore``, hashed as an explicit local durability policy)
would otherwise drift invisibly. This checker closes that gap with a
repo-local manifest (``.github/trellis-provenance.json``) and asserts that
tracked ``.claude`` adapter paths never become ignored again — the known
``trellis init`` re-run failure mode documented in CONTRIBUTING.md.

Check mode (default) is read-only and reports findings as ``<class>: <path>``
lines. ``--write`` regenerates the manifest; new paths are absorbed only when
named via repeatable ``--accept``. Exit status: 0 pass, 1 findings, 2
usage/environment/malformed-input error.

``.trellis/.template-hashes.json`` is gitignored and absent in CI, so the
manifest snapshots that registry's tracked-platform path list
(``templateReceipted``) and the live registry is consulted only when present.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MANIFEST_PATH = ".github/trellis-provenance.json"
PACK_PROVENANCE_PATH = ".sd-ai-command-pack/provenance.json"
TEMPLATE_REGISTRY_PATH = ".trellis/.template-hashes.json"
PLATFORM_DIRS = (".agents", ".claude", ".codex", ".gemini", ".github", ".opencode")
EXTRA_COVERED_UNIVERSE = (".gitignore",)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_KEYS = ("__version", "files", "repoOwn", "templateReceipted")


class CheckError(Exception):
    """Environment, usage, or malformed-input error (exit 2)."""


def fail(message: str) -> CheckError:
    return CheckError(message)


def run_git(repo: Path, *args: str, ok_status: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in ok_status:
        raise fail(f"git {' '.join(args)} exited {proc.returncode}: {proc.stderr.strip()}")
    return proc


def canonical_path(path: str) -> bool:
    if not path or path.startswith("/") or path.endswith("/"):
        return False
    parts = path.split("/")
    return all(part not in ("", ".", "..") for part in parts)


def reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict:
    obj: dict = {}
    for key, value in pairs:
        if key in obj:
            raise fail(f"duplicate JSON member: {key!r}")
        obj[key] = value
    return obj


def load_json_strict(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_pairs)
    except OSError as exc:
        raise fail(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise fail(f"invalid JSON in {path}: {exc}") from exc


def validate_path_list(values: object, label: str) -> list[str]:
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise fail(f"{label} must be an array of strings")
    seen: set[str] = set()
    for value in values:
        if not canonical_path(value):
            raise fail(f"{label} contains a non-canonical path: {value!r}")
        if value in seen:
            raise fail(f"{label} contains a duplicate entry: {value!r}")
        seen.add(value)
    return values


def load_manifest(path: Path) -> dict:
    data = load_json_strict(path)
    if not isinstance(data, dict):
        raise fail(f"{path} must be a JSON object")
    if sorted(data.keys()) != sorted(MANIFEST_KEYS):
        raise fail(f"{path} must have exactly the keys {list(MANIFEST_KEYS)}")
    if data["__version"] != 1:
        raise fail(f"{path} __version must be 1")
    files = data["files"]
    if not isinstance(files, dict):
        raise fail(f"{path} files must be an object")
    for file_path, digest in files.items():
        if not canonical_path(file_path):
            raise fail(f"{path} files contains a non-canonical path: {file_path!r}")
        if not isinstance(digest, str) or not SHA256_RE.match(digest):
            raise fail(f"{path} files[{file_path!r}] is not a lowercase 64-char sha256")
    repo_own = validate_path_list(data["repoOwn"], f"{path} repoOwn")
    template_receipted = validate_path_list(data["templateReceipted"], f"{path} templateReceipted")
    sets = {
        "files": set(files),
        "repoOwn": set(repo_own),
        "templateReceipted": set(template_receipted),
    }
    names = list(sets)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            overlap = sets[left] & sets[right]
            if overlap:
                raise fail(f"{path}: {left} and {right} overlap on {sorted(overlap)[:3]}")
    return data


def load_pack_provenance(repo: Path) -> set[str]:
    data = load_json_strict(repo / PACK_PROVENANCE_PATH)
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise fail(f"{PACK_PROVENANCE_PATH} has no files object")
    return set(data["files"].keys())


def load_template_registry(repo: Path) -> set[str] | None:
    """Validated key set of the live Trellis registry, or None when absent."""
    registry = repo / TEMPLATE_REGISTRY_PATH
    if not registry.exists():
        return None
    data = load_json_strict(registry)
    if not isinstance(data, dict) or data.get("__version") != 2:
        raise fail(f"{TEMPLATE_REGISTRY_PATH} is not a v2 registry")
    hashes = data.get("hashes")
    if not isinstance(hashes, dict):
        raise fail(f"{TEMPLATE_REGISTRY_PATH} has no hashes object")
    for key, value in hashes.items():
        if not canonical_path(key):
            raise fail(f"{TEMPLATE_REGISTRY_PATH} has a non-canonical path: {key!r}")
        if not isinstance(value, str) or not SHA256_RE.match(value):
            raise fail(f"{TEMPLATE_REGISTRY_PATH} hashes[{key!r}] is not a lowercase 64-char sha256")
    return set(hashes.keys())


def tracked_platform_files(repo: Path) -> list[str]:
    proc = run_git(repo, "ls-files", "-z", "--", *PLATFORM_DIRS, *EXTRA_COVERED_UNIVERSE)
    return [p for p in proc.stdout.split("\0") if p]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_ignored_tracked_paths(repo: Path, paths: list[str]) -> list[str]:
    """Tracked paths the current ignore rules would ignore (fail-closed).

    Exit 0 means at least one path is ignored (stdout lists them), 1 means
    none are; anything else — e.g. 128 — is an environment error, never a
    pass.
    """
    if not paths:
        return []
    proc = run_git(repo, "check-ignore", "--no-index", "--", *paths, ok_status=(0, 1))
    if proc.returncode == 1:
        return []
    return [p for p in proc.stdout.splitlines() if p]


def run_check(repo: Path) -> int:
    manifest_file = repo / MANIFEST_PATH
    if not manifest_file.exists():
        raise fail(f"{MANIFEST_PATH} not found; run --write to create it")
    manifest = load_manifest(manifest_file)
    pack_covered = load_pack_provenance(repo)
    tracked = tracked_platform_files(repo)
    tracked_set = set(tracked)

    findings: list[str] = []

    covered = (
        pack_covered
        | set(manifest["files"])
        | set(manifest["repoOwn"])
        | set(manifest["templateReceipted"])
    )
    findings.extend(f"uncovered: {path}" for path in tracked if path not in covered)

    for path, expected in sorted(manifest["files"].items()):
        absolute = repo / path
        if absolute.is_symlink():
            findings.append(f"not-regular-file: {path}")
            continue
        if path not in tracked_set or not absolute.exists():
            findings.append(f"missing: {path}")
            continue
        if not absolute.is_file():
            findings.append(f"not-regular-file: {path}")
            continue
        if sha256_file(absolute) != expected:
            findings.append(f"drifted: {path}")

    claude_tracked = [p for p in tracked if p.startswith(".claude/")]
    findings.extend(
        f"ignored-tracked-path: {path}"
        for path in check_ignored_tracked_paths(repo, claude_tracked)
    )

    registry_keys = load_template_registry(repo)
    if registry_keys is not None:
        live_platform = registry_keys & tracked_set
        if live_platform != set(manifest["templateReceipted"]):
            findings.append(f"template-snapshot-stale: {TEMPLATE_REGISTRY_PATH}")

    for line in findings:
        print(line)
    if findings:
        print(f"trellis-provenance check: {len(findings)} finding(s)")
        return 1
    print(
        f"trellis-provenance check: ok ({len(manifest['files'])} hashed, "
        f"{len(tracked)} tracked platform files covered)"
    )
    return 0


def run_write(repo: Path, accepted: list[str]) -> int:
    manifest_file = repo / MANIFEST_PATH
    if manifest_file.exists():
        manifest = load_manifest(manifest_file)
    else:
        manifest = {"__version": 1, "files": {}, "repoOwn": [], "templateReceipted": []}
    pack_covered = load_pack_provenance(repo)
    tracked = tracked_platform_files(repo)
    tracked_set = set(tracked)
    accepted_set = set(accepted)
    for path in accepted:
        if path not in tracked_set:
            raise fail(f"--accept path is not a tracked platform file: {path}")

    registry_keys = load_template_registry(repo)
    if registry_keys is None:
        template_receipted = list(manifest["templateReceipted"])
        print(f"notice: {TEMPLATE_REGISTRY_PATH} absent; keeping existing snapshot")
    else:
        template_receipted = sorted(registry_keys & tracked_set)

    repo_own_set = set(manifest["repoOwn"])
    other_covered = repo_own_set | set(template_receipted) | pack_covered
    already_covered = sorted(accepted_set & other_covered)
    if already_covered:
        raise fail(
            "--accept paths already covered by another receipt: "
            + ", ".join(already_covered)
        )

    candidate_files: dict[str, str] = {}
    for path in sorted(set(manifest["files"]) | accepted_set):
        if path not in tracked_set:
            print(f"removed: {path}")
            continue
        if path in other_covered:
            print(f"removed (now covered elsewhere): {path}")
            continue
        absolute = repo / path
        if absolute.is_symlink() or not absolute.is_file():
            raise fail(f"refusing to hash a non-regular file: {path}")
        digest = sha256_file(absolute)
        previous = manifest["files"].get(path)
        if previous is None:
            print(f"added: {path}")
        elif previous != digest:
            print(f"rehashed: {path}")
        candidate_files[path] = digest

    covered = (
        pack_covered
        | set(candidate_files)
        | set(manifest["repoOwn"])
        | set(template_receipted)
    )
    unabsorbed = [p for p in tracked if p not in covered]
    if unabsorbed:
        for path in unabsorbed:
            print(f"uncovered: {path} (name it via --accept or curate repoOwn by hand)")
        print(f"trellis-provenance write refused: {len(unabsorbed)} unclassified path(s)")
        return 1

    candidate = {
        "__version": 1,
        "files": dict(sorted(candidate_files.items())),
        "repoOwn": sorted(manifest["repoOwn"]),
        "templateReceipted": template_receipted,
    }
    payload = json.dumps(candidate, indent=2, sort_keys=False) + "\n"
    fd, temp_name = tempfile.mkstemp(dir=str(manifest_file.parent), prefix=".trellis-provenance-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temp_name, manifest_file)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temp_name)
        raise
    print(f"trellis-provenance write: {len(candidate_files)} file(s) hashed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".", help="repository root (default: cwd)")
    parser.add_argument("--write", action="store_true", help="regenerate the manifest")
    parser.add_argument(
        "--accept",
        action="append",
        default=[],
        metavar="PATH",
        help="with --write: absorb this new uncovered path into files (repeatable)",
    )
    args = parser.parse_args(argv)
    if args.accept and not args.write:
        parser.error("--accept requires --write")
    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        print(f"error: {repo} is not a git repository root", file=sys.stderr)
        return 2
    try:
        if args.write:
            return run_write(repo, args.accept)
        return run_check(repo)
    except CheckError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: filesystem failure: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
