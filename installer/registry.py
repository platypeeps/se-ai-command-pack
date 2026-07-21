"""Source of truth for platform scopes, skill names, and pack-wide constants."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# The package lives one level below the pack root that hosts install.py,
# manifest.json, and templates/.
ROOT = Path(__file__).resolve().parent.parent

PACK_NAME = "se-ai-command-pack"
ENV_PREFIX = "SE_AI_COMMAND_PACK_"


@dataclass(frozen=True)
class PlatformInfo:
    """One user-scope install surface.

    skills_dir: home-relative directory skills install into.
    anchor: home-relative directory whose existence selects the platform.
    display: human-readable name for hints and messages.
    """

    skills_dir: str
    anchor: str
    display: str


@dataclass(frozen=True)
class SkillInfo:
    """One canonical skill and its primary outcome family."""

    name: str
    family: str


# One registry row per platform id. Adding a platform means one row here;
# `make generate` then fans every skill into its skills_dir.
PLATFORM_REGISTRY: dict[str, PlatformInfo] = {
    "agents": PlatformInfo(
        skills_dir=".config/agents/skills",
        anchor=".config/agents",
        display="shared agents dir (Amp and compatible tools)",
    ),
    "claude": PlatformInfo(
        skills_dir=".claude/skills",
        anchor=".claude",
        display="Claude Code / Cowork",
    ),
    "codex": PlatformInfo(
        skills_dir=".codex/skills",
        anchor=".codex",
        display="OpenAI Codex",
    ),
}

PLATFORMS = tuple(sorted(PLATFORM_REGISTRY))

# Families describe a skill's primary outcome. Mapping order is the public
# catalog order; declared families with zero registered skills remain valid but
# are omitted from the catalog.
FAMILY_LABELS: dict[str, str] = {
    "understand": "Understand",
    "decide": "Decide",
    "create": "Create",
    "coordinate": "Coordinate",
    "operate": "Operate",
    "improve": "Improve",
}

FAMILY_DESCRIPTIONS: dict[str, str] = {
    "understand": "Gather, verify, and synthesize information.",
    "decide": "Compare evidence and choose a defensible direction.",
    "create": "Turn source material and intent into a polished artifact.",
    "coordinate": "Align people, plans, status, and handoffs.",
    "operate": "Discover and operate the SE skill pack itself.",
    "improve": "Reflect, learn, and strengthen future work.",
}

# Canonical skill registry. Row order remains the manifest/install order;
# catalog display groups these rows through FAMILY_LABELS without moving paths.
SKILLS: tuple[SkillInfo, ...] = (
    SkillInfo(name="se-research", family="understand"),
    SkillInfo(name="se-brief", family="coordinate"),
    SkillInfo(name="se-meeting-prep", family="coordinate"),
    SkillInfo(name="se-scan", family="understand"),
    SkillInfo(name="se-digest", family="understand"),
    SkillInfo(name="se-decide", family="decide"),
    SkillInfo(name="se-status", family="coordinate"),
    SkillInfo(name="se-fact-check", family="understand"),
    SkillInfo(name="se-help", family="operate"),
)
SKILL_NAMES: tuple[str, ...] = tuple(skill.name for skill in SKILLS)

# Shared reference source (relative to templates/skills/) -> consuming skills.
# The generator copies each shared reference into every consumer's
# references/ dir so installed skill dirs stay self-contained per platform.
SHARED_REFERENCES: dict[str, tuple[str, ...]] = {
    "_shared/references/source-standards.md": (
        "se-research",
        "se-brief",
        "se-meeting-prep",
        "se-scan",
        "se-digest",
        "se-decide",
        "se-status",
        "se-fact-check",
    ),
    "_shared/references/verification-protocol.md": (
        "se-research",
        "se-fact-check",
    ),
    "_shared/references/skill-catalog.md": ("se-help",),
}

ALWAYS_INSTALL = "always"
IF_ANCHOR_EXISTS = "if-anchor-exists"
IF_NOT_EXISTS = "if-not-exists"
KNOWN_INSTALL_MODES = frozenset(
    {
        ALWAYS_INSTALL,
        IF_ANCHOR_EXISTS,
        IF_NOT_EXISTS,
    }
)

USER_SCOPE = "user"
# "project" is reserved for a future per-folder install mode.
KNOWN_SCOPES = frozenset({USER_SCOPE})

# Targets --force must never overwrite (user-tunable configs). Empty in
# v0.1; install_file keeps the preserve hook for future config-like files.
FORCE_PRESERVED_TARGETS: frozenset[Path] = frozenset()

RECEIPT_DIR = Path(f".{PACK_NAME}")
INSTALLED_TARGETS_FILE = RECEIPT_DIR / "installed-targets.txt"
PROVENANCE_FILE = RECEIPT_DIR / "provenance.json"
PACK_MANIFEST_FILE = RECEIPT_DIR / "manifest.json"

TEMPLATES_SKILLS_DIR = "templates/skills"
SKILL_PREFIX = "se-"


def validate_registry() -> None:
    if tuple(FAMILY_DESCRIPTIONS) != tuple(FAMILY_LABELS):
        raise RuntimeError(
            "FAMILY_DESCRIPTIONS must match FAMILY_LABELS without reordering"
        )
    for family, description in FAMILY_DESCRIPTIONS.items():
        if not description.strip():
            raise RuntimeError(f"family {family} has an empty description")
    for platform, info in PLATFORM_REGISTRY.items():
        for field_name, value in (
            ("skills_dir", info.skills_dir),
            ("anchor", info.anchor),
        ):
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise RuntimeError(
                    f"registry platform {platform} has unsafe {field_name}: {value}"
                )
        if not (
            info.skills_dir == info.anchor
            or info.skills_dir.startswith(info.anchor + "/")
        ):
            raise RuntimeError(
                f"registry platform {platform} anchor {info.anchor!r} does not "
                f"contain skills_dir {info.skills_dir!r}"
            )
    expected_names = tuple(skill.name for skill in SKILLS)
    if SKILL_NAMES != expected_names:
        raise RuntimeError("SKILL_NAMES must be derived from SKILLS without reordering")
    seen_skills: set[str] = set()
    for skill in SKILLS:
        name = skill.name
        family = skill.family
        if not name:
            raise RuntimeError("skill registry contains an empty name")
        if not family:
            raise RuntimeError(f"skill {name} has an empty family")
        if family not in FAMILY_LABELS:
            raise RuntimeError(f"skill {name} has unknown family: {family}")
        if not name.startswith(SKILL_PREFIX):
            raise RuntimeError(f"skill name missing {SKILL_PREFIX} prefix: {name}")
        if name in seen_skills:
            raise RuntimeError(f"duplicate skill name in registry: {name}")
        seen_skills.add(name)
    for source, consumers in SHARED_REFERENCES.items():
        if not source.startswith("_shared/"):
            raise RuntimeError(
                f"SHARED_REFERENCES source must live under _shared/: {source}"
            )
        unknown = set(consumers) - set(SKILL_NAMES)
        if unknown:
            raise RuntimeError(
                f"SHARED_REFERENCES {source} names unknown skills: {sorted(unknown)}"
            )


validate_registry()


__all__ = [
    "ALWAYS_INSTALL",
    "ENV_PREFIX",
    "FAMILY_DESCRIPTIONS",
    "FAMILY_LABELS",
    "FORCE_PRESERVED_TARGETS",
    "IF_ANCHOR_EXISTS",
    "IF_NOT_EXISTS",
    "INSTALLED_TARGETS_FILE",
    "KNOWN_INSTALL_MODES",
    "KNOWN_SCOPES",
    "PACK_MANIFEST_FILE",
    "PACK_NAME",
    "PLATFORMS",
    "PLATFORM_REGISTRY",
    "PROVENANCE_FILE",
    "PlatformInfo",
    "RECEIPT_DIR",
    "ROOT",
    "SHARED_REFERENCES",
    "SKILLS",
    "SKILL_NAMES",
    "SKILL_PREFIX",
    "SkillInfo",
    "TEMPLATES_SKILLS_DIR",
    "USER_SCOPE",
    "validate_registry",
]
