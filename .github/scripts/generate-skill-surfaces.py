#!/usr/bin/env python3
"""Generate the committed manifest rows and skill catalog surfaces.

`installer/registry.py` (SKILLS, PLATFORM_REGISTRY, SHARED_REFERENCES) and
canonical skill frontmatter are the sources of truth. The generator validates
every canonical skill, regenerates manifest.json's files array, replaces the
marker-bounded README catalog, and writes the bundled help catalog from the
same family metadata and frontmatter descriptions. Manifest header fields and
README content outside the markers are preserved.

--check regenerates to memory and fails when any committed surface drifts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACK_ROOT))

from installer.fileops import atomic_write_text  # noqa: E402
from installer.registry import (  # noqa: E402
    FAMILY_DESCRIPTIONS,
    FAMILY_LABELS,
    IF_ANCHOR_EXISTS,
    PACK_NAME,
    PLATFORM_REGISTRY,
    ROOT,
    SHARED_REFERENCES,
    SKILL_NAMES,
    SKILL_PREFIX,
    SKILLS,
    TEMPLATES_SKILLS_DIR,
    USER_SCOPE,
    SkillInfo,
)

MANIFEST_PATH = ROOT / "manifest.json"
README_PATH = ROOT / "README.md"
SKILLS_ROOT = ROOT / TEMPLATES_SKILLS_DIR
SHARED_DIR_NAME = "_shared"
HELP_CATALOG_SOURCE = "_shared/references/skill-catalog.md"
HELP_CATALOG_PATH = SKILLS_ROOT / HELP_CATALOG_SOURCE
GENERATED_SHARED_REFERENCES = frozenset({HELP_CATALOG_SOURCE})
README_CATALOG_START = "<!-- SE_SKILL_CATALOG:START -->"
README_CATALOG_END = "<!-- SE_SKILL_CATALOG:END -->"

REQUIRED_SECTIONS = (
    "## When to use",
    "## Arguments",
    "## Workflow",
    "## Safety rules",
    "## Final report",
)

ALLOWED_FRONTMATTER_KEYS = ("name", "description")
ALLOWED_RESOURCE_SUFFIXES = {
    "references": ".md",
    "scripts": ".py",
}
DESCRIPTION_PREFIX = "Use when"
DESCRIPTION_MAX_LENGTH = 1024

# Canonical bodies speak in capabilities ("your web search tooling"), not
# tool brand names, so one skill text serves every platform. Lowercase
# dotted paths like `.claude/skills` are allowed; brand words are not.
BANNED_PHRASE_PATTERN = re.compile(
    r"\b(Claude|Cowork|Codex|Copilot|Gemini|ChatGPT|OpenAI|Anthropic|Amp)\b"
)

DEFAULT_MANIFEST_HEADER = {
    "schemaVersion": 1,
    "name": PACK_NAME,
    "version": "0.1.0",
    "license": "MIT",
    "description": (
        "Install user-level knowledge-work skills for personal profiles, "
        "consultation, technical authoring, checkpoint-driven technical "
        "tutorials, destination-neutral capture, "
        "critical checklists, "
        "controlled standard operating procedures, "
        "safe operational runbooks, "
        "evidence-aware stakeholder mapping, "
        "source-bound study guides, "
        "message-evidenced conversation digests, "
        "neutral comparisons, "
        "evidence-traceable diagrams, "
        "auditable extreme distillation, "
        "rubric-driven evaluations, "
        "evidence-backed editorial opportunity ranking, "
        "report-first technical editing, "
        "audience-calibrated explanations, "
        "traceable feedback synthesis, "
        "evidence-backed context handoffs, "
        "preview-first knowledge publishing, "
        "bounded knowledge-system audits, "
        "adaptive mastery learning paths, "
        "source-traceable literature maps, "
        "evidence-linked meeting follow-through, "
        "portable baseline monitoring, "
        "methodologically gated research papers, "
        "outcome-based execution planning, "
        "evidence-linked blameless postmortems, "
        "pre-execution failure stress tests, "
        "source-grounded presentation blueprints, "
        "decision-ready proposal development, "
        "source-faithful destination adaptation, "
        "constructive adversarial reviews, "
        "evidence-led general retrospectives, "
        "bookmark and action-inbox triage, agendas, research, "
        "fact checks, decisions, status "
        "reports, discovery, briefs, meeting prep, scans, and digests into "
        "agent skill directories."
    ),
}
HEADER_FIELDS = tuple(DEFAULT_MANIFEST_HEADER)


class GenerationError(Exception):
    """Raised for any validation or drift failure; no partial writes."""


def _display(path: Path) -> str:
    """Repo-relative label when possible; sandboxed test trees fall back
    to the absolute path."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_frontmatter(text: str, label: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise GenerationError(f"{label}: missing YAML frontmatter opening '---'")
    end = text.find("\n---\n", len("---\n") - 1)
    if end == -1:
        raise GenerationError(f"{label}: missing YAML frontmatter closing '---'")
    raw = text[len("---\n") : end + 1]
    body = text[end + len("\n---\n") :]
    import yaml

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        raise GenerationError(f"{label}: invalid frontmatter YAML ({error})") from None
    if not isinstance(data, dict):
        raise GenerationError(f"{label}: frontmatter must be a YAML mapping")
    return data, body


