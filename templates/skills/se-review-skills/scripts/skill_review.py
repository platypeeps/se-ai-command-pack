#!/usr/bin/env python3
"""Build a deterministic inventory for a bounded skill review.

The script reports facts and candidate signals. It never creates findings,
tasks, or edits. Semantic judgment remains with the calling skill.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Sequence

SCHEMA_VERSION = 3
TRANSPORT_SCHEMA_VERSION = 1
MINIMUM_PYTHON = (3, 9)
GIT_TIMEOUT_SECONDS = 15
MAX_TEXT_BYTES = 2_000_000
MAX_EXISTING_INVENTORY_BYTES = 64 * 1024 * 1024
MAX_ENVELOPE_ERROR_CHARS = 500
MAX_DESCRIPTION_SIMILARITY_PAIRS = 10_000
HASH_CHUNK_BYTES = 128 * 1024
FIRST_PARTY_REMOTES = {
    "se-ai-command-pack": "github.com/platypeeps/se-ai-command-pack",
    "sd-ai-command-pack": "github.com/platypeeps/sd-ai-command-pack",
}
IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "build",
        "dist",
        "node_modules",
        "vendor",
        "__pycache__",
    }
)
RECEIPT_NAMES = (
    ".se-ai-command-pack/provenance.json",
    ".sd-ai-command-pack/provenance.json",
)
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCED_BLOCK_PATTERN = re.compile(
    r"^```([^\n]*)\n(.*?)^```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
WORD_PATTERN = re.compile(r"\b[\w'-]+\b")
INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
SCRIPT_SIGNAL_PATTERNS = {
    "structured-parsing": re.compile(
        r"\b(json|ya?ml|toml|csv|xml|jq|parse|deserialize|loads?)\b",
        re.IGNORECASE,
    ),
    "normalization-or-transformation": re.compile(
        r"\b(normalize|canonicali[sz]e|transform|convert|sort|deduplicat)\w*\b",
        re.IGNORECASE,
    ),
    "validation-or-schema": re.compile(
        r"\b(validate|validation|schema|assert|lint|check)\w*\b",
        re.IGNORECASE,
    ),
    "hashing": re.compile(
        r"\b(sha(?:1|224|256|384|512)?|hash|digest|checksum)\w*\b",
        re.IGNORECASE,
    ),
    "path-resolution-or-inventory": re.compile(
        r"\b(realpath|resolve|glob|find|inventory|manifest|pathlib|Path)\b",
        re.IGNORECASE,
    ),
}


class ReviewError(Exception):
    """Expected invalid-input or unsafe-boundary failure."""


@dataclass(frozen=True)
class RegistryData:
    families: dict[str, str]
    family_order: tuple[str, ...]
    skill_order: tuple[str, ...]
    platforms: tuple[str, ...]
    shared_references: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class PackageContext:
    root: Path
    git_root: Path | None
    name: str | None
    version: str | None
    manifest: dict[str, Any] | None
    registry: RegistryData
    remote: str | None
    owner_kind: str
    allowed_template_root: Path | None


@dataclass(frozen=True)
class ResolvedSkill:
    observed: Path
    canonical: Path
    context: PackageContext
    source_role: str
    drift: str
    mapping_evidence: str
    installations: tuple[InstalledCopy, ...]


@dataclass(frozen=True)
class InstalledCopy:
    path: Path
    root: Path
    platform: str | None
    observed_hash: str
    drift: str
    mapping_evidence: str


@dataclass(frozen=True)
class DestinationState:
    path: Path
    fingerprint: tuple[int, int, int, int, int]


def _read_regular_text(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ReviewError(f"unsafe or missing regular file: {path}")
    try:
        size = path.stat().st_size
        if size > MAX_TEXT_BYTES:
            raise ReviewError(
                f"refusing text file larger than {MAX_TEXT_BYTES} bytes: {path}"
            )
        return path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as error:
        raise ReviewError(f"cannot read UTF-8 file {path}: {error}") from None


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if path.is_symlink() or not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _sha256(path: Path) -> str:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while chunk := handle.read(HASH_CHUNK_BYTES):
                digest.update(chunk)
    except OSError as error:
        raise ReviewError(f"cannot hash {path}: {error}") from None
    return "sha256:" + digest.hexdigest()


def _run_git(path: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _git_root(path: Path) -> Path | None:
    start = path if path.is_dir() else path.parent
    value = _run_git(start, "rev-parse", "--show-toplevel")
    return Path(value).resolve() if value else None


def _normalized_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    value = remote.strip()
    if value.startswith("git@") and ":" in value:
        host, path = value[4:].split(":", 1)
        value = f"{host}/{path}"
    value = re.sub(r"^[a-z]+://", "", value, flags=re.IGNORECASE)
    value = value.removeprefix("git@")
    return value.casefold().strip("/").removesuffix(".git")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _assignment(tree: ast.Module, name: str) -> ast.AST | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return node.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return node.value
    return None


def _string_value(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_value(call: ast.Call, name: str, position: int) -> str | None:
    for keyword in call.keywords:
        if keyword.arg == name:
            return _string_value(keyword.value)
    if len(call.args) > position:
        return _string_value(call.args[position])
    return None


def _parse_registry(path: Path) -> RegistryData:
    if not path.is_file() or path.is_symlink():
        return RegistryData({}, (), (), (), {})
    try:
        tree = ast.parse(_read_regular_text(path), filename=str(path))
    except SyntaxError:
        return RegistryData({}, (), (), (), {})

    family_order: list[str] = []
    labels = _assignment(tree, "FAMILY_LABELS")
    if isinstance(labels, ast.Dict):
        family_order = [
            value
            for key in labels.keys
            if (value := _string_value(key)) is not None
        ]

    families: dict[str, str] = {}
    skill_order: list[str] = []
    for assignment_name, constructor, family_position in (
        ("SKILLS", "SkillInfo", 1),
        ("COMMAND_REGISTRY", "CommandInfo", 2),
    ):
        value = _assignment(tree, assignment_name)
        if not isinstance(value, (ast.Tuple, ast.List)):
            continue
        for entry in value.elts:
            if not isinstance(entry, ast.Call):
                continue
            function = entry.func
            function_name = function.id if isinstance(function, ast.Name) else None
            if function_name != constructor:
                continue
            skill_name = _call_value(entry, "name", 0)
            family = _call_value(entry, "family", family_position)
            if skill_name and family:
                if skill_name not in families:
                    skill_order.append(skill_name)
                families[skill_name] = family

    platforms: list[str] = []
    registry = _assignment(tree, "PLATFORM_REGISTRY")
    if isinstance(registry, ast.Dict):
        platforms = [
            value
            for key in registry.keys
            if (value := _string_value(key)) is not None
        ]

    shared_references: dict[str, tuple[str, ...]] = {}
    shared = _assignment(tree, "SHARED_REFERENCES")
    if isinstance(shared, ast.Dict):
        for key_node, value_node in zip(shared.keys, shared.values):
            key = _string_value(key_node)
            if key is None or not isinstance(value_node, (ast.Tuple, ast.List)):
                continue
            consumers = tuple(
                value
                for entry in value_node.elts
                if (value := _string_value(entry)) is not None
            )
            shared_references[key] = consumers
    return RegistryData(
        families,
        tuple(family_order),
        tuple(skill_order),
        tuple(sorted(platforms)),
        shared_references,
    )


def _package_context(root: Path) -> PackageContext:
    root = root.resolve()
    git_root = _git_root(root)
    package_root = git_root or root
    manifest = _read_json_object(package_root / "manifest.json")
    name_value = manifest.get("name") if manifest else None
    version_value = manifest.get("version") if manifest else None
    name = name_value if isinstance(name_value, str) else None
    version = version_value if isinstance(version_value, str) else None
    registry = _parse_registry(package_root / "installer" / "registry.py")
    remote = _run_git(package_root, "config", "--get", "remote.origin.url")
    normalized = _normalized_remote(remote)

    owner_kind = "unresolved"
    expected = FIRST_PARTY_REMOTES.get(name or "")
    if expected:
        if normalized == expected:
            owner_kind = (
                "se-upstream" if name == "se-ai-command-pack" else "sd-upstream"
            )
    elif git_root is not None:
        owner_kind = "repo-local"

    allowed: Path | None = None
    if name == "se-ai-command-pack":
        allowed = package_root / "templates" / "skills"
    elif name == "sd-ai-command-pack":
        allowed = package_root / "templates"

    return PackageContext(
        root=package_root,
        git_root=git_root,
        name=name,
        version=version,
        manifest=manifest,
        registry=registry,
        remote=remote,
        owner_kind=owner_kind,
        allowed_template_root=allowed.resolve() if allowed else None,
    )


def _validate_bounded_root(root: Path) -> Path:
    resolved = root.expanduser().resolve()
    filesystem_root = Path(resolved.anchor).resolve()
    if resolved in {filesystem_root, Path.home().resolve()}:
        raise ReviewError(
            f"refusing unbounded filesystem or home-directory discovery: {resolved}"
        )
    return resolved


def _crosses_symlink(path: Path) -> bool:
    return path.is_symlink() or any(parent.is_symlink() for parent in path.parents)


def _walk_skill_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for current, directories, files in os.walk(root, followlinks=False):
        directories[:] = sorted(
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES
            and not (Path(current) / name).is_symlink()
        )
        if "SKILL.md" in files:
            found.append((Path(current) / "SKILL.md").resolve())
        if len(found) > 1000:
            raise ReviewError(f"skill discovery exceeded 1000 files under {root}")
    return sorted(found)


def _discover(
    context: PackageContext,
    bounded_root: Path,
    root_was_explicit: bool,
) -> list[Path]:
    if root_was_explicit and bounded_root != context.root:
        return _walk_skill_files(bounded_root)
    if context.name == "se-ai-command-pack":
        base = context.root / "templates" / "skills"
        return sorted(
            path.resolve()
            for path in base.glob("*/SKILL.md")
            if path.parent.name != "_shared" and not path.is_symlink()
        )
    if context.name == "sd-ai-command-pack":
        base = context.root / "templates" / ".agents" / "skills"
        return sorted(
            path.resolve()
            for path in base.glob("*/SKILL.md")
            if not path.is_symlink()
        )
    return _walk_skill_files(context.root)


def _frontmatter(text: str, label: str) -> tuple[dict[str, str], str, tuple[str, ...]]:
    if not text.startswith("---\n"):
        raise ReviewError(f"{label}: missing frontmatter opening")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ReviewError(f"{label}: missing frontmatter closing")
    raw = text[4 : end + 1]
    body = text[end + 5 :]
    values: dict[str, str] = {}
    keys: list[str] = []
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        keys.append(key)
        if value in {"|", ">", "|-", ">-"}:
            continuation: list[str] = []
            while index < len(lines) and (
                not lines[index] or lines[index][0].isspace()
            ):
                continuation.append(lines[index].strip())
                index += 1
            values[key] = " ".join(part for part in continuation if part)
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            try:
                parsed = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                parsed = value[1:-1]
            values[key] = str(parsed)
        else:
            values[key] = value
    return values, body, tuple(keys)


def _candidate_path(
    value: str,
    root: Path,
    *,
    enforce_root: bool,
) -> Path | None:
    supplied = Path(value).expanduser()
    candidates = [supplied] if supplied.is_absolute() else [root / supplied]
    for candidate in candidates:
        if not candidate.exists():
            continue
        resolved = candidate.resolve()
        if enforce_root and not _is_relative_to(resolved, root):
            raise ReviewError(f"skill path escapes the bounded root: {value}")
        if candidate.is_symlink():
            raise ReviewError(f"skill path crosses a symlink boundary: {candidate}")
        if candidate.is_dir():
            candidate = candidate / "SKILL.md"
        if candidate.name != "SKILL.md":
            raise ReviewError(f"skill path must name a skill directory or SKILL.md: {value}")
        return candidate.absolute()
    return None


def _manifest_rows(context: PackageContext) -> list[dict[str, Any]]:
    rows = context.manifest.get("files", []) if context.manifest else []
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _safe_manifest_source(
    context: PackageContext, source: str
) -> Path | None:
    source_path = Path(source)
    if source_path.is_absolute() or ".." in source_path.parts:
        return None
    supplied = context.root / source_path
    current = context.root
    for part in source_path.parts:
        current /= part
        if current.is_symlink():
            return None
    canonical = supplied.resolve()
    if not _is_relative_to(canonical, context.root):
        return None
    allowed = context.allowed_template_root
    if allowed is not None and not _is_relative_to(canonical, allowed):
        return None
    if canonical.name != "SKILL.md" or not canonical.is_file():
        return None
    return canonical


def _manifest_mapping(
    observed: Path, context: PackageContext
) -> tuple[Path, str | None, str] | None:
    if context.owner_kind not in {"sd-upstream", "se-upstream", "repo-local"}:
        return None
    observed_parts = observed.resolve().parts
    for row in _manifest_rows(context):
        target = row.get("target")
        source = row.get("source")
        if not isinstance(target, str) or not isinstance(source, str):
            continue
        target_path = Path(target)
        if target_path.is_absolute() or ".." in target_path.parts:
            continue
        target_parts = target_path.parts
        if not target_parts or len(observed_parts) < len(target_parts):
            continue
        if observed_parts[-len(target_parts) :] != target_parts:
            continue
        canonical = _safe_manifest_source(context, source)
        if canonical is None:
            continue
        platform = row.get("platform")
        return (
            canonical,
            platform if isinstance(platform, str) else None,
            f"verified manifest target {target!r} in {context.root}",
        )
    return None


def _installed_mapping(
    observed: Path,
) -> tuple[Path, PackageContext, str | None, str] | None:
    for base in observed.parents:
        for receipt_name in RECEIPT_NAMES:
            receipt_path = base / receipt_name
            receipt = _read_json_object(receipt_path)
            if receipt is None:
                continue
            source_value = receipt.get("sourceRoot")
            if not isinstance(source_value, str) or not source_value.strip():
                continue
            supplied_source_root = Path(source_value).expanduser()
            if supplied_source_root.is_symlink() or not supplied_source_root.is_dir():
                continue
            source_root = supplied_source_root.resolve()
            context = _package_context(source_root)
            if context.name not in FIRST_PARTY_REMOTES:
                continue
            try:
                target = observed.relative_to(base).as_posix()
            except ValueError:
                continue
            for row in _manifest_rows(context):
                if row.get("target") != target:
                    continue
                source = row.get("source")
                if not isinstance(source, str):
                    continue
                canonical = _safe_manifest_source(context, source)
                if canonical is None:
                    continue
                platform = row.get("platform")
                return (
                    canonical,
                    context,
                    platform if isinstance(platform, str) else None,
                    receipt_path.as_posix(),
                )
    return None


def _role_for(canonical: Path, observed: Path, context: PackageContext) -> str:
    if observed.resolve() != canonical.resolve():
        return "installed-copy"
    allowed = context.allowed_template_root
    if allowed is not None and not _is_relative_to(canonical, allowed):
        return "local-override"
    relative = canonical.relative_to(context.root).as_posix()
    if context.name == "sd-ai-command-pack" and relative.startswith(
        ("templates/.claude/", "templates/.gemini/", "templates/.github/")
    ):
        return "generated-template-adapter"
    return "authored-template"


def _resolve_path(
    path: Path,
    context_hint: PackageContext | None = None,
    *,
    installation_root: Path | None = None,
    platform: str | None = None,
) -> ResolvedSkill:
    observed = path.absolute()
    if observed.is_symlink() or any(parent.is_symlink() for parent in observed.parents):
        raise ReviewError(f"skill path crosses a symlink boundary: {observed}")
    manifest_mapping = (
        _manifest_mapping(observed, context_hint) if context_hint is not None else None
    )
    if manifest_mapping:
        canonical, mapped_platform, evidence = manifest_mapping
        context = context_hint
        drift = (
            "canonical-match"
            if _sha256(observed) == _sha256(canonical)
            else "installed-drift"
        )
        copy = InstalledCopy(
            observed,
            installation_root or observed.parent.parent,
            platform or mapped_platform,
            _sha256(observed),
            drift,
            evidence,
        )
        return ResolvedSkill(
            observed,
            canonical,
            context,
            "installed-copy",
            drift,
            evidence,
            (copy,),
        )

    mapping = _installed_mapping(observed)
    if mapping:
        canonical, context, mapped_platform, evidence = mapping
        drift = (
            "canonical-match"
            if _sha256(observed) == _sha256(canonical)
            else "installed-drift"
        )
        copy = InstalledCopy(
            observed,
            installation_root or observed.parent.parent,
            platform or mapped_platform,
            _sha256(observed),
            drift,
            evidence,
        )
        return ResolvedSkill(
            observed,
            canonical,
            context,
            "installed-copy",
            drift,
            evidence,
            (copy,),
        )

    if installation_root is not None:
        context = _package_context(observed.parent)
        evidence = "unmatched installed copy; canonical ownership unresolved"
        copy = InstalledCopy(
            observed,
            installation_root,
            platform,
            _sha256(observed),
            "unresolved",
            evidence,
        )
        return ResolvedSkill(
            observed,
            observed.resolve(),
            context,
            "installed-copy-unowned",
            "unresolved",
            evidence,
            (copy,),
        )

    if context_hint is not None and _is_relative_to(observed.resolve(), context_hint.root):
        context = context_hint
    else:
        context = _package_context(observed.parent)
    canonical = observed.resolve()
    role = _role_for(canonical, observed, context)
    return ResolvedSkill(
        observed,
        canonical,
        context,
        role,
        "canonical-match",
        "canonical path inside repository",
        (),
    )


def _select_paths(
    context: PackageContext,
    root: Path,
    skill_specs: Sequence[str],
    family: str | None,
    scope: str | None,
    root_was_explicit: bool,
    *,
    allow_empty: bool = False,
) -> list[ResolvedSkill]:
    discovered = _discover(context, root, root_was_explicit)
    selected_paths: list[Path] = []
    for spec in skill_specs:
        path = _candidate_path(spec, root, enforce_root=root_was_explicit)
        if path is not None:
            selected_paths.append(path)
            continue
        matches = [path for path in discovered if path.parent.name == spec]
        if not matches:
            raise ReviewError(f"unknown skill in bounded scope: {spec}")
        if len(matches) > 1:
            labels = ", ".join(str(path) for path in matches)
            raise ReviewError(f"ambiguous skill {spec!r}; matches: {labels}")
        selected_paths.append(matches[0])

    if not selected_paths:
        selected_paths = discovered
    if not selected_paths:
        if allow_empty and not skill_specs:
            return []
        raise ReviewError(f"no skills found under bounded root: {root}")

    if not skill_specs and context.name is None and not root_was_explicit:
        declared_roots = {path.parent.parent for path in selected_paths}
        if len(declared_roots) > 1:
            raise ReviewError(
                "multiple unrelated skill roots found; pass --root or --skill explicitly"
            )

    resolved = [_resolve_path(path, context) for path in selected_paths]
    if family:
        resolved = [
            item
            for item in resolved
            if item.context.registry.families.get(item.canonical.parent.name) == family
        ]
        if not resolved:
            raise ReviewError(f"family {family!r} has no skills in the bounded scope")

    if scope == "skill" and len(resolved) != 1:
        raise ReviewError("scope=skill requires exactly one resolved skill")
    if scope == "family" and not family:
        raise ReviewError("scope=family requires --family")
    registry_positions = {
        str(item.context.root): {
            name: index
            for index, name in enumerate(item.context.registry.skill_order)
        }
        for item in resolved
    }

    def sort_key(item: ResolvedSkill) -> tuple[str, int, str]:
        root_key = str(item.context.root)
        skill_name = item.canonical.parent.name
        positions = registry_positions[root_key]
        return (root_key, positions.get(skill_name, len(positions)), skill_name)

    return sorted(resolved, key=sort_key)


def _manifest_install_roots(
    context: PackageContext, home: Path
) -> list[tuple[Path, tuple[str, ...], str]]:
    roots: dict[Path, set[str]] = {}
    for row in _manifest_rows(context):
        target = row.get("target")
        source = row.get("source")
        if not isinstance(target, str) or not isinstance(source, str):
            continue
        target_path = Path(target)
        if (
            target_path.is_absolute()
            or ".." in target_path.parts
            or target_path.name != "SKILL.md"
            or len(target_path.parts) < 3
        ):
            continue
        if _safe_manifest_source(context, source) is None:
            continue
        install_root = (home / target_path.parent.parent).absolute()
        platform = row.get("platform")
        roots.setdefault(install_root, set())
        if isinstance(platform, str):
            roots[install_root].add(platform)
    return [
        (path, tuple(sorted(platforms)), "manifest")
        for path, platforms in sorted(roots.items(), key=lambda item: str(item[0]))
    ]


def _validate_installed_root(path: Path) -> Path:
    supplied = path.expanduser().absolute()
    if _crosses_symlink(supplied):
        raise ReviewError(f"installed skill root crosses a symlink boundary: {supplied}")
    resolved = _validate_bounded_root(supplied)
    if not resolved.exists():
        raise ReviewError(f"installed skill root does not exist: {resolved}")
    if not resolved.is_dir():
        raise ReviewError(f"installed skill root is not a directory: {resolved}")
    return resolved


def _discover_installed(
    context: PackageContext,
    mode: str,
    explicit_roots: Sequence[Path],
) -> tuple[list[ResolvedSkill], list[dict[str, Any]]]:
    if mode not in {"auto", "off"}:
        raise ReviewError(f"unknown installed discovery mode: {mode}")
    if mode == "off" and explicit_roots:
        raise ReviewError("installed roots cannot be supplied when installed discovery is off")
    if mode == "off":
        return [], []

    root_specs: list[tuple[Path, tuple[str, ...], str]]
    if explicit_roots:
        root_specs = [
            (_validate_installed_root(path), (), "explicit") for path in explicit_roots
        ]
    else:
        root_specs = _manifest_install_roots(context, Path.home())

    installed: list[ResolvedSkill] = []
    root_records: list[dict[str, Any]] = []
    seen_roots: set[Path] = set()
    for candidate, platforms, source in root_specs:
        absolute = candidate.expanduser().absolute()
        if absolute in seen_roots:
            continue
        seen_roots.add(absolute)
        if source == "manifest":
            if absolute.is_symlink() or any(
                parent.is_symlink() for parent in absolute.parents
            ):
                root_records.append(
                    {
                        "path": str(absolute),
                        "source": source,
                        "platforms": list(platforms),
                        "status": "skipped-symlink",
                        "skillsFound": 0,
                        "symlinksSkipped": 0,
                    }
                )
                continue
            if not absolute.exists():
                root_records.append(
                    {
                        "path": str(absolute),
                        "source": source,
                        "platforms": list(platforms),
                        "status": "missing",
                        "skillsFound": 0,
                        "symlinksSkipped": 0,
                    }
                )
                continue
            if not absolute.is_dir():
                root_records.append(
                    {
                        "path": str(absolute),
                        "source": source,
                        "platforms": list(platforms),
                        "status": "not-directory",
                        "skillsFound": 0,
                        "symlinksSkipped": 0,
                    }
                )
                continue

        paths: list[Path] = []
        symlinks_skipped = 0
        for path in sorted(absolute.glob("*/SKILL.md")):
            if path.is_symlink() or path.parent.is_symlink():
                symlinks_skipped += 1
                continue
            if path.is_file():
                paths.append(path.absolute())
        for path in paths:
            installed.append(
                _resolve_path(
                    path,
                    context,
                    installation_root=absolute,
                    platform=platforms[0] if len(platforms) == 1 else None,
                )
            )
        root_records.append(
            {
                "path": str(absolute),
                "source": source,
                "platforms": list(platforms),
                "status": "scanned",
                "skillsFound": len(paths),
                "symlinksSkipped": symlinks_skipped,
            }
        )
    return installed, root_records


def _skill_name(item: ResolvedSkill) -> str:
    text = _read_regular_text(item.canonical)
    metadata, _, _ = _frontmatter(text, str(item.canonical))
    return metadata.get("name") or item.canonical.parent.name


def _deduplication_key(item: ResolvedSkill) -> tuple[str, ...]:
    if item.context.owner_kind in {"sd-upstream", "se-upstream", "repo-local"}:
        return ("canonical", str(item.context.root), str(item.canonical.resolve()))
    return ("unowned-content", _skill_name(item), _sha256(item.canonical))


def _deduplicate_resolved(items: Sequence[ResolvedSkill]) -> list[ResolvedSkill]:
    groups: dict[tuple[str, ...], list[ResolvedSkill]] = {}
    for item in items:
        groups.setdefault(_deduplication_key(item), []).append(item)

    deduplicated: list[ResolvedSkill] = []
    for group in groups.values():
        primary = next(
            (
                item
                for item in group
                if item.observed.resolve() == item.canonical.resolve()
            ),
            group[0],
        )
        installations = {
            str(copy.path): copy
            for item in group
            for copy in item.installations
        }
        ordered = tuple(
            installations[path] for path in sorted(installations)
        )
        aggregate_drift = primary.drift
        if any(copy.drift == "installed-drift" for copy in ordered):
            aggregate_drift = "installed-drift"
        evidence = primary.mapping_evidence
        if ordered:
            copy_label = "copy" if len(ordered) == 1 else "copies"
            evidence = (
                f"{evidence}; deduplicated {len(ordered)} installed "
                f"{copy_label} by canonical identity"
            )
        deduplicated.append(
            replace(
                primary,
                drift=aggregate_drift,
                mapping_evidence=evidence,
                installations=ordered,
            )
        )

    registry_positions = {
        str(item.context.root): {
            name: index
            for index, name in enumerate(item.context.registry.skill_order)
        }
        for item in deduplicated
    }

    def sort_key(item: ResolvedSkill) -> tuple[str, int, str, str]:
        root_key = str(item.context.root)
        name = _skill_name(item)
        positions = registry_positions[root_key]
        return (
            root_key,
            positions.get(name, len(positions)),
            name,
            str(item.canonical),
        )

    return sorted(deduplicated, key=sort_key)


def _paragraphs(body: str) -> list[str]:
    result: list[str] = []
    for paragraph in re.split(r"\n\s*\n", body):
        normalized = " ".join(paragraph.split())
        if len(normalized) >= 80 and not normalized.startswith("#"):
            result.append(normalized)
    return result


def _declared_arguments(body: str) -> list[str]:
    start = re.search(r"^## Arguments\s*$", body, re.MULTILINE)
    if start is None:
        return []
    remainder = body[start.end() :]
    end = re.search(r"^## [^#]", remainder, re.MULTILINE)
    section = remainder[: end.start()] if end else remainder
    return sorted(set(INLINE_CODE_PATTERN.findall(section)))


def _script_candidate_signals(
    related: Sequence[dict[str, str]],
) -> tuple[int, list[dict[str, Any]]]:
    block_count = 0
    candidates: list[dict[str, Any]] = []
    for entry in related:
        path = Path(entry["path"])
        if path.suffix.casefold() != ".md":
            continue
        text = _read_regular_text(path)
        for match in FENCED_BLOCK_PATTERN.finditer(text):
            block_count += 1
            language = match.group(1).strip().casefold() or "plain"
            content = match.group(2)
            kinds = [
                name
                for name, pattern in SCRIPT_SIGNAL_PATTERNS.items()
                if pattern.search(content)
            ]
            content_lines = [line for line in content.splitlines() if line.strip()]
            if language in {"bash", "console", "fish", "powershell", "sh", "zsh"}:
                if len(content_lines) >= 2:
                    kinds.append("stable-command-orchestration")
            if not kinds:
                continue
            candidates.append(
                {
                    "path": str(path),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "language": language,
                    "lineCount": len(content.splitlines()),
                    "candidateKinds": sorted(set(kinds)),
                }
            )
    return block_count, candidates


def _test_text_references(
    context: PackageContext, skill_name: str
) -> list[dict[str, Any]]:
    tests = context.root / "tests"
    if not tests.is_dir():
        return []
    matches: list[dict[str, Any]] = []
    for path in sorted(tests.glob("test*.py")):
        try:
            lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
        except (OSError, UnicodeError):
            continue
        for number, line in enumerate(lines, start=1):
            if skill_name in line:
                matches.append(
                    {
                        "path": path.relative_to(context.root).as_posix(),
                        "line": number,
                        "classification": "substring-reference",
                        "behavioralPinVerified": False,
                    }
                )
                if len(matches) == 25:
                    return matches
    return matches


def _is_ignored_related_path(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    return path.suffix.casefold() == ".pyc" or any(
        part in IGNORED_DIRECTORIES for part in relative.parts
    )


def _related_templates(item: ResolvedSkill) -> list[dict[str, str]]:
    context = item.context
    skill_name = item.canonical.parent.name
    candidates: dict[Path, str] = {}
    for path in item.canonical.parent.rglob("*"):
        if (
            path.is_file()
            and not path.is_symlink()
            and not _is_ignored_related_path(path, item.canonical.parent)
        ):
            candidates[path.resolve()] = "authored-template"
    for relative, consumers in context.registry.shared_references.items():
        if skill_name not in consumers:
            continue
        source = Path(relative)
        if source.is_absolute() or ".." in source.parts:
            raise ReviewError(
                f"shared reference escapes the template root: {relative}"
            )
        source_root = context.allowed_template_root or context.root
        candidate = source_root / source
        if candidate.is_symlink() or not candidate.is_file():
            raise ReviewError(f"unsafe or missing shared reference: {candidate}")
        path = candidate.resolve()
        allowed = context.allowed_template_root
        if allowed is not None and not _is_relative_to(path, allowed):
            raise ReviewError(
                f"shared reference escapes the template allowlist: {relative}"
            )
        candidates[path] = "authored-shared-reference"
    if context.name == "sd-ai-command-pack":
        short = skill_name.removeprefix("sd-")
        for relative in (
            f"templates/.commands/{skill_name}.md",
            f"templates/.claude/commands/sd/{short}.md",
            f"templates/.gemini/commands/sd/{short}.toml",
            f"templates/.github/prompts/{skill_name}.prompt.md",
        ):
            path = (context.root / relative).resolve()
            if path.is_file() and not path.is_symlink():
                role = "authored-template"
                if relative.startswith(
                    ("templates/.claude/", "templates/.gemini/", "templates/.github/")
                ):
                    role = "generated-template-adapter"
                candidates[path] = role

    related: list[dict[str, str]] = []
    for path in sorted(candidates):
        role = candidates[path]
        related.append({"path": str(path), "role": role, "hash": _sha256(path)})
    return related


def _associated_rows(item: ResolvedSkill, related: Sequence[dict[str, str]]) -> list[dict[str, Any]]:
    relative_sources = {
        Path(entry["path"]).relative_to(item.context.root).as_posix()
        for entry in related
    }
    return [
        row
        for row in _manifest_rows(item.context)
        if isinstance(row.get("source"), str) and row["source"] in relative_sources
    ]


def _target_matrix(item: ResolvedSkill, rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    platforms = set(item.context.registry.platforms)
    platforms.update(
        row["platform"]
        for row in rows
        if isinstance(row.get("platform"), str)
    )
    result: list[dict[str, Any]] = []
    for platform in sorted(platforms):
        platform_rows = [row for row in rows if row.get("platform") == platform]
        sources = sorted(
            {
                source
                for row in platform_rows
                if isinstance((source := row.get("source")), str)
            }
        )
        suffixes = {Path(source).suffix for source in sources}
        command_format = "none"
        if ".toml" in suffixes:
            command_format = "toml"
        elif ".md" in suffixes and item.context.name == "sd-ai-command-pack":
            command_format = "markdown"
        adapted = any(
            source.startswith(
                ("templates/.claude/", "templates/.gemini/", "templates/.github/")
            )
            for source in sources
        )
        result.append(
            {
                "target": platform,
                "content": "adapted" if adapted else ("shared" if sources else "unknown"),
                "frontmatter": (
                    ["name", "description"]
                    if item.context.name == "se-ai-command-pack"
                    else []
                ),
                "commandFormat": command_format,
                "uiMetadata": "none-observed",
                "contextIsolation": "unknown",
                "modelRouting": "profile-only",
                "validation": "manifest-mapped" if sources else "unknown",
                "sources": sources,
            }
        )
    return result


def _inventory_record(item: ResolvedSkill) -> dict[str, Any]:
    text = _read_regular_text(item.canonical)
    metadata, body, metadata_keys = _frontmatter(text, str(item.canonical))
    skill_name = metadata.get("name") or item.canonical.parent.name
    family = item.context.registry.families.get(skill_name, "Uncategorized")
    headings = [match.group(2) for match in HEADING_PATTERN.finditer(body)]
    paragraph_counts: dict[str, int] = {}
    for paragraph in _paragraphs(body):
        paragraph_counts[paragraph] = paragraph_counts.get(paragraph, 0) + 1
    duplicates = [
        {"count": count, "preview": paragraph[:160]}
        for paragraph, count in sorted(paragraph_counts.items())
        if count > 1
    ]
    related = _related_templates(item)
    code_block_count, script_candidates = _script_candidate_signals(related)
    rows = _associated_rows(item, related)
    allowed = item.context.allowed_template_root
    owner_verified = item.context.owner_kind in {
        "sd-upstream",
        "se-upstream",
        "repo-local",
    }
    changeable = bool(
        owner_verified
        and allowed is not None
        and _is_relative_to(item.canonical, allowed)
    )
    trellis = item.context.root / ".trellis" / "scripts" / "task.py"
    references = _resource_paths(related, "references")
    scripts = _resource_paths(related, "scripts")
    links = sorted({match.group(1) for match in LINK_PATTERN.finditer(body)})
    return {
        "name": skill_name,
        "family": family,
        "description": metadata.get("description", ""),
        "canonicalPath": str(item.canonical),
        "canonicalHash": _sha256(item.canonical),
        "reviewPath": str(item.canonical),
        "observedPath": str(item.observed),
        "observedHash": _sha256(item.observed),
        "installations": [
            {
                "path": str(copy.path),
                "root": str(copy.root),
                "platform": copy.platform,
                "observedHash": copy.observed_hash,
                "drift": copy.drift,
                "mappingEvidence": copy.mapping_evidence,
            }
            for copy in item.installations
        ],
        "installedCopies": len(item.installations),
        "sourceRole": item.source_role,
        "drift": item.drift,
        "mappingEvidence": item.mapping_evidence,
        "reviewable": True,
        "changeable": changeable,
        "metadataKeys": list(metadata_keys),
        "headings": headings,
        "arguments": _declared_arguments(body),
        "siblingNames": sorted(
            name
            for name, declared_family in item.context.registry.families.items()
            if declared_family == family and name != skill_name
        ),
        "references": references,
        "scripts": scripts,
        "linkedResources": links,
        "relatedTemplates": related,
        "stats": {
            "lines": len(text.splitlines()),
            "words": len(WORD_PATTERN.findall(text)),
            "bodyParagraphs": len(_paragraphs(body)),
        },
        "signals": {
            "repeatedParagraphs": duplicates,
            "largestSectionLines": _largest_section_lines(body),
            "codeBlockCount": code_block_count,
            "scriptCandidateSignals": script_candidates,
        },
        "testTextReferences": _test_text_references(item.context, skill_name),
        "platformTargets": _target_matrix(item, rows),
        "taskRouting": {
            "ownerKind": item.context.owner_kind,
            "ownerRepo": str(item.context.root),
            "remote": item.context.remote,
            "trellisEntrypoint": str(trellis) if trellis.is_file() else None,
            "allowedTemplateRoot": str(allowed) if allowed else None,
            "canCreateTask": owner_verified and trellis.is_file() and changeable,
        },
    }


def _resource_paths(
    related: Sequence[dict[str, str]], directory: str
) -> list[str]:
    matches: list[str] = []
    for entry in related:
        path = entry["path"]
        parts = [part for part in re.split(r"[\\/]", path) if part]
        if len(parts) >= 2 and parts[-2] == directory:
            matches.append(path)
    return matches


def _largest_section_lines(body: str) -> int:
    indices = [match.start() for match in HEADING_PATTERN.finditer(body)]
    if not indices:
        return len(body.splitlines())
    boundaries = [0, *indices, len(body)]
    return max(
        len(body[boundaries[index] : boundaries[index + 1]].splitlines())
        for index in range(len(boundaries) - 1)
    )


def _cross_skill_signals(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    total_pairs = len(records) * (len(records) - 1) // 2
    if total_pairs > MAX_DESCRIPTION_SIMILARITY_PAIRS:
        return {
            "descriptionSimilarityCandidates": [],
            "descriptionSimilarityPairLimit": MAX_DESCRIPTION_SIMILARITY_PAIRS,
            "unorderedPairsTotal": total_pairs,
            "unorderedPairsCompared": 0,
            "unorderedPairsSkipped": total_pairs,
            "warning": (
                "Description similarity was skipped because the pair count "
                "exceeded the deterministic analysis limit; candidate signals "
                "are not findings."
            ),
        }

    descriptions: list[dict[str, Any]] = []
    for index, left in enumerate(records):
        for right in records[index + 1 :]:
            left_description = str(left.get("description", ""))
            right_description = str(right.get("description", ""))
            ratio = SequenceMatcher(
                None,
                left_description.casefold(),
                right_description.casefold(),
            ).ratio()
            if ratio >= 0.65:
                descriptions.append(
                    {
                        "skills": [left["name"], right["name"]],
                        "ratio": round(ratio, 3),
                    }
                )
    descriptions.sort(key=lambda item: (-item["ratio"], item["skills"]))
    return {
        "descriptionSimilarityCandidates": descriptions,
        "descriptionSimilarityPairLimit": MAX_DESCRIPTION_SIMILARITY_PAIRS,
        "unorderedPairsTotal": total_pairs,
        "unorderedPairsCompared": total_pairs,
        "unorderedPairsSkipped": 0,
        "warning": "Candidate signals are not findings; verify semantics and evidence.",
    }


def _repository_records(items: Sequence[ResolvedSkill]) -> list[dict[str, Any]]:
    contexts: dict[str, PackageContext] = {}
    for item in items:
        contexts[str(item.context.root)] = item.context
    return [
        {
            "root": str(context.root),
            "gitRoot": str(context.git_root) if context.git_root else None,
            "package": context.name,
            "version": context.version,
            "remote": context.remote,
            "ownerKind": context.owner_kind,
            "familyOrder": list(context.registry.family_order),
            "declaredPlatforms": list(context.registry.platforms),
            "allowedTemplateRoot": (
                str(context.allowed_template_root)
                if context.allowed_template_root
                else None
            ),
        }
        for context in sorted(contexts.values(), key=lambda value: str(value.root))
    ]


def build_inventory(
    root: Path,
    skill_specs: Sequence[str],
    family: str | None,
    scope: str | None,
    *,
    root_was_explicit: bool,
    installed_mode: str = "off",
    installed_roots: Sequence[Path] = (),
) -> dict[str, Any]:
    root = _validate_bounded_root(root)
    context = _package_context(root)
    items = _select_paths(
        context,
        root,
        skill_specs,
        family,
        scope,
        root_was_explicit,
        allow_empty=installed_mode != "off",
    )
    installed_items, installation_roots = _discover_installed(
        context,
        installed_mode,
        installed_roots,
    )
    if skill_specs:
        selected_names = {_skill_name(item) for item in items}
        installed_items = [
            item for item in installed_items if _skill_name(item) in selected_names
        ]
    if family:
        installed_items = [
            item
            for item in installed_items
            if item.context.registry.families.get(_skill_name(item), "Uncategorized")
            == family
        ]
    combined = [*items, *installed_items]
    if not combined:
        raise ReviewError(f"no skills found under bounded root or installed roots: {root}")
    items = _deduplicate_resolved(combined)
    if scope == "skill" and len(items) != 1:
        raise ReviewError("scope=skill requires exactly one deduplicated skill")
    records = [_inventory_record(item) for item in items]
    payload: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "scope": scope or ("skill" if len(records) == 1 else "repo"),
        "selector": {
            "skills": list(skill_specs),
            "family": family,
            "root": str(root),
            "installed": installed_mode,
            "installedRoots": [str(path) for path in installed_roots],
        },
        "repositories": _repository_records(items),
        "installationRoots": installation_roots,
        "skills": records,
        "candidateSignals": _cross_skill_signals(records),
        "coverage": {
            "selectedSkills": len(records),
            "installedCopies": sum(
                skill["installedCopies"] for skill in records
            ),
            "deduplicatedSkillRecords": len(combined) - len(items),
            "readOnly": True,
            "semanticFindingsProduced": False,
            "limits": [
                "Metadata parsing is intentionally limited to top-level scalar fields.",
                "Host capabilities marked unknown require current host verification.",
                "Similarity and repetition are candidate signals, not defects.",
                "Test-text references are substring locators, not verified behavioral pins.",
                "Missing or symlinked automatic install roots remain coverage limits.",
            ],
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["snapshotId"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _stat_fingerprint(metadata: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _destination_fingerprint(path: Path) -> tuple[int, int, int, int, int] | None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as error:
        raise ReviewError(f"cannot inspect output destination {path}: {error}") from None
    if stat.S_ISLNK(metadata.st_mode):
        raise ReviewError(f"output destination is a symlink: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise ReviewError(f"output destination is not a regular file: {path}")
    return _stat_fingerprint(metadata)


def _snapshot_matches(payload: dict[str, Any]) -> bool:
    snapshot = payload.get("snapshotId")
    required = {
        "schemaVersion",
        "scope",
        "selector",
        "repositories",
        "installationRoots",
        "skills",
        "candidateSignals",
        "coverage",
        "snapshotId",
    }
    if (
        payload.get("schemaVersion") != SCHEMA_VERSION
        or not isinstance(snapshot, str)
        or len(snapshot) != 64
        or not required.issubset(payload)
        or not isinstance(payload.get("selector"), dict)
        or not isinstance(payload.get("repositories"), list)
        or not isinstance(payload.get("installationRoots"), list)
        or not isinstance(payload.get("skills"), list)
        or not isinstance(payload.get("candidateSignals"), dict)
        or not isinstance(payload.get("coverage"), dict)
    ):
        return False
    unsigned = dict(payload)
    del unsigned["snapshotId"]
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest() == snapshot


def _validate_existing_inventory(path: Path) -> DestinationState | None:
    fingerprint = _destination_fingerprint(path)
    if fingerprint is None:
        return None
    if fingerprint[2] > MAX_EXISTING_INVENTORY_BYTES:
        raise ReviewError(
            "refusing to replace inventory artifact larger than "
            f"{MAX_EXISTING_INVENTORY_BYTES} bytes: {path}"
        )
    descriptor = -1
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or _stat_fingerprint(metadata) != fingerprint
        ):
            raise ReviewError(f"output destination changed during validation: {path}")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            raw = handle.read(fingerprint[2] + 1)
        if len(raw) != fingerprint[2]:
            raise ReviewError(f"output destination changed during validation: {path}")
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except ReviewError:
        raise
    except (OSError, UnicodeError, ValueError) as error:
        raise ReviewError(
            f"refusing to replace invalid inventory artifact {path}: {error}"
        ) from None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if not isinstance(value, dict) or not _snapshot_matches(value):
        raise ReviewError(
            f"refusing to replace unverified inventory artifact: {path}"
        )
    if _destination_fingerprint(path) != fingerprint:
        raise ReviewError(f"output destination changed during validation: {path}")
    return DestinationState(path=path, fingerprint=fingerprint)


def _forbidden_output_roots(payload: dict[str, Any]) -> list[Path]:
    candidates: list[str] = []
    for repository in payload.get("repositories", []):
        if isinstance(repository, dict) and isinstance(repository.get("root"), str):
            candidates.append(repository["root"])
    for installation in payload.get("installationRoots", []):
        if isinstance(installation, dict) and isinstance(installation.get("path"), str):
            candidates.append(installation["path"])
    return sorted(
        {Path(value).expanduser().resolve(strict=False) for value in candidates},
        key=str,
    )


def _validate_output_destination(
    output: Path,
    output_root: Path,
    forbidden_roots: Sequence[Path],
) -> tuple[Path, DestinationState | None]:
    supplied_root = output_root.expanduser().absolute()
    if _crosses_symlink(supplied_root):
        raise ReviewError(f"output root crosses a symlink boundary: {supplied_root}")
    if not supplied_root.exists():
        raise ReviewError(f"output root does not exist: {supplied_root}")
    if not supplied_root.is_dir():
        raise ReviewError(f"output root is not a directory: {supplied_root}")
    root = supplied_root.resolve()
    filesystem_root = Path(root.anchor).resolve()
    if root in {filesystem_root, Path.home().resolve()}:
        raise ReviewError(f"refusing unsafe output root: {root}")

    expanded_output = output.expanduser()
    if ".." in expanded_output.parts:
        raise ReviewError(f"output destination contains a parent escape: {output}")
    candidate = expanded_output if expanded_output.is_absolute() else root / expanded_output
    candidate = Path(os.path.abspath(str(candidate)))
    if candidate == root or not _is_within(candidate, root):
        raise ReviewError(f"output destination escapes output root {root}: {candidate}")

    relative = candidate.relative_to(root)
    parent = root
    for part in relative.parts[:-1]:
        parent = parent / part
        if parent.is_symlink():
            raise ReviewError(f"output destination crosses a symlink: {parent}")
        if not parent.exists() or not parent.is_dir():
            raise ReviewError(f"output destination parent is not a directory: {parent}")
    if candidate.is_symlink():
        raise ReviewError(f"output destination is a symlink: {candidate}")
    resolved = candidate.resolve(strict=False)
    if not _is_within(resolved, root):
        raise ReviewError(f"output destination escapes output root {root}: {resolved}")
    for forbidden in forbidden_roots:
        if _is_within(resolved, forbidden):
            raise ReviewError(
                f"output destination is inside a reviewed or installed root: {resolved}"
            )
    return resolved, _validate_existing_inventory(resolved)


def _atomic_write_inventory(
    destination: Path,
    content: str,
    prior: DestinationState | None,
) -> None:
    descriptor = -1
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(temporary_name)
        os.fchmod(descriptor, 0o600)
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            errors="strict",
            newline="\n",
        ) as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        current = _destination_fingerprint(destination)
        expected = prior.fingerprint if prior is not None else None
        if current != expected:
            raise ReviewError(f"output destination changed before replacement: {destination}")
        os.replace(temporary_path, destination)
        temporary_path = None
    except ReviewError:
        raise
    except OSError as error:
        raise ReviewError(f"cannot write inventory artifact {destination}: {error}") from None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def _bounded_error(error: object) -> str:
    text = " ".join(str(error).split())
    if len(text) <= MAX_ENVELOPE_ERROR_CHARS:
        return text
    return text[: MAX_ENVELOPE_ERROR_CHARS - 3] + "..."


def _transport_envelope(
    payload: dict[str, Any] | None,
    *,
    status: str,
    artifact_written: bool,
    inventory_path: Path | None,
    error: object | None,
) -> dict[str, Any]:
    coverage = payload.get("coverage", {}) if payload is not None else {}
    return {
        "artifactWritten": artifact_written,
        "coverageLimits": coverage.get("limits") if payload is not None else None,
        "error": _bounded_error(error) if error is not None else None,
        "installedCopies": (
            coverage.get("installedCopies") if payload is not None else None
        ),
        "inventoryPath": str(inventory_path) if inventory_path is not None else None,
        "inventorySchemaVersion": (
            payload.get("schemaVersion") if payload is not None else None
        ),
        "selectedSkills": coverage.get("selectedSkills") if payload is not None else None,
        "snapshotId": payload.get("snapshotId") if payload is not None else None,
        "status": status,
        "transportSchemaVersion": TRANSPORT_SCHEMA_VERSION,
    }


def _print_json(value: dict[str, Any], pretty: bool) -> None:
    indent = 2 if pretty else None
    print(json.dumps(value, indent=indent, sort_keys=bool(indent)))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory", help="inventory a bounded skill scope")
    inventory.add_argument("--root", type=Path)
    inventory.add_argument("--skill", action="append", default=[])
    inventory.add_argument("--family")
    inventory.add_argument(
        "--installed",
        choices=("auto", "off"),
        default="auto",
        help="scan supported user skill roots (default: auto)",
    )
    inventory.add_argument(
        "--installed-root",
        type=Path,
        action="append",
        default=[],
        help="repeatable bounded installed skill root; overrides automatic roots",
    )
    inventory.add_argument(
        "--scope",
        choices=("skill", "family", "repo", "package", "all"),
    )
    inventory.add_argument(
        "--output",
        type=Path,
        help="write the complete inventory to this caller-selected bounded path",
    )
    inventory.add_argument(
        "--output-root",
        type=Path,
        help="existing non-home root that bounds --output",
    )
    inventory.add_argument("--pretty", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if sys.version_info < MINIMUM_PYTHON:
        required = ".".join(str(part) for part in MINIMUM_PYTHON)
        current = ".".join(str(part) for part in sys.version_info[:3])
        print(
            f"error: skill_review.py requires Python {required}+; found {current}. "
            "Use the documented bounded manual-coverage fallback.",
            file=sys.stderr,
        )
        return 2
    parser = _parser()
    args = parser.parse_args(argv)
    if args.output_root is not None and args.output is None:
        parser.error("--output-root requires --output")
    bounded_mode = args.output is not None
    if bounded_mode and args.output_root is None:
        error = ReviewError("--output requires --output-root")
        print(f"error: {error}", file=sys.stderr)
        _print_json(
            _transport_envelope(
                None,
                status="error",
                artifact_written=False,
                inventory_path=None,
                error=error,
            ),
            args.pretty,
        )
        return 2
    root_was_explicit = args.root is not None
    root = (args.root or Path.cwd()).expanduser().resolve()
    if not root.exists():
        if not bounded_mode:
            parser.error(f"bounded root does not exist: {root}")
        error = ReviewError(f"bounded root does not exist: {root}")
        print(f"error: {error}", file=sys.stderr)
        _print_json(
            _transport_envelope(
                None,
                status="error",
                artifact_written=False,
                inventory_path=None,
                error=error,
            ),
            args.pretty,
        )
        return 2
    try:
        payload = build_inventory(
            root,
            args.skill,
            args.family,
            args.scope,
            root_was_explicit=root_was_explicit,
            installed_mode=args.installed,
            installed_roots=args.installed_root,
        )
    except ReviewError as error:
        print(f"error: {error}", file=sys.stderr)
        if bounded_mode:
            _print_json(
                _transport_envelope(
                    None,
                    status="error",
                    artifact_written=False,
                    inventory_path=None,
                    error=error,
                ),
                args.pretty,
            )
        return 2
    if not bounded_mode:
        _print_json(payload, args.pretty)
        return 0

    destination: Path | None = None
    try:
        assert args.output is not None and args.output_root is not None
        destination, prior = _validate_output_destination(
            args.output,
            args.output_root,
            _forbidden_output_roots(payload),
        )
        content = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
        _atomic_write_inventory(destination, content, prior)
    except ReviewError as error:
        print(f"error: {error}", file=sys.stderr)
        _print_json(
            _transport_envelope(
                payload,
                status="error",
                artifact_written=False,
                inventory_path=destination,
                error=error,
            ),
            args.pretty,
        )
        return 2
    _print_json(
        _transport_envelope(
            payload,
            status="success",
            artifact_written=True,
            inventory_path=destination,
            error=None,
        ),
        args.pretty,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
