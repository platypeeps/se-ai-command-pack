# Design the personal profile integration contract Design

## Overview

Adopt one user-owned Markdown profile with a stable, public schema and private
instance data. The pack ships only the schema and consumption rules; it never
ships a real profile, personal locator, connector credential, or source excerpt.

`se-profile` owns creation and mutation. `se-ask-me` and outward-facing skills
are read-only consumers. Consumer skills load a profile only from an explicit
locator or an opt-in private locator already configured in the host environment.
The public installer does not gain a profile/configuration subsystem in the
first version.

The artifact is an operating profile, not a personality score. It records
specific, reviewable assertions about preferences, goals, expertise, values,
voice, decision patterns, and boundaries. Every assertion remains attributable,
scoped, correctable, and forgettable.

## Proposal

### Public schema and private instance

Define the portable contract in a shared
`references/personal-profile-contract.md` resource. A conforming private
Markdown artifact uses this shape:

```markdown
---
schema: se-personal-profile/v1
profile_id: <user-chosen-stable-id>
updated_at: <ISO-8601 timestamp>
last_reviewed_at: <ISO-8601 timestamp or unknown>
default_scope: internal
---

# Personal Operating Profile

## Active Profile
### Identity And Context
### Values And Goals
### Expertise And Interests
### Working Preferences
### Communication And Voice
### Decision Patterns
### Boundaries

## Audience Overlays
## Proposed And Contested
## Evidence Ledger
## Review And Revision Log
## Personal Notes
```

`## Personal Notes` is user-owned. The other named sections are skill-managed,
but updates are previewed as section/entry changes and must preserve unknown
content. The initial implementation should use a dedicated profile note rather
than embedding managed sections in an unrelated note.

Represent each durable assertion as a compact Markdown entry with these fields:

- `id` — stable dotted identifier, such as `communication.directness`;
- `statement` — one bounded, falsifiable/useful proposition;
- `kind` — `identity`, `value`, `goal`, `expertise`, `interest`, `preference`,
  `voice`, `decision-pattern`, or `boundary`;
- `basis` — `explicit`, `observed`, or `inferred`;
- `status` — `confirmed`, `proposed`, `contested`, or `retired`;
- `confidence` — `high`, `medium`, or `low`;
- `scope` — `private-only`, `internal`, or `outward-safe`;
- `applies_to` — contexts/audiences/channels, or `general`;
- `first_observed`, `last_evidenced`, `last_confirmed`, and `review_after`;
- `evidence` — one or more evidence-ledger IDs; and
- optional `conflicts_with` and `notes`.

Only `confirmed` assertions appear in Active Profile. Observed assertions can be
confirmed after review; inferred assertions always start `proposed`. A direct
user correction made during an explicit maintenance request may create or
confirm an entry, but it still records provenance and revision history.

The evidence ledger stores stable IDs, source type, title/author when known,
locator, evidence date, retrieval date, coverage, and a minimal paraphrase or
short excerpt. It records whether text is user-authored, third-party, or
assistant-generated. Generated outputs and summaries cannot independently
corroborate a profile assertion derived from the same underlying source.

### Audience overlays

Store each overlay as metadata plus sparse operations against base assertion
IDs:

- overlay ID, label, purpose, intended audience, channels, and match terms;
- `prefer` — assertion IDs to emphasize;
- `suppress` — non-boundary preferences to de-emphasize for this context;
- `override` — a scoped replacement statement with its own full provenance;
- disclosure constraints, last confirmed/review dates, and status.

Provide synthetic starter examples for technical peers, executives, public
writing, close collaborators, and private reflection, but create none in a real
profile without user approval. Overlays cannot suppress or override boundaries,
confidentiality, factual integrity, or `private-only`/`outward-safe` controls.

Select overlays in this order:

1. explicit current invocation;
2. exactly one active overlay matching the stated audience and channel;
3. base profile with a disclosed ambiguity or no-match note.