def validate_skill(name: str) -> tuple[list[str], dict[str, str] | None]:
    errors: list[str] = []
    skill_dir = SKILLS_ROOT / name
    skill_md = skill_dir / "SKILL.md"
    label = _display(skill_md)
    if not skill_md.is_file():
        return [f"{label}: missing canonical SKILL.md"], None
    text = skill_md.read_text(encoding="utf-8")
    try:
        frontmatter, body = parse_frontmatter(text, label)
    except GenerationError as error:
        return [str(error)], None

    extra_keys = sorted(set(frontmatter) - set(ALLOWED_FRONTMATTER_KEYS))
    if extra_keys:
        errors.append(
            f"{label}: frontmatter keys {extra_keys} are not allowed "
            f"(allowed: {', '.join(ALLOWED_FRONTMATTER_KEYS)})"
        )
    if frontmatter.get("name") != name:
        errors.append(
            f"{label}: frontmatter name {frontmatter.get('name')!r} must equal "
            f"the skill directory name {name!r}"
        )
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{label}: frontmatter description is missing or empty")
    else:
        if not description.startswith(DESCRIPTION_PREFIX):
            errors.append(
                f"{label}: description must start with {DESCRIPTION_PREFIX!r}"
            )
        if '"' in description:
            errors.append(f"{label}: description must not contain double quotes")
        if "\n" in description.strip():
            errors.append(f"{label}: description must be a single line")
        if len(description) > DESCRIPTION_MAX_LENGTH:
            errors.append(
                f"{label}: description exceeds {DESCRIPTION_MAX_LENGTH} characters"
            )

    if not text.endswith("\n"):
        errors.append(f"{label}: file must end with a newline")
    if not body.lstrip("\n").startswith("# "):
        errors.append(f"{label}: body must open with an H1 title")
    last_index = -1
    for section in REQUIRED_SECTIONS:
        index = body.find(f"\n{section}\n")
        if index == -1:
            errors.append(f"{label}: missing required section {section!r}")
            continue
        if index < last_index:
            errors.append(f"{label}: section {section!r} is out of order")
        last_index = index

    banned = sorted({match.group(0) for match in BANNED_PHRASE_PATTERN.finditer(text)})
    if banned:
        errors.append(
            f"{label}: framework-neutrality lint: replace brand names {banned} "
            "with capability phrasing (e.g. 'your web search tooling')"
        )

    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir).as_posix()
        if path.is_symlink():
            errors.append(
                f"{label}: unexpected symlink {relative} "
                "(skill payload files and directories must be regular)"
            )
            continue
        if path.is_dir():
            relative_dir = path.relative_to(skill_dir)
            if (
                len(relative_dir.parts) != 1
                or relative_dir.parts[0] not in ALLOWED_RESOURCE_SUFFIXES
            ):
                errors.append(
                    f"{label}: unexpected directory "
                    f"{relative_dir.as_posix()}/ (only references/ and scripts/ "
                    "are shipped in this pack version)"
                )
            continue
        if relative == "SKILL.md":
            continue
        parts = Path(relative).parts
        expected_suffix = (
            ALLOWED_RESOURCE_SUFFIXES.get(parts[0]) if len(parts) == 2 else None
        )
        if expected_suffix is None or path.suffix != expected_suffix:
            errors.append(
                f"{label}: unexpected file {relative} (only SKILL.md, "
                "references/*.md, and scripts/*.py are shipped in this pack "
                "version)"
            )
    metadata = None
    if not errors and isinstance(description, str):
        metadata = {"name": name, "description": description}
    return errors, metadata


