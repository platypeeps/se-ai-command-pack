"""Source of truth for platform scopes, skill names, and pack-wide constants."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# The package lives one level below the pack root that hosts install.py,
# manifest.json, and templates/.
ROOT = Path(__file__).resolve().parent.parent

PACK_NAME = "se-ai-command-pack"


@dataclass(frozen=True)
class PlatformInfo:
    """One user-scope install surface.

    skills_dir: home-relative directory skills install into.
    anchor: home-relative directory whose existence selects the platform.
    display: human-readable name for hints and messages.
    agents_dir: home-relative directory agents install into, or None when the
        platform has no agent surface (e.g. the shared Amp anchor). Reuses the
        existing anchor; no new anchor is introduced for agents.
    """

    skills_dir: str
    anchor: str
    display: str
    agents_dir: str | None = None


@dataclass(frozen=True)
class SkillInfo:
    """One canonical skill and its primary outcome family."""

    name: str
    family: str


@dataclass(frozen=True)
class RuntimeProfile:
    """Portable execution recommendation for one or more skills."""

    invocation: str
    context: str
    model: str
    effort: str
    delegation: str = "none"
    roles: tuple[str, ...] = ()


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
        agents_dir=".claude/agents",
    ),
    "codex": PlatformInfo(
        skills_dir=".codex/skills",
        anchor=".codex",
        display="OpenAI Codex",
        agents_dir=".codex/agents",
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
    "operate": "Manage durable user context and operate the SE skill pack.",
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
    SkillInfo(name="se-profile", family="operate"),
    SkillInfo(name="se-action-inbox", family="coordinate"),
    SkillInfo(name="se-agenda", family="coordinate"),
    SkillInfo(name="se-ask-me", family="understand"),
    SkillInfo(name="se-author", family="create"),
    SkillInfo(name="se-bookmark-triage", family="operate"),
    SkillInfo(name="se-capture", family="operate"),
    SkillInfo(name="se-checklist", family="operate"),
    SkillInfo(name="se-compare", family="understand"),
    SkillInfo(name="se-diagram", family="create"),
    SkillInfo(name="se-distill", family="understand"),
    SkillInfo(name="se-evaluate", family="improve"),
    SkillInfo(name="se-topic-radar", family="create"),
    SkillInfo(name="se-technical-editor", family="improve"),
    SkillInfo(name="se-explain", family="understand"),
    SkillInfo(name="se-feedback", family="improve"),
    SkillInfo(name="se-handoff", family="coordinate"),
    SkillInfo(name="se-knowledge-capture", family="operate"),
    SkillInfo(name="se-knowledge-gap", family="understand"),
    SkillInfo(name="se-learn", family="understand"),
    SkillInfo(name="se-literature-map", family="understand"),
    SkillInfo(name="se-meeting-follow-through", family="coordinate"),
    SkillInfo(name="se-monitor", family="understand"),
    SkillInfo(name="se-paper", family="create"),
    SkillInfo(name="se-plan", family="decide"),
    SkillInfo(name="se-postmortem", family="improve"),
    SkillInfo(name="se-premortem", family="improve"),
    SkillInfo(name="se-presentation", family="create"),
    SkillInfo(name="se-proposal", family="create"),
    SkillInfo(name="se-propose-skills", family="improve"),
    SkillInfo(name="se-publish", family="create"),
    SkillInfo(name="se-red-team", family="improve"),
    SkillInfo(name="se-retro", family="improve"),
    SkillInfo(name="se-weekly-review", family="improve"),
    SkillInfo(name="se-runbook", family="operate"),
    SkillInfo(name="se-review-skills", family="improve"),
    SkillInfo(name="se-socratic-review", family="understand"),
    SkillInfo(name="se-sop", family="operate"),
    SkillInfo(name="se-stakeholder-map", family="coordinate"),
    SkillInfo(name="se-study-guide", family="understand"),
    SkillInfo(name="se-thread-digest", family="coordinate"),
    SkillInfo(name="se-tutorial", family="create"),
    SkillInfo(name="se-video-notes", family="understand"),
    SkillInfo(name="se-watchlist", family="operate"),
    SkillInfo(name="se-brand-voice", family="improve"),
)
SKILL_NAMES: tuple[str, ...] = tuple(skill.name for skill in SKILLS)

KNOWN_RUNTIME_INVOCATIONS = frozenset({"automatic", "user-only", "both"})
KNOWN_RUNTIME_CONTEXTS = frozenset({"inline", "forked", "fresh-session"})
KNOWN_RUNTIME_MODELS = frozenset({"inherit", "fast", "balanced", "deep"})
KNOWN_RUNTIME_EFFORTS = frozenset({"low", "medium", "high", "xhigh"})
KNOWN_RUNTIME_DELEGATIONS = frozenset({"none", "optional", "required"})

CONVERSATIONAL = RuntimeProfile("both", "inline", "balanced", "medium")
DEEP_ANALYSIS = RuntimeProfile("both", "forked", "deep", "high")
BOUNDED_SYNTHESIS = RuntimeProfile("both", "forked", "balanced", "medium")
PERSONAL_DIALOGUE = RuntimeProfile("user-only", "inline", "deep", "high")
PROFILE_MUTATION = RuntimeProfile("user-only", "inline", "inherit", "high")
ARTIFACT_AUTHORING = RuntimeProfile("user-only", "inline", "deep", "high")
INSTRUCTIONAL = RuntimeProfile("both", "inline", "deep", "high")
DISCOVERY_UTILITY = RuntimeProfile("both", "inline", "fast", "low")
CAPTURE_UTILITY = RuntimeProfile("both", "inline", "fast", "medium")
INDEPENDENT_RED_TEAM = RuntimeProfile(
    "user-only", "fresh-session", "deep", "xhigh"
)
PACKAGE_REVIEW = RuntimeProfile("user-only", "inline", "deep", "xhigh")
# Pilot delegated profiles: same execution axes as DEEP_ANALYSIS, but each names
# one optional worker role. Split out so delegation reaches only the two pilot
# skills and not the rest of the DEEP_ANALYSIS group. Roles are existence-gated
# by the generator (validate_delegation_roles).
DEEP_ANALYSIS_SOURCE_READING = RuntimeProfile(
    "both", "forked", "deep", "high",
    delegation="optional", roles=("se-source-reader",)
)
DEEP_ANALYSIS_CLAIM_VERIFYING = RuntimeProfile(
    "both", "forked", "deep", "high",
    delegation="optional", roles=("se-claim-verifier",)
)

# Grouped recommendations are easier to audit than 52 repeated records. The
# builder rejects cross-group duplication before deriving the per-skill map.
RUNTIME_PROFILE_ASSIGNMENTS: tuple[
    tuple[RuntimeProfile, tuple[str, ...]], ...
] = (
    (
        CONVERSATIONAL,
        (
            "se-brief",
            "se-meeting-prep",
            "se-decide",
            "se-status",
            "se-action-inbox",
            "se-agenda",
            "se-checklist",
            "se-diagram",
            "se-distill",
            "se-explain",
            "se-handoff",
            "se-learn",
            "se-meeting-follow-through",
            "se-monitor",
            "se-plan",
            "se-presentation",
            "se-publish",
            "se-propose-skills",
            "se-retro",
        ),
    ),
    (DEEP_ANALYSIS_SOURCE_READING, ("se-research",)),
    (DEEP_ANALYSIS_CLAIM_VERIFYING, ("se-fact-check",)),
    (
        DEEP_ANALYSIS,
        (
            "se-knowledge-gap",
            "se-literature-map",
            "se-evaluate",
        ),
    ),
    (
        BOUNDED_SYNTHESIS,
        (
            "se-scan",
            "se-digest",
            "se-compare",
            "se-study-guide",
            "se-video-notes",
            "se-thread-digest",
            "se-bookmark-triage",
            "se-watchlist",
            "se-feedback",
            "se-premortem",
            "se-brand-voice",
        ),
    ),
    (PERSONAL_DIALOGUE, ("se-ask-me", "se-socratic-review")),
    (PROFILE_MUTATION, ("se-profile", "se-knowledge-capture")),
    (
        ARTIFACT_AUTHORING,
        (
            "se-author",
            "se-topic-radar",
            "se-paper",
            "se-proposal",
            "se-stakeholder-map",
            "se-runbook",
            "se-postmortem",
            "se-weekly-review",
        ),
    ),
    (INSTRUCTIONAL, ("se-tutorial", "se-sop", "se-technical-editor")),
    (DISCOVERY_UTILITY, ("se-help",)),
    (CAPTURE_UTILITY, ("se-capture",)),
    (INDEPENDENT_RED_TEAM, ("se-red-team",)),
    (PACKAGE_REVIEW, ("se-review-skills",)),
)


def validate_runtime_profile(profile: RuntimeProfile) -> None:
    """Fail closed when a portable runtime recommendation is unknown."""

    for field_name, value, allowed in (
        ("invocation", profile.invocation, KNOWN_RUNTIME_INVOCATIONS),
        ("context", profile.context, KNOWN_RUNTIME_CONTEXTS),
        ("model", profile.model, KNOWN_RUNTIME_MODELS),
        ("effort", profile.effort, KNOWN_RUNTIME_EFFORTS),
        ("delegation", profile.delegation, KNOWN_RUNTIME_DELEGATIONS),
    ):
        if value not in allowed:
            raise RuntimeError(
                f"runtime profile has unknown {field_name} value: {value!r}"
            )
    if not isinstance(profile.roles, tuple):
        # A bare string is iterable char-by-char, so it would silently pass
        # the per-role checks below as a sequence of single-character "roles".
        raise RuntimeError(
            "runtime profile roles must be a tuple, not "
            f"{type(profile.roles).__name__}: {profile.roles!r}"
        )
    if profile.delegation == "none":
        if profile.roles:
            raise RuntimeError(
                "runtime profile delegation 'none' must carry no roles: "
                f"{profile.roles!r}"
            )
    elif not profile.roles:
        raise RuntimeError(
            f"runtime profile delegation {profile.delegation!r} requires "
            "at least one role"
        )
    if any(not isinstance(role, str) or not role for role in profile.roles):
        raise RuntimeError(
            f"runtime profile roles must be non-empty strings: {profile.roles!r}"
        )


def build_skill_runtime_profiles(
    assignments: tuple[tuple[RuntimeProfile, tuple[str, ...]], ...],
    skill_names: tuple[str, ...],
) -> dict[str, RuntimeProfile]:
    """Validate grouped membership and derive a registry-ordered skill map."""

    registered = set(skill_names)
    assigned: dict[str, RuntimeProfile] = {}
    for profile, names in assignments:
        validate_runtime_profile(profile)
        for name in names:
            if name not in registered:
                raise RuntimeError(
                    f"runtime profile assignment names unknown skill: {name}"
                )
            if name in assigned:
                raise RuntimeError(
                    f"duplicate runtime profile assignment for skill: {name}"
                )
            assigned[name] = profile
    missing = sorted(registered - set(assigned))
    if missing:
        raise RuntimeError(f"skills missing runtime profile assignments: {missing}")
    return {name: assigned[name] for name in skill_names}


SKILL_RUNTIME_PROFILES = build_skill_runtime_profiles(
    RUNTIME_PROFILE_ASSIGNMENTS, SKILL_NAMES
)

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
        "se-profile",
        "se-action-inbox",
        "se-agenda",
        "se-ask-me",
        "se-author",
        "se-bookmark-triage",
        "se-capture",
        "se-checklist",
        "se-compare",
        "se-diagram",
        "se-distill",
        "se-evaluate",
        "se-topic-radar",
        "se-technical-editor",
        "se-explain",
        "se-feedback",
        "se-handoff",
        "se-knowledge-capture",
        "se-knowledge-gap",
        "se-learn",
        "se-literature-map",
        "se-meeting-follow-through",
        "se-monitor",
        "se-paper",
        "se-plan",
        "se-postmortem",
        "se-premortem",
        "se-presentation",
        "se-proposal",
        "se-publish",
        "se-red-team",
        "se-retro",
        "se-weekly-review",
        "se-runbook",
        "se-socratic-review",
        "se-sop",
        "se-stakeholder-map",
        "se-study-guide",
        "se-thread-digest",
        "se-tutorial",
        "se-video-notes",
        "se-watchlist",
    ),
    "_shared/references/state-schema.md": (
        "se-monitor",
        "se-watchlist",
    ),
    "_shared/references/verification-protocol.md": (
        "se-research",
        "se-fact-check",
        "se-literature-map",
        "se-paper",
    ),
    "_shared/references/argument-vocabulary.md": (
        "se-action-inbox",
        "se-agenda",
        "se-ask-me",
        "se-author",
        "se-bookmark-triage",
        "se-brief",
        "se-capture",
        "se-checklist",
        "se-compare",
        "se-decide",
        "se-diagram",
        "se-digest",
        "se-distill",
        "se-evaluate",
        "se-explain",
        "se-fact-check",
        "se-feedback",
        "se-handoff",
        "se-help",
        "se-knowledge-capture",
        "se-knowledge-gap",
        "se-learn",
        "se-literature-map",
        "se-meeting-follow-through",
        "se-meeting-prep",
        "se-monitor",
        "se-paper",
        "se-plan",
        "se-postmortem",
        "se-premortem",
        "se-presentation",
        "se-profile",
        "se-proposal",
        "se-propose-skills",
        "se-publish",
        "se-red-team",
        "se-research",
        "se-retro",
        "se-review-skills",
        "se-runbook",
        "se-scan",
        "se-socratic-review",
        "se-sop",
        "se-stakeholder-map",
        "se-status",
        "se-study-guide",
        "se-technical-editor",
        "se-thread-digest",
        "se-topic-radar",
        "se-tutorial",
        "se-video-notes",
        "se-watchlist",
        "se-weekly-review",
        "se-brand-voice",
    ),
    "_shared/references/skill-catalog.md": ("se-help",),
    "_shared/references/personal-profile-contract.md": (
        "se-profile",
        "se-ask-me",
        "se-topic-radar",
        "se-technical-editor",
        "se-paper",
        "se-presentation",
        "se-proposal",
        "se-publish",
        "se-tutorial",
        "se-watchlist",
        "se-weekly-review",
    ),
}

# Canonical `key=value` argument vocabulary shared across skills. These two
# constants are the single source of truth for the enforced value ladders and
# the reserved argument names. The human-readable contract is the shared
# reference registered under the `_shared/references/argument-vocabulary.md` key
# in SHARED_REFERENCES above. Value ladders are checked as set membership (a
# skill may declare any subset, in any order).
CANONICAL_ARGUMENT_LADDERS: dict[str, tuple[str, ...]] = {
    "depth": ("brief", "standard", "deep"),
    "sensitivity": ("minimal", "restricted", "standard"),
}

RESERVED_ARGUMENT_NAMES: tuple[str, ...] = (
    "input",
    "sources",
    "min_sources",
    "coverage",
    "target_words",
    "privacy",
    "evidence",
    "format",
    "mode",
    "scope",
    "audience",
)

# Known non-canonical aliases for the enforced covered axes, mapped to the
# canonical name(s) a regression should use instead. Declaring one of these is a
# hard validation error. This is a closed set by construction: enforcement does
# not infer a covered concept from an arbitrary future name, so the guarantee is
# "no regression under a known covered-axis alias or off-ladder value", not "no
# drift under any conceivable name". `detail` maps to both canonicals because it
# was used for both the verbosity and redaction senses before A-006.
KNOWN_COVERED_AXIS_ALIASES: dict[str, tuple[str, ...]] = {
    "length": ("depth",),
    "source": ("input",),
    "inputs": ("input",),
    "detail": ("depth", "sensitivity"),
}

_ARGUMENT_SPAN_RE = re.compile(r"`([^`\n]+)`")
_ARGUMENT_NAME_RE = re.compile(r"[a-z0-9_-]+")


def arguments_section(body: str) -> str:
    """Return a skill body's ``## Arguments`` section text, or '' when absent.

    Slices from the ``## Arguments`` heading to the next ``## `` heading (or the
    end of the body). Shared so the generator's `validate_skill()` and the
    live-corpus conformance test extract the same span from one definition.
    """
    start = body.find("\n## Arguments\n")
    if start == -1:
        return ""
    rest = body[start + 1 :]
    next_section = rest.find("\n## ", len("## Arguments"))
    return rest if next_section == -1 else rest[:next_section]


def argument_vocabulary_errors(label: str, section: str) -> list[str]:
    """Covered-axis argument violations in one skill's ``## Arguments`` body.

    Parses every inline-code ``key=values`` span in the given section text (a
    single Arguments bullet may declare more than one argument). Returns
    human-readable error strings, each prefixed with ``label``:

    - a covered axis declared under a known non-canonical alias
      (``length``/``source``/``inputs``/``detail``); and
    - a ``depth=`` or ``sensitivity=`` value outside its canonical ladder,
      checked as set membership rather than declaration order.

    A name that is neither a known alias nor an enforced ladder is left alone
    (reserved or per-skill owned) — see the closed-set note above.
    """
    errors: list[str] = []
    for match in _ARGUMENT_SPAN_RE.finditer(section):
        span = match.group(1)
        if "=" not in span:
            continue
        left, _, right = span.partition("=")
        # Only treat a span as a declaration when its whole left side is a clean
        # argument token; `depth*foo=x` and similar malformed spans are skipped
        # rather than mis-read as a `depth=` declaration.
        if _ARGUMENT_NAME_RE.fullmatch(left) is None:
            continue
        name = left
        if name in KNOWN_COVERED_AXIS_ALIASES:
            canonical = KNOWN_COVERED_AXIS_ALIASES[name]
            suggestion = " or ".join(f"`{canon}=`" for canon in canonical)
            errors.append(
                f"{label}: argument `{name}=` is a non-canonical alias for the "
                f"{' / '.join(canonical)} axis; use {suggestion}"
            )
        elif name in CANONICAL_ARGUMENT_LADDERS:
            ladder = CANONICAL_ARGUMENT_LADDERS[name]
            allowed = set(ladder)
            # Any non-empty `|`-separated token that is not in the ladder is a
            # violation — including one with stray case or punctuation
            # (`Standard`, `standard,`), which must be flagged, not skipped.
            off_ladder = sorted(
                {
                    value
                    for token in right.split("|")
                    if (value := token.strip()) and value not in allowed
                }
            )
            if off_ladder:
                errors.append(
                    f"{label}: argument `{name}=` value(s) {off_ladder} are not "
                    f"in the canonical {name} ladder {list(ladder)}"
                )
    return errors


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
        if info.agents_dir is not None:
            agents_path = Path(info.agents_dir)
            if agents_path.is_absolute() or ".." in agents_path.parts:
                raise RuntimeError(
                    f"registry platform {platform} has unsafe agents_dir: "
                    f"{info.agents_dir}"
                )
            if not (
                info.agents_dir == info.anchor
                or info.agents_dir.startswith(info.anchor + "/")
            ):
                raise RuntimeError(
                    f"registry platform {platform} anchor {info.anchor!r} does "
                    f"not contain agents_dir {info.agents_dir!r}"
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
    expected_profiles = build_skill_runtime_profiles(
        RUNTIME_PROFILE_ASSIGNMENTS, SKILL_NAMES
    )
    if SKILL_RUNTIME_PROFILES != expected_profiles:
        raise RuntimeError(
            "SKILL_RUNTIME_PROFILES must be derived from runtime assignments"
        )
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
    "FAMILY_DESCRIPTIONS",
    "FAMILY_LABELS",
    "IF_ANCHOR_EXISTS",
    "IF_NOT_EXISTS",
    "INSTALLED_TARGETS_FILE",
    "KNOWN_INSTALL_MODES",
    "KNOWN_RUNTIME_CONTEXTS",
    "KNOWN_RUNTIME_DELEGATIONS",
    "KNOWN_RUNTIME_EFFORTS",
    "KNOWN_RUNTIME_INVOCATIONS",
    "KNOWN_RUNTIME_MODELS",
    "KNOWN_SCOPES",
    "PACK_MANIFEST_FILE",
    "PACK_NAME",
    "PLATFORMS",
    "PLATFORM_REGISTRY",
    "PROVENANCE_FILE",
    "PlatformInfo",
    "RECEIPT_DIR",
    "ROOT",
    "RUNTIME_PROFILE_ASSIGNMENTS",
    "RuntimeProfile",
    "SHARED_REFERENCES",
    "SKILLS",
    "SKILL_NAMES",
    "SKILL_RUNTIME_PROFILES",
    "SKILL_PREFIX",
    "SkillInfo",
    "TEMPLATES_SKILLS_DIR",
    "USER_SCOPE",
    "build_skill_runtime_profiles",
    "validate_registry",
    "validate_runtime_profile",
]
