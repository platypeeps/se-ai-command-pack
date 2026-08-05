# Research: RuntimeProfile system and a new `delegation` field

- **Query**: What would adding a `delegation` (none|optional|required + role refs) field to RuntimeProfile require? Dataclass, validation, assignment/resolution, generator overlay.
- **Scope**: internal
- **Date**: 2026-08-05

## Findings

### Current RuntimeProfile dataclass (verbatim)

`installer/registry.py:43-50`:

```python
@dataclass(frozen=True)
class RuntimeProfile:
    """Portable execution recommendation for one or more skills."""

    invocation: str
    context: str
    model: str
    effort: str
```

Four string axes. Frozen dataclass — equality is field-by-field (used in `validate_registry`'s `SKILL_RUNTIME_PROFILES != expected_profiles` check, `:638`).

### Known-value vocabularies

`installer/registry.py:157-160`:

```python
KNOWN_RUNTIME_INVOCATIONS = frozenset({"automatic", "user-only", "both"})
KNOWN_RUNTIME_CONTEXTS = frozenset({"inline", "forked", "fresh-session"})
KNOWN_RUNTIME_MODELS = frozenset({"inherit", "fast", "balanced", "deep"})
KNOWN_RUNTIME_EFFORTS = frozenset({"low", "medium", "high", "xhigh"})
```

A `delegation` axis would add e.g. `KNOWN_RUNTIME_DELEGATIONS = frozenset({"none", "optional", "required"})`.

### Profile constants (`:162-174`)

Eleven named constants, each `RuntimeProfile(invocation, context, model, effort)` positional. The pilot skills se-research + se-fact-check use `DEEP_ANALYSIS = RuntimeProfile("both", "forked", "deep", "high")` (`:163`).

**Coupling alert**: every constant is built with **positional** args (`:162-174`). Adding a 5th field to the dataclass means either (a) giving it a default (`delegation: str = "none"`) so the 11 existing positional constructions stay valid, or (b) updating all 11 call sites. A default keeps the blast radius to just the pilot constants that opt in. The frozen dataclass supports defaults on trailing fields.

### Assignment table (`:178-250`)

`RUNTIME_PROFILE_ASSIGNMENTS: tuple[tuple[RuntimeProfile, tuple[str, ...]], ...]` groups a profile with the skill names sharing it. `DEEP_ANALYSIS` currently covers `se-research, se-fact-check, se-knowledge-gap, se-literature-map, se-evaluate` (`:206-214`).

**Coupling alert**: only se-research and se-fact-check are pilot skills for delegation, but they currently **share** the `DEEP_ANALYSIS` group with three non-pilots. If delegation is added to `DEEP_ANALYSIS` itself, all five would inherit it. To scope delegation to only the two pilots, the design must **split** them into a new group/constant (e.g. `DEEP_ANALYSIS_DELEGATED = RuntimeProfile("both","forked","deep","high", delegation="optional", roles=(...))`) and move only `se-research`/`se-fact-check` there, leaving the other three on plain `DEEP_ANALYSIS`. The builder rejects a skill appearing in two groups (`:283-285`).

### Validation (`validate_runtime_profile`, :253-265)

```python
def validate_runtime_profile(profile: RuntimeProfile) -> None:
    for field_name, value, allowed in (
        ("invocation", profile.invocation, KNOWN_RUNTIME_INVOCATIONS),
        ("context", profile.context, KNOWN_RUNTIME_CONTEXTS),
        ("model", profile.model, KNOWN_RUNTIME_MODELS),
        ("effort", profile.effort, KNOWN_RUNTIME_EFFORTS),
    ):
        if value not in allowed:
            raise RuntimeError(...)
```

A delegation axis needs one more tuple row here. If `roles` reference agent names, a stricter validator would also assert each role name resolves to a discovered agent — but note `registry.py` has **no** import of the generator's `agent_names()` (agents are discovered by the generator, not the registry). Cross-checking role→agent existence would introduce a new registry→templates/agents coupling, or must live in the generator/tests instead.

### Resolver (`build_skill_runtime_profiles`, :268-291)

Validates each group's profile (`validate_runtime_profile`), rejects unknown/duplicate skill names, requires every registered skill to have exactly one profile, returns a `SKILL_NAMES`-ordered `dict[str, RuntimeProfile]`. `SKILL_RUNTIME_PROFILES` is the module-level derived map (`:294-296`). A delegation field rides along automatically once it is on the dataclass — no resolver change unless delegation gets its own coverage checks.

`validate_registry()` (`:576-651`) re-derives and compares `SKILL_RUNTIME_PROFILES` at import time (`:635-641`); it does not currently inspect profile axes beyond that equality.

### How skills → profiles → generator overlay works (where delegation would emit)

The generator consumes `SKILL_RUNTIME_PROFILES` only for **Claude** overlays. `render_claude_skill` (`:485-520`) → `claude_frontmatter` (`:437-482`) reads `profile.invocation`, `profile.context`, `profile.model`, `profile.effort` and maps them to Claude frontmatter keys (`disable-model-invocation`, `user-invocable`, `context: fork`) and, for `fresh-session`, appends an in-body advisory note (`FRESH_SESSION_NOTE`, `:124-129`, applied `:512-519`).

There is currently **no per-skill body overlay for delegation**. The precedent for "portable intent that has no host frontmatter field" is exactly the `fresh-session` in-body note pattern (`FRESH_SESSION_MARKER` marker comment + appended note, `:124-129`, `:512-519`). A `delegation: optional` + roles overlay would most naturally follow that pattern: append a marker-tagged note to the generated body naming the optional roles — **but** the dispatch-section wording likely belongs in the canonical SKILL.md body (which serves all platforms), not just the Claude overlay, since inline platforms also read it. Design must decide: canonical body text (all platforms) vs generated Claude-only overlay note.

Codex/Amp skills ship the **canonical** SKILL.md verbatim (no overlay) — `build_rows()` only substitutes the generated path for `platform == "claude" and relative == "SKILL.md"` (`:927-928`). So anything delegation-related that must reach Codex/Amp must live in the canonical body.

### Registry snapshot coupling

`regenerated_registry_snapshot_text()` (`.github/scripts/generate-skill-surfaces.py:1012-1027`) serializes `schemaVersion, familyOrder, skills[{name,family}], platforms, sharedReferences` — it does **not** currently emit RuntimeProfile axes at all. So a `delegation` field would **not** force a snapshot schema bump unless the design chooses to expose delegation in the snapshot for `se-review-skills`' consumer. `REGISTRY_SNAPSHOT_SCHEMA_VERSION = 1` (`:55`); bumping it is coupled to `skill_review.SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS` (`:50-53`).

### Delegation contract language (runtime-routing.md)

`templates/skills/se-review-skills/references/runtime-routing.md:18` is the sole `delegation` mention:

```text
delegation: none | optional | required
roles: [name, bounded input, artifact, model-profile, effort]
```

This "Recommendation record" block (`:12-24`) is the source contract R4 points to. The `## Subagent decomposition` section (`:68-86`) already specifies the role contract prose: "smallest complete source set, explicit exclusions, authority boundary, expected artifact, stop condition. Cap concurrency to the host and task budget, prohibit recursive spawning, and keep task creation or edits with the parent." That is the same governance language R2/R3/R6 want in the agent bodies.

## Caveats / Not Found

- **Positional-constructor coupling** (all 11 constants) is the main blast-radius risk — a trailing default field is the low-risk path.
- **Group-sharing coupling**: se-research/se-fact-check share `DEEP_ANALYSIS` with 3 non-pilots; delegation must be scoped via a new constant/group to avoid leaking to the others.
- Registry has no agent-name registry and no import of the generator, so role→agent existence validation is not natively available in `registry.py`; it would be new coupling or a generator/test-side check.
- `__all__` (`:657-693`) would need `KNOWN_RUNTIME_DELEGATIONS` (and any new constant) exported if consumed elsewhere.
</content>
