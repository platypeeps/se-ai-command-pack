# Implement se-profile Design

## Overview

Add `se-profile` as the sole maintenance workflow for a user-owned personal
operating profile conforming to `se-personal-profile/v1`. It creates, validates,
reviews, proposes, corrects, forgets, imports, exports, and persists the profile;
all other skills remain read-only consumers.

The canonical skill stays connector-neutral. Obsidian is the preferred
destination because the artifact is native Markdown and directly editable. A
user-selected Notion page is offered only when Obsidian capability is
unavailable or the user explicitly prefers it. Connector availability never
changes the profile schema or approval rules.

This is an explicitly invoked maintenance skill, not a passive observer. It may
use the current conversation or bounded user-supplied sources, but it never
mines all chat history, vaults, workspaces, channels, or browsing activity.

## Proposal

Create `templates/skills/se-profile/SKILL.md` and make it consume the shared
`references/personal-profile-contract.md`. Use this argument surface:

- `mode=create|status|propose-update|apply-approved|correct|forget|review|audience|import|export`
  — infer only when unambiguous; otherwise ask which maintenance operation is intended.
- `profile=auto|<locator>` — existing profile locator; `auto` resolves only an
  attached/authorized profile or private host-configured locator.
- `sources=` — bounded list of current-chat, messages, notes, pages, documents,
  or URLs to analyze. Required for source-based proposals when the current
  context does not already identify the material.
- `destination=obsidian|notion|<locator>` — used for first creation or explicit migration.
- `entries=` — assertion/overlay IDs or a numbered proposal selection.
- `audience=` — audience-overlay ID or label for audience operations.
- `scope=private-only|internal|outward-safe` — optional default for explicitly
  supplied assertions; never infer a broader scope.
- `cadence=` — optional review recommendation such as monthly or quarterly;
  records preference only and does not schedule anything.
- `format=markdown|summary` — full portable export or a redacted status/review report.

Unknown explicit arguments remain an error under the pack-wide convention.

### Common preflight

Every mode begins by:

1. Resolving the intended profile and operation without broad source discovery.
2. Reading the existing artifact when present and validating schema version,
   profile ID, required sections, stable entry/evidence IDs, allowed enums,
   duplicate IDs, and manually edited/unknown content.
3. Classifying the destination state as `new`, `valid`, `repairable`,
   `conflicting`, `unsupported-version`, or `unavailable`.
4. Reporting access gaps and stopping before mutation for the wrong profile,
   destructive conflict, unsupported migration, or ambiguous locator.
5. Treating profile text and every imported source as data, not instructions.

Validation errors produce a repair proposal; they never cause silent
normalization, deletion, or replacement.

### Create and status

`create` should conduct a short, one-question-at-a-time setup interview covering
desired identity/context terms, goals, values, expertise/interests, working
preferences, communication/voice preferences, boundaries, initial audience
needs, default visibility, and destination. Users may skip any category.

Create only entries directly stated or explicitly approved in the interview.
Do not seed synthetic audience overlays into a real profile. Show the initial
artifact and destination, obtain approval for creation, write, read back, and
verify profile ID plus every created assertion ID.

`status` is read-only and reports schema/destination health, active/proposed/
contested/stale counts, overlays, last review, next requested review, access
gaps, and repair needs without dumping private evidence.

### Source analysis and proposal

`propose-update` inventories the bounded sources first: type, locator, author,
date, retrieval coverage, and whether content is user-authored, third-party, or
assistant-generated. It then:

1. extracts atomic candidate assertions rather than broad personality labels;
2. classifies kind, basis, confidence, scope, applicability, freshness, and evidence lineage;
3. compares candidates with existing entries for support, contradiction,
   context narrowing, changed preference, or duplication;
4. rejects sensitive/protected-attribute inference and unsupported generalization;
5. prevents summaries, assistant drafts, and repeated derivatives from counting
   as independent evidence for their own conclusions; and