def validate_skills() -> dict[str, dict[str, str]]:
    errors: list[str] = []
    metadata: dict[str, dict[str, str]] = {}
    if not SKILLS_ROOT.is_dir():
        raise GenerationError(f"missing skills root {SKILLS_ROOT}")
    actual = sorted(
        entry.name
        for entry in SKILLS_ROOT.iterdir()
        if entry.is_dir() and entry.name != SHARED_DIR_NAME
    )
    registered = sorted(SKILL_NAMES)
    missing_dirs = sorted(set(registered) - set(actual))
    unregistered = sorted(set(actual) - set(registered))
    for name in missing_dirs:
        errors.append(
            f"registry skill {name} has no directory under {TEMPLATES_SKILLS_DIR}/"
        )
    for name in unregistered:
        errors.append(
            f"{TEMPLATES_SKILLS_DIR}/{name}/ is not registered in "
            "installer/registry.py SKILL_NAMES"
        )
        if not name.startswith(SKILL_PREFIX):
            errors.append(
                f"{TEMPLATES_SKILLS_DIR}/{name}/ is missing the "
                f"{SKILL_PREFIX} prefix"
            )

    for name in SKILL_NAMES:
        if name in missing_dirs:
            continue
        skill_errors, skill_metadata = validate_skill(name)
        errors.extend(skill_errors)
        if skill_metadata is not None:
            metadata[name] = skill_metadata

    shared_dir = SKILLS_ROOT / SHARED_DIR_NAME
    shared_sources = set(SHARED_REFERENCES)
    if shared_dir.is_dir():
        for path in sorted(shared_dir.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(SKILLS_ROOT).as_posix()
            if relative not in shared_sources:
                errors.append(
                    f"{TEMPLATES_SKILLS_DIR}/{relative} is not registered in "
                    "installer/registry.py SHARED_REFERENCES"
                )
    for source, consumers in SHARED_REFERENCES.items():
        source_path = SKILLS_ROOT / source
        if not source_path.is_file():
            if source in GENERATED_SHARED_REFERENCES:
                continue
            errors.append(f"missing shared reference {TEMPLATES_SKILLS_DIR}/{source}")
            continue
        basename = source_path.name
        for consumer in consumers:
            own_copy = SKILLS_ROOT / consumer / "references" / basename
            if own_copy.exists():
                errors.append(
                    f"{TEMPLATES_SKILLS_DIR}/{consumer}/references/{basename} "
                    f"collides with the shared reference fan-out of {source}"
                )

    if errors:
        raise GenerationError(
            "skill validation failed:\n" + "\n".join(f"- {error}" for error in errors)
        )
    return metadata


def skill_payload_files(name: str) -> list[str]:
    """Per-skill shipped file list: SKILL.md first, then sorted resources."""
    skill_dir = SKILLS_ROOT / name
    resources: list[str] = []
    for directory, suffix in ALLOWED_RESOURCE_SUFFIXES.items():
        resource_dir = skill_dir / directory
        if resource_dir.is_symlink() or not resource_dir.is_dir():
            continue
        resources.extend(
            path.relative_to(skill_dir).as_posix()
            for path in resource_dir.glob(f"*{suffix}")
            if path.is_file() and not path.is_symlink()
        )
    resources.sort()
    return ["SKILL.md", *resources]


def build_rows() -> list[dict]:
    rows: list[dict] = []
    for name in SKILL_NAMES:
        payload = skill_payload_files(name)
        shared = [
            source
            for source, consumers in SHARED_REFERENCES.items()
            if name in consumers
        ]
        for platform in sorted(PLATFORM_REGISTRY):
            info = PLATFORM_REGISTRY[platform]
            for relative in payload:
                rows.append(
                    {
                        "platform": platform,
                        "kind": "skill",
                        "scope": USER_SCOPE,
                        "source": f"{TEMPLATES_SKILLS_DIR}/{name}/{relative}",
                        "target": f"{info.skills_dir}/{name}/{relative}",
                        "anchor": info.anchor,
                        "install": IF_ANCHOR_EXISTS,
                    }
                )
            for source in shared:
                basename = Path(source).name
                rows.append(
                    {
                        "platform": platform,
                        "kind": "skill",
                        "scope": USER_SCOPE,
                        "source": f"{TEMPLATES_SKILLS_DIR}/{source}",
                        "target": f"{info.skills_dir}/{name}/references/{basename}",
                        "anchor": info.anchor,
                        "install": IF_ANCHOR_EXISTS,
                    }
                )

    seen: dict[str, str] = {}
    for row in rows:
        key = row["target"].casefold()
        if key in seen:
            raise GenerationError(
                f"duplicate manifest target {row['target']} "
                f"(also produced as {seen[key]})"
            )
        seen[key] = row["target"]
    return rows


def is_derived_row(row: dict) -> bool:
    return str(row.get("source", "")).startswith(f"{TEMPLATES_SKILLS_DIR}/")


def regenerated_manifest_text() -> str:
    if MANIFEST_PATH.is_file():
        try:
            current = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise GenerationError(f"cannot read manifest.json: {error}") from None
        if not isinstance(current, dict):
            raise GenerationError("manifest.json must be a JSON object")
    else:
        current = dict(DEFAULT_MANIFEST_HEADER)

    manifest: dict = {}
    for field in HEADER_FIELDS:
        manifest[field] = current.get(field, DEFAULT_MANIFEST_HEADER[field])
    unknown_header_fields = sorted(set(current) - {*HEADER_FIELDS, "files"})
    if unknown_header_fields:
        raise GenerationError(
            f"manifest.json has unknown header fields {unknown_header_fields}; "
            "extend the generator before adding header fields"
        )

    existing_files = current.get("files", [])
    if not isinstance(existing_files, list):
        raise GenerationError("manifest.json 'files' must be an array")
    static_rows = [
        row
        for row in existing_files
        if isinstance(row, dict) and not is_derived_row(row)
    ]
    manifest["files"] = [*static_rows, *build_rows()]
    return json.dumps(manifest, indent=2) + "\n"


def _catalog_table_cell(value: str) -> str:
    return value.replace("|", "\\|")


def rendered_skill_catalog(metadata: dict[str, dict[str, str]]) -> str:
    lines: list[str] = []
    for family, label in FAMILY_LABELS.items():
        family_skills: list[SkillInfo] = [
            skill for skill in SKILLS if skill.family == family
        ]
        if not family_skills:
            continue
        if lines:
            lines.append("")
        lines.extend(
            [
                f"### {label}",
                "",
                "| Skill | Use when |",
                "|---|---|",
            ]
        )
        for skill in family_skills:
            try:
                description = metadata[skill.name]["description"]
            except KeyError:
                raise GenerationError(
                    f"validated metadata missing for registry skill {skill.name}"
                ) from None
            lines.append(
                f"| `{skill.name}` | {_catalog_table_cell(description)} |"
            )
    return "\n".join(lines) + "\n"


def _manifest_version(manifest_text: str) -> str:
    try:
        manifest = json.loads(manifest_text)
    except ValueError as error:
        raise GenerationError(f"cannot read manifest version: {error}") from None
    version = manifest.get("version") if isinstance(manifest, dict) else None
    if not isinstance(version, str) or not version.strip():
        raise GenerationError("manifest.json version must be a non-empty string")
    return version


def rendered_help_catalog(
    metadata: dict[str, dict[str, str]], version: str
) -> str:
    lines = [
        "<!-- Generated by .github/scripts/generate-skill-surfaces.py; do not edit. -->",
        "# SE Skill Catalog",
        "",
        f"Bundled pack version: `{version}`",
        "",
        (
            "This catalog describes skills bundled with this release. Current "
            "session availability must be reconciled separately by `se-help`."
        ),
    ]
    for family, label in FAMILY_LABELS.items():
        try:
            description = FAMILY_DESCRIPTIONS[family]
        except KeyError:
            raise GenerationError(
                f"family description missing for registry family {family}"
            ) from None
        lines.extend(["", f"## {label}", "", description])
        family_skills = [skill for skill in SKILLS if skill.family == family]
        if not family_skills:
            lines.extend(["", "No bundled skills in this release."])
            continue
        lines.extend(["", "| Skill | Use when |", "|---|---|"])
        for skill in family_skills:
            try:
                skill_description = metadata[skill.name]["description"]
            except KeyError:
                raise GenerationError(
                    f"validated metadata missing for registry skill {skill.name}"
                ) from None
            lines.append(
                f"| `{skill.name}` | {_catalog_table_cell(skill_description)} |"
            )
    return "\n".join(lines) + "\n"


def regenerated_help_catalog_text(
    metadata: dict[str, dict[str, str]] | None = None,
    manifest_text: str | None = None,
) -> str:
    if metadata is None:
        metadata = validate_skills()
    if manifest_text is None:
        manifest_text = regenerated_manifest_text()
    return rendered_help_catalog(metadata, _manifest_version(manifest_text))


def read_readme_text() -> str:
    try:
        return README_PATH.read_text(encoding="utf-8")
    except OSError as error:
        raise GenerationError(f"cannot read README.md: {error}") from None


def regenerated_readme_text(
    metadata: dict[str, dict[str, str]] | None = None,
    current: str | None = None,
) -> str:
    if metadata is None:
        metadata = validate_skills()
    if current is None:
        current = read_readme_text()
    if (
        current.count(README_CATALOG_START) != 1
        or current.count(README_CATALOG_END) != 1
    ):
        raise GenerationError(
            "README.md must contain exactly one ordered pair of skill catalog markers"
        )
    start = current.index(README_CATALOG_START) + len(README_CATALOG_START)
    end = current.index(README_CATALOG_END)
    if start >= end:
        raise GenerationError(
            "README.md must contain exactly one ordered pair of skill catalog markers"
        )
    catalog = rendered_skill_catalog(metadata).rstrip("\n")
    return f"{current[:start]}\n{catalog}\n{current[end:]}"


def write_generated_surfaces(
    updates: list[tuple[Path, str, str | None]],
) -> None:
    written: list[tuple[Path, str | None]] = []
    try:
        for path, regenerated, committed in updates:
            atomic_write_text(path, regenerated)
            written.append((path, committed))
    except SystemExit as error:
        rollback_errors: list[str] = []
        for path, committed in reversed(written):
            try:
                if committed is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write_text(path, committed)
            except (OSError, SystemExit) as rollback_error:
                rollback_errors.append(f"{_display(path)}: {rollback_error}")
        detail = str(error).removeprefix("error: ")
        if rollback_errors:
            detail += "; rollback failed for " + ", ".join(rollback_errors)
        raise GenerationError(detail) from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate skills and regenerate manifest and README surfaces."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when a committed generated surface drifts.",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    try:
        metadata = validate_skills()
        regenerated_manifest = regenerated_manifest_text()
        committed_readme = read_readme_text()
        regenerated_readme = regenerated_readme_text(metadata, committed_readme)
        regenerated_help_catalog = regenerated_help_catalog_text(
            metadata, regenerated_manifest
        )
    except GenerationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    try:
        committed_manifest = (
            MANIFEST_PATH.read_text(encoding="utf-8")
            if MANIFEST_PATH.is_file()
            else None
        )
        committed_help_catalog = (
            HELP_CATALOG_PATH.read_text(encoding="utf-8")
            if HELP_CATALOG_PATH.is_file()
            else None
        )
    except OSError as error:
        print(f"error: cannot read generated surface: {error}", file=sys.stderr)
        return 1
    if args.check:
        drifted = False
        if committed_manifest != regenerated_manifest:
            print(
                "error: manifest.json drifts from the generated surfaces; "
                "run `make generate` and commit the result",
                file=sys.stderr,
            )
            drifted = True
        if committed_readme != regenerated_readme:
            print(
                "error: README.md skill catalog drifts from the generated surfaces; "
                "run `make generate` and commit the result",
                file=sys.stderr,
            )
            drifted = True
        if committed_help_catalog != regenerated_help_catalog:
            print(
                "error: skill-catalog.md drifts from the generated surfaces; "
                "run `make generate` and commit the result",
                file=sys.stderr,
            )
            drifted = True
        if drifted:
            return 1
        print(
            "manifest.json, README.md, and skill-catalog.md match the "
            "generated surfaces"
        )
        return 0

    updates: list[tuple[Path, str, str | None]] = []
    if committed_readme != regenerated_readme:
        updates.append((README_PATH, regenerated_readme, committed_readme))
    if committed_help_catalog != regenerated_help_catalog:
        updates.append(
            (
                HELP_CATALOG_PATH,
                regenerated_help_catalog,
                committed_help_catalog,
            )
        )
    if committed_manifest != regenerated_manifest:
        updates.append((MANIFEST_PATH, regenerated_manifest, committed_manifest))
    if not updates:
        print("manifest.json, README.md, and skill-catalog.md unchanged")
        return 0
    try:
        write_generated_surfaces(updates)
    except GenerationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for path, _, _ in updates:
        print(f"wrote {_display(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
