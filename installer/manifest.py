"""Manifest loading and validation: PackFile entries and safe path resolution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from installer.registry import (
    IF_ANCHOR_EXISTS,
    KNOWN_INSTALL_MODES,
    KNOWN_SCOPES,
    PLATFORMS,
    ROOT,
    USER_SCOPE,
)

MANIFEST_PATH = ROOT / "manifest.json"


@dataclass(frozen=True)
class PackFile:
    platform: str
    kind: str
    scope: str
    source: Path | None
    target: Path
    anchor: Path | None
    install: str


SUPPORTED_MANIFEST_SCHEMA_VERSION = 1
KNOWN_MANIFEST_KINDS = frozenset(
    {
        "command",
        "config",
        "doc",
        "prompt",
        "script",
        "skill",
        "workflow",
    }
)


def load_manifest() -> tuple[dict, list[PackFile]]:
    """Parse manifest.json into its raw dict plus PackFile entries, aborting
    with SystemExit on invalid JSON, an unsupported schemaVersion, or a
    malformed files array."""
    try:
        raw = json.loads(read_text_strict(MANIFEST_PATH, "manifest"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"error: manifest is not valid JSON: {error}") from None
    if not isinstance(raw, dict):
        raise SystemExit(
            f"error: manifest must be a JSON object, got {type(raw).__name__}"
        )
    schema_version = raw.get("schemaVersion", 1)
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise SystemExit(
            f"error: manifest schemaVersion must be an integer, got {schema_version!r}"
        )
    if schema_version > SUPPORTED_MANIFEST_SCHEMA_VERSION:
        raise SystemExit(
            f"error: manifest schemaVersion {schema_version} is newer than this "
            f"installer supports ({SUPPORTED_MANIFEST_SCHEMA_VERSION}); update "
            "the pack checkout before installing"
        )
    files_value = raw.get("files", [])
    if not isinstance(files_value, list):
        raise SystemExit(
            f"error: manifest 'files' must be an array, got "
            f"{type(files_value).__name__}"
        )
    files: list[PackFile] = []
    for index, item in enumerate(files_value):
        try:
            files.append(
                PackFile(
                    platform=str(item["platform"]),
                    kind=str(item["kind"]),
                    scope=str(item.get("scope", USER_SCOPE)),
                    source=ROOT / str(item["source"]),
                    target=Path(str(item["target"])),
                    anchor=Path(str(item["anchor"])) if item.get("anchor") else None,
                    install=str(item.get("install", IF_ANCHOR_EXISTS)),
                )
            )
        except KeyError as error:
            raise SystemExit(
                f"error: manifest files[{index}] is missing required field "
                f"{error.args[0]!r}"
            ) from None
        except TypeError:
            raise SystemExit(
                f"error: manifest files[{index}] must be an object with "
                "platform/kind/source/target fields"
            ) from None
    return raw, files


def validate_manifest(files: list[PackFile]) -> None:
    """Reject unknown platforms, kinds, or scopes, unsafe or duplicate paths,
    and missing pack templates, aborting with SystemExit on the first
    violation."""
    seen_targets: set[Path] = set()
    for file in files:
        if file.platform not in PLATFORMS:
            raise SystemExit(f"error: unknown platform {file.platform!r} in manifest")
        if file.kind not in KNOWN_MANIFEST_KINDS:
            raise SystemExit(
                f"error: unknown kind {file.kind!r} in manifest for {file.target} "
                f"(known kinds: {', '.join(sorted(KNOWN_MANIFEST_KINDS))})"
            )
        if file.scope not in KNOWN_SCOPES:
            raise SystemExit(
                f"error: unknown scope {file.scope!r} in manifest for {file.target} "
                f"(known scopes: {', '.join(sorted(KNOWN_SCOPES))})"
            )
        if file.install not in KNOWN_INSTALL_MODES:
            raise SystemExit(
                f"error: unknown install mode {file.install!r} in manifest for "
                f"{file.target} (known install modes: "
                f"{', '.join(sorted(KNOWN_INSTALL_MODES))})"
            )
        if file.source is None:
            raise SystemExit(f"error: manifest file has no source: {file.target}")
        validate_pack_source(file.source)
        validate_relative_manifest_path("target", file.target)
        if file.anchor is not None:
            validate_relative_manifest_path("anchor", file.anchor)
        if file.target in seen_targets:
            raise SystemExit(f"error: duplicate target in manifest: {file.target}")
        seen_targets.add(file.target)
        if not file.source.is_file():
            raise SystemExit(f"error: missing pack template {file.source}")


def validate_relative_manifest_path(field: str, path: Path) -> None:
    windows_path = PureWindowsPath(str(path))
    if (
        path.is_absolute()
        or bool(windows_path.drive)
        or bool(windows_path.root)
        or ".." in path.parts
        or ".." in windows_path.parts
    ):
        raise SystemExit(f"error: unsafe {field} path in manifest: {path}")


def read_text_strict(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"error: {label} not found: {path}") from None
    except UnicodeDecodeError as error:
        raise SystemExit(
            f"error: {label} is not valid UTF-8: {path} ({error})"
        ) from None
    except OSError as error:
        raise SystemExit(f"error: cannot read {label}: {path} ({error})") from None


def read_text_if_exists(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError as error:
        raise SystemExit(
            f"error: {label} is not valid UTF-8: {path} ({error})"
        ) from None
    except OSError as error:
        raise SystemExit(f"error: cannot read {label}: {path} ({error})") from None


def system_exit_detail(error: SystemExit) -> str:
    detail = str(error)
    if detail.startswith("error: "):
        detail = detail[len("error: ") :]
    return detail or "operation failed"


def manifest_cli_identity() -> str:
    try:
        raw = json.loads(read_text_strict(MANIFEST_PATH, "manifest"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"error: manifest is not valid JSON: {error}") from None
    name = raw.get("name")
    version = raw.get("version")
    if not isinstance(name, str) or not name.strip():
        raise SystemExit("error: manifest name is missing")
    if not isinstance(version, str) or not version.strip():
        raise SystemExit("error: manifest version is missing")
    return f"{name} {version}"


def validate_pack_source(source: Path) -> None:
    try:
        relative_source = source.relative_to(ROOT)
    except ValueError:
        raise SystemExit(f"error: unsafe source path in manifest: {source}") from None
    validate_relative_manifest_path("source", relative_source)
    try:
        # ROOT is Path(__file__).resolve().parent.parent, i.e. already
        # symlink-resolved and absolute; ROOT.resolve() would be a no-op.
        source.resolve(strict=False).relative_to(ROOT)
    except (OSError, RuntimeError) as error:
        raise SystemExit(
            f"error: cannot resolve source path in manifest: {source} ({error})"
        ) from None
    except ValueError:
        raise SystemExit(f"error: unsafe source path in manifest: {source}") from None


def validate_resolved_target_path(root: Path, path: Path, label: str) -> None:
    try:
        resolved_root = root.resolve()
        resolved_path = path.resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise SystemExit(f"error: cannot resolve {label}: {path} ({error})") from None

    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        raise SystemExit(
            f"error: {label} resolves outside the install root: {path}"
        ) from None


def target_destination(
    root: Path, relative_path: Path, label: str = "target path"
) -> Path:
    validate_relative_manifest_path("target", relative_path)
    destination = root / relative_path
    validate_resolved_target_path(root, destination, label)
    return destination


def removal_target_destination(
    root: Path,
    relative_path: Path,
    label: str = "target path",
) -> Path:
    validate_relative_manifest_path("target", relative_path)
    destination = root / relative_path
    validate_resolved_target_path(root, destination.parent, f"{label} parent")
    return destination


def require_install_root(root: Path) -> None:
    if not root.is_dir():
        raise SystemExit(
            f"error: install root not found or not a directory: {root}"
        )


__all__ = [
    "IF_ANCHOR_EXISTS",
    "KNOWN_INSTALL_MODES",
    "KNOWN_MANIFEST_KINDS",
    "MANIFEST_PATH",
    "PackFile",
    "SUPPORTED_MANIFEST_SCHEMA_VERSION",
    "load_manifest",
    "manifest_cli_identity",
    "read_text_if_exists",
    "read_text_strict",
    "removal_target_destination",
    "require_install_root",
    "system_exit_detail",
    "target_destination",
    "validate_manifest",
    "validate_pack_source",
    "validate_relative_manifest_path",
    "validate_resolved_target_path",
]