Do not blend multiple overlays automatically. The user may explicitly request a
combination, in which case conflicts are surfaced and current instructions win.

### Discovery and persistence

Use a consumer argument contract of `profile=auto|off|<locator>` plus optional
`audience=`. `auto` means only an already-authorized profile attached to the
current context or resolved by a private host configuration; it never means
search every Obsidian vault, Notion workspace, or connected source. `off`
disables profile use for the invocation.

`se-profile` asks the user to select an Obsidian Markdown destination on first
write. If Obsidian capability is unavailable, it offers a user-selected Notion
page as fallback. Destination and locator details remain private. Every write
requires a preview, preservation check, write, read-back, and semantic
verification of changed entry IDs. Destructive replacement, destination
migration, and schema migration require explicit approval.

The Notion fallback preserves the same heading/entry contract in page blocks;
it does not require a database schema. Export must reproduce portable Markdown.

### Consumer contract

For profile-aware output, apply this precedence:

1. safety, privacy, confidentiality, and factual-integrity rules;
2. explicit current user instructions;
3. required audience, venue, and artifact constraints;
4. explicitly selected audience overlay;
5. confirmed context-matching outward-safe/internal profile assertions;
6. confirmed general profile assertions;
7. normal skill defaults.

Proposed, contested, retired, stale, or `private-only` assertions cannot silently
shape outward-facing output. A stale confirmed assertion may be used only when
low-risk and disclosed, or after one focused confirmation when it materially
changes the result.

Consumers load Active Profile and the selected overlay first. They consult the
Evidence Ledger only to resolve a material ambiguity; they must not reproduce
private evidence in output. They disclose material profile choices in a short
note such as the applied overlay and any stale/conflicting preference, not a
dump of profile contents.

Consumers never invent the user's experience, opinions, credentials,
relationships, results, or commitments. If a draft requires a first-person
claim absent from confirmed outward-safe entries, insert a question or marked
placeholder rather than fabricating it.

Initial profile-aware consumers should be:

- Create: `se-author`, `se-paper`, `se-proposal`, `se-tutorial`,
  `se-presentation`, and `se-publish`;
- Coordinate: `se-status`, `se-handoff`, `se-agenda`, `se-feedback`, and
  `se-meeting-follow-through` when their artifact is intended for others;
- Improve: `se-technical-editor` for voice-preservation review; and
- profile workflows: `se-profile` and `se-ask-me`.

Internal research, monitoring, capture, and mechanical operating skills should
not load the profile merely because it exists. Additional consumers require a
clear personalization benefit and profile-boundary tests.

### Review contract

An on-demand or scheduled review inventories changes since `last_reviewed_at`
and returns, without mutation:

- new explicit evidence and proposed assertions;
- changed or contradictory evidence;
- entries past `review_after`;
- possible overgeneralizations or context collapse;
- repeated evidence that derives from assistant-generated outputs;
- overlay overlap, drift, or unused overlays;
- unused/low-value entries and deletion or consolidation candidates; and
- a numbered proposed change set.

The user approves, edits, rejects, or defers each change. Only `se-profile` may
apply approved changes, followed by read-back. A configured cadence may schedule
a reminder/invocation through a separately authorized host capability; it never
authorizes autonomous source scanning or mutation.

### Shared reference and versioning

The approved contract should become
`templates/skills/_shared/references/personal-profile-contract.md`, fanned into
each implemented consumer through `SHARED_REFERENCES`. Version the schema in the
profile frontmatter. Additive optional fields remain compatible within v1;
renames, changed meanings, or required-field changes need migration preview and
a schema-version change.

The contract task itself completes the design and updates dependent task plans.
The shared reference first ships with `se-profile`, so this design-only task
does not create an orphan manifest payload or release bump.

## Boundaries And Non-Goals

- Do not commit a real profile, personal locator, vault/workspace name, identity,
  source excerpt, or credential to this public repository.
- Do not add public installer flags or configuration solely to locate the first
  profile version.
