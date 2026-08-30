# Design: per-target runtime profile overlays

## Context

The skill reviewer now produces portable runtime recommendations, but the pack
ships one canonical `SKILL.md` byte stream to every platform. That was the safe
initial design because canonical Agent Skills and Codex metadata do not accept
Claude-specific runtime fields. It also means reviewed fork/model/effort choices
never become operational.

Claude Code now documents exact skill frontmatter for invocation controls,
`context: fork`, model aliases, and effort. Codex still requires portable
`name`/`description` frontmatter; its optional `agents/openai.yaml` controls UI
presentation rather than per-skill execution. The implementation therefore
adapts only the verified Claude surface.

## Data flow and ownership

```text
SKILLS + RUNTIME_PROFILES + SKILL_RUNTIME_PROFILES
                         |
canonical SKILL.md ------+--> validate portable inputs
                              |
                              +--> render canonical bytes (agents, Codex)
                              |
                              +--> render Claude frontmatter + canonical body
                                      |
                                      +--> generated/skills/claude/*/SKILL.md
                                                |
                                                +--> manifest source rows
                                                          |
                                                          +--> installer copy,
                                                               hash, receipt
```

`installer/registry.py` owns declarations and portable values. The generator
owns validation and platform translation. The manifest owns the source-to-target
copy plan. The installer remains a byte-copying consumer and needs no new
transform logic.

## Registry model

Add a frozen `RuntimeProfile` record with:

```python
invocation: str  # automatic | user-only | both
context: str     # inline | forked | fresh-session
model: str       # inherit | fast | balanced | deep
effort: str      # low | medium | high | xhigh
```

Define named immutable profiles once, then map every skill name to one profile.
Validation checks:

- profile values belong to the portable allowlists;
- the assignment keys equal `SKILL_NAMES` exactly;
- no assignment key is unregistered; and
- registry construction cannot silently overwrite duplicate skill membership.

Use grouped tuples as the authored assignment input and derive the final mapping
only after duplicate detection. This keeps similar recommendations concise while
making cross-group duplicates such as the earlier `se-evaluate` error fatal.

### Reviewed assignments

| Profile | Invocation | Context | Model | Effort | Skills |
|---|---|---|---|---|---|
| conversational | both | inline | balanced | medium | `se-brief`, `se-meeting-prep`, `se-decide`, `se-status`, `se-action-inbox`, `se-agenda`, `se-checklist`, `se-diagram`, `se-distill`, `se-explain`, `se-handoff`, `se-learn`, `se-meeting-follow-through`, `se-monitor`, `se-plan`, `se-presentation`, `se-publish`, `se-retro` |
| deep-analysis | both | forked | deep | high | `se-research`, `se-fact-check`, `se-knowledge-gap`, `se-literature-map`, `se-evaluate` |
| bounded-synthesis | both | forked | balanced | medium | `se-scan`, `se-digest`, `se-compare`, `se-study-guide`, `se-video-notes`, `se-thread-digest`, `se-bookmark-triage`, `se-watchlist`, `se-feedback`, `se-premortem` |
| personal-dialogue | user-only | inline | deep | high | `se-ask-me`, `se-socratic-review` |
| profile-mutation | user-only | inline | inherit | high | `se-profile`, `se-knowledge-capture` |
| artifact-authoring | user-only | inline | deep | high | `se-author`, `se-topic-radar`, `se-paper`, `se-proposal`, `se-stakeholder-map`, `se-runbook`, `se-postmortem`, `se-weekly-review` |
| instructional | both | inline | deep | high | `se-tutorial`, `se-sop`, `se-technical-editor` |
| discovery-utility | both | inline | fast | low | `se-help` |
| capture-utility | both | inline | fast | medium | `se-capture` |
| independent-red-team | user-only | fresh-session | deep | xhigh | `se-red-team` |
| package-review | user-only | inline | deep | xhigh | `se-review-skills` |

The groups cover all 52 registered skills exactly once. `se-evaluate` follows
the detailed independent review (forked/deep/high), not the duplicated summary
row that also placed it in the conversational profile.

## Platform capability adapter

Declare platform support explicitly rather than switching on brand names in
multiple functions:

| Platform | Canonical body | Frontmatter overlay | Model map | Context map |
|---|---|---|---|---|
| `agents` | yes | none | unsupported | unsupported |
| `codex` | yes | none | unsupported | unsupported |
| `claude` | yes | invocation/model/effort/context | `inherit`, `haiku`, `sonnet`, `opus` | `forked` only |

Claude rendering uses stable key order:

1. `name`
2. `description`
3. `disable-model-invocation` when user-only
4. `user-invocable` only if a future automatic-only profile is added
5. `context` when forked
6. `model`
7. `effort`

No `agent` is emitted. The runtime review recommended isolation, not a specific
Claude subagent type, and adding a type would invent a second decision.

`fresh-session` is a known portable recommendation with no Claude skill
frontmatter equivalent. It deliberately renders no `context` field. Unknown
portable values, adapter keys, aliases, and effort values are errors.

## Generated payloads

Generated Claude entrypoints live under:

```text
generated/skills/claude/<skill>/SKILL.md
```

They are committed release payloads and begin directly with valid skill YAML;
no marker is inserted into the body. Each generated body must exactly equal the
body parsed from its canonical source. Supporting resources remain canonical
and shared across platforms.

`build_rows()` selects the generated source only for the Claude `SKILL.md` row.
This avoids installer-time transformations, keeps receipt hashes meaningful,
and preserves the existing manifest/file-operation trust boundary.

The generator computes and validates all Claude payloads, manifest text, README,
and help catalog before writing. The existing coordinated writer is extended to
include the generated files. On write failure it restores prior files and
removes newly created ones. `--check` reports every missing or drifted generated
entrypoint independently.

## Failure and compatibility behavior

- A bad runtime declaration fails during registry/generator validation before
  any output changes.
- A missing generated directory is created only during apply, never check mode.
- Unexpected generated skill entrypoints are reported as drift so retired or
  renamed skills cannot remain in the release payload.
- User-modified installed files still conflict unless `--force` is explicit.
- Existing canonical Claude installs will require the normal forced pack
  refresh because the shipped bytes intentionally change; backup semantics stay
  unchanged.
- Agents and Codex installations remain byte-compatible with the previous
  canonical source.

## Verification strategy

Focused registry/generator tests pin coverage, translation, canonical body
preservation, unsupported-field failures, generated drift, coordinated rollback,
and manifest source selection. Installer tests compare installed bytes to the
manifest-selected source for each platform and retain conflict/backup coverage.

The full gate is `make generate`, focused unit tests while iterating, then
`make check` and `git diff --check`. Generation is run twice to prove
idempotence. Because payload bytes change, the manifest version and changelog
are updated before the release check.

## Documentation impact

Update the backend directory/quality guidance with the registry-owned runtime
profile and generated-overlay contract. Update the review skill's runtime
routing reference to say Claude recommendations can now be applied by this pack,
while Codex/shared-agent recommendations remain advisory until those hosts expose
validated execution controls.

## Out of scope

- Adding a new installation platform.
- Generating Codex `agents/openai.yaml`; it does not enforce model or context.
- Selecting Claude `agent` types or tool grants.
- Emulating `fresh-session` with a forked subagent.
- Changing canonical skill instructions beyond the reviewer reference status.