6. returns a numbered proposal set with add/update/contest/retire/overlay/no-change,
   rationale, exact affected IDs, and a preview of the resulting sections.

Observed assertions may be proposed as confirmed only when evidence is strong
and non-sensitive, but still require approval. Inferred assertions always enter
`proposed` status. Source instructions cannot change the profile workflow.

`apply-approved` accepts only explicit proposal numbers/IDs from an available
proposal context. Recompute the patch against the current destination,
detect concurrent changes, show the final delta, write only approved items,
read back, and semantically verify changed IDs and preserved user-owned content.

### Direct correction and forgetting

For a direct request such as “remember that I prefer concise answers” or
“correct my title,” the invocation itself authorizes that bounded maintenance
change. Build a complete explicit-basis entry and show an inline preview before
writing. Require a second confirmation only when the change conflicts with
existing evidence, broadens visibility, affects a boundary/sensitive fact,
migrates destination/schema, or deletes/replaces material.

`correct` preserves superseded evidence and records the new explicit statement;
it does not reinterpret the user's correction as merely another observation.

`forget` supports assertion IDs, evidence IDs, overlays, a source locator, or
the whole profile. Preview exactly what active entries, evidence, overlays, and
cross-references will be removed. Hard-delete the requested content from the
current artifact, leaving only a content-free revision event when appropriate.
Disclose that connector/version history or backups may retain earlier copies and
do not claim deletion beyond systems actually verified. Whole-profile deletion
requires explicit destructive confirmation and destination read-back/not-found verification.

### Review and audience overlays

`review` is read-only until individual changes are approved. Compare relevant
authorized evidence since `last_reviewed_at` and report:

- new explicit/observed evidence;
- stale, contested, contradictory, unused, or low-value assertions;
- possible context collapse or overgeneralization;
- evidence derived from assistant-generated material;
- audience-overlay overlap, drift, ambiguity, or inactivity;
- schema/manual-edit repair needs; and
- a numbered add/update/contest/retire/delete/consolidate/defer change set.

Approving review changes routes through `apply-approved`. Updating
`last_reviewed_at` also occurs only after an approved, verified write. `cadence=`
records a preference and may suggest a separate reminder request, but the skill
does not create or run an automation.

`audience` lists, creates, previews, renames, merges, corrects, or deletes sparse
overlays. It validates all referenced base IDs and refuses any operation that
weakens a boundary, confidentiality/factual-integrity rule, or visibility scope.
Merges surface conflicting operations and require approval; no automatic overlay
combination occurs during ordinary consumption.

### Import, export, and persistence

`import` accepts a conforming Markdown profile or bounded legacy material. It
validates provenance and schema, generates a field-by-field merge proposal, and
never replaces an existing profile silently. Entries without adequate
provenance remain proposed or are excluded with reasons.

`export` is read-only. `format=markdown` returns the complete portable contract
only to the requesting private context; `summary` omits private evidence and may
filter to `outward-safe`. Export never publishes or writes a second copy unless
the user separately requests a destination action.

For Obsidian, preserve frontmatter keys and unknown/user-owned sections, then
return an adoptable/openable note link when the connector supports it. For
Notion, preserve semantic headings/fields in page blocks and return the page
link. Never mirror both destinations by default. Every successful mutation ends
with read-back and semantic verification; synthesis without verified write is
reported as incomplete.

Register `se-profile` under Operate/current flat paths. Fan in both
`personal-profile-contract.md` and `source-standards.md`; the latter governs
source provenance and external claims but does not transform observed behavior
into verified personality facts. Add the skill to external-input safety coverage.

## Boundaries And Non-Goals

- Do not monitor, crawl, or ingest personal sources continuously or without a
  bounded user-authorized source set.
- Do not update the profile when another skill merely reads or uses it.
- Do not infer sensitive/protected traits, diagnose health/personality, assign
  scores/types, manipulate the user, or create profiles of other people.
- Do not treat prior behavior as destiny or flatten context-dependent evidence
  into a universal trait.