- Do not auto-discover all personal sources, continuously observe the user, or
  update the profile during ordinary skill consumption.
- Do not infer sensitive/protected attributes, diagnose personality or health,
  score the user, predict identity, manipulate communication, or profile other people.
- Do not use the profile as authentication or as authority to send, publish,
  decide, commit, or disclose information.
- Do not let audience overlays become separate inconsistent personas or weaken
  base boundaries.
- Do not require a profile for ordinary pack operation; unavailable/off profiles
  fall back to explicit current context and skill defaults.

## Affected Files

For this design task:

- `.trellis/tasks/07-17-personal-profile-contract/prd.md`
- `.trellis/tasks/07-17-personal-profile-contract/design.md`
- `.trellis/tasks/07-17-personal-profile-contract/implement.md`
- dependent task PRDs/designs where the consumer contract must be recorded.

When `se-profile` is implemented:

- `templates/skills/_shared/references/personal-profile-contract.md` — public
  schema, precedence, privacy, overlay, and review contract.
- `templates/skills/se-profile/SKILL.md` and its optional schema/example reference.
- `installer/registry.py` and `manifest.json` — shared-reference fan-out and payloads.
- `tests/test_skills.py` — profile-consumer membership and contract pins.
- `tests/test_generate.py` — shared-reference fan-out and validation coverage.
- affected consumer skill templates, README/operator docs, and release metadata.

No private Obsidian/Notion artifact is a repository file.

## Risks And Edge Cases

- A Markdown schema can become cumbersome. Keep the active section concise and
  place provenance/history later in the same artifact; do not introduce opaque
  sidecar state until real size limits are observed.
- Manual edits can omit required fields or create duplicate IDs. `se-profile`
  should validate, report, and propose repairs without discarding user text.
- A configured locator can become stale, inaccessible, or point at the wrong
  account. Confirm profile ID/owner context before mutation and never create a
  replacement silently.
- Notion and Obsidian formatting differ. Preserve semantic headings/fields and
  verify them after write rather than requiring byte-identical Markdown.
- Evidence locators may expose private channel/page names. Consumers normally
  load only active assertions; reports redact or summarize private locators.
- Confidence can masquerade as truth. Status, basis, scope, freshness, and
  contradictory evidence remain independently visible.
- Old behavior may be context-specific rather than a stable preference. Prefer
  narrow `applies_to` scopes and flag cross-context generalization in review.
- Assistant-authored drafts can create a feedback loop. Evidence lineage must
  trace to original user/source material and derived outputs cannot count as
  independent confirmation.
- The user's values and preferences can legitimately change. Recency informs
  review but never silently erases earlier evidence or overrides a direct correction.
- Automatically applying a public-writing overlay could be surprising. Require
  a unique match and disclose the selection; ambiguity falls back to base.
- Cross-skill adoption can create a large noisy change. Land the shared contract
  with `se-profile`, then update consumer skills in bounded releases or as each
  planned skill is implemented.

## Validation

- Validate synthetic Markdown examples containing complete, proposed,
  contested, retired, stale, conflicting, and manually edited entries.
- Pin required assertion fields, allowed enums, stable IDs, evidence lineage,
  and schema-version behavior.
- Pin that inferred entries start proposed and sensitive traits are never inferred.
- Pin overlay inheritance, selection precedence, conflict handling, sparse
  storage, and inability to weaken boundaries/scopes.
- Pin consumer precedence, `profile=auto|off|<locator>`, unavailable fallback,
  minimal disclosure, and no fabricated first-person claims.
- Pin review coverage, generated-output feedback-loop detection, numbered
  approval set, and no mutation before approval/read-back.
- Model Obsidian write/read-back, Notion fallback/export, destination conflict,
  schema migration, and manual-edit preservation with synthetic data.
- Scan every public fixture for real identities, home/vault paths, workspace
  names, private URLs, and source excerpts.
- Run `git diff --check` for this design task. The implementation task later runs
  focused tests, generation, and the full pack gate.