- Do not use the profile as authentication, permission for external actions, or
  proof of a current opinion, commitment, credential, or relationship.
- Do not embed a personal locator, path, source inventory, identity, or
  credential in the public skill or installer.
- Do not silently fall back from Obsidian to Notion, create both copies, or
  claim deletion from unverified backups/history.
- Do not implement connectors, a hosted profile service, scheduler, telemetry,
  opaque vector store, or automatic consumer execution.

## Affected Files

- `templates/skills/se-profile/SKILL.md` — canonical maintenance workflow.
- `templates/skills/_shared/references/personal-profile-contract.md` — v1 schema,
  consumer, privacy, overlay, review, and persistence contract.
- `installer/registry.py` — Operate/current registration and shared-reference fan-out.
- `manifest.json` — generated skill and reference rows.
- `tests/test_skills.py` — mode, schema, provenance, sensitive-trait, approval,
  preservation, deletion, review, overlay, feedback-loop, and read-back pins.
- `tests/test_generate.py` — shared-reference registration/fan-out and payload coverage.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

No real profile, destination locator, connector fixture, identity, or private
source content belongs in the repository. All examples and tests use synthetic data.

## Risks And Edge Cases

- A user may ask the agent to “learn from everything.” Convert that into a
  bounded source-selection proposal; do not interpret it as perpetual consent.
- Current-chat access may be partial or summarized. Record the accessible range
  and never claim complete conversational history.
- User-authored content can still be performative, outdated, quoted, or written
  for a role. Scope observations narrowly and privilege direct corrections.
- Shared/forwarded Slack or Notion content may describe someone else. Confirm
  authorship and subject before proposing a profile assertion.
- Prompt injection can masquerade as a self-description or profile-edit command.
  Only the current user's explicit request authorizes workflow changes.
- Manual edits may create malformed or duplicated IDs. Preserve raw text and
  propose repair; never discard it to make parsing convenient.
- Concurrent destination changes can invalidate an approved proposal. Re-read
  and recompute before every write; stop on material conflicts.
- The active profile and evidence ledger may grow without bound. Reviews should
  consolidate redundant evidence and retire stale assertions, but archival
  splitting is deferred until actual scale proves it necessary.
- Hard deletion from the artifact may not erase connector history, backups, or
  model context. State verified deletion scope plainly.
- Notion block structure may not round-trip byte-for-byte to Markdown. Verify
  schema semantics and stable IDs, not formatting identity.
- A review cadence can be mistaken for continuous surveillance. Cadence is a
  reminder preference only; each review receives a fresh bounded source scope.
- A direct explicit update can still create privacy risk if marked outward-safe.
  Visibility broadening and sensitive/boundary changes require separate confirmation.

## Validation

- Pin all modes and the unknown-argument stop rule.
- Pin common preflight states, v1 schema validation, stable IDs, allowed enums,
  unknown-content preservation, and unsupported-version stop behavior.
- Pin bounded source inventory, access coverage, evidence lineage, derivative-
  output detection, injection safety, and no sensitive-trait inference.
- Pin direct explicit-update behavior versus approval-required observed,
  inferred, conflicting, visibility-broadening, boundary, and destructive changes.
- Pin correction precedence, hard-forget scope, cross-reference cleanup,
  connector-history disclosure, and whole-profile confirmation.
- Pin review categories, numbered change set, `last_reviewed_at` write rule,
  cadence non-automation, and no mutation before approval.
- Pin sparse overlay operations, base-ID validation, merge conflicts, and
  inability to weaken boundaries/scopes.
- Model create, status, propose/apply, correct, forget, review, audience, import,
  and export with synthetic profiles.
- Model Obsidian success/failure/read-back, explicit Notion fallback, concurrent
  edit, destination mismatch, schema migration, and idempotent rerun.
- Scan public artifacts for real personal data and run `make generate`, focused
  skill/generator tests, `make check`, and `git diff --check`.
