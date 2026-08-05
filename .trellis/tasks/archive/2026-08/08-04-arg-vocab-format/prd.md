# Argument vocabulary format density classification

## Goal

Resolve the one judgment part of the verbosity axis: decide, per `format=`
declaration, whether its values are a *density ladder* (verbosity in disguise,
→ `depth=`) or a genuine *output shape* (stays `format=`). Isolated from the
mechanical verbosity rename so the risky judgment is a small, separate PR (D-3).

Parent decision + rationale: `07-25-audit-skill-arg-vocabulary/design.md`.
Ordering: parent `implement.md`. Land after `08-04-arg-vocab-verbosity`, before
`08-04-arg-vocab-locator` / `08-04-arg-vocab-enforce`.

## Requirements

- Review every `format=` declaration across the 53 skills. Migrate pure density
  ladders (`compact|standard`, `standard|compact` — e.g. se-thread-digest,
  se-meeting-follow-through) to `depth=` per the canonical ladder.
- Leave genuine structural output shapes as `format=` (`ledger|memo`,
  `table|memo`, `prose|walkthrough|qa`, `mermaid|brief`, `register|brief`,
  `technical-blog|tutorial|…`, `markdown|summary`, `facilitator`, …).
- Resolve the borderline cases explicitly: `se-sop format=full|compact`,
  `se-runbook format=full|quick-reference` — default "keep as shape unless the
  value pair is a pure density ladder"; record the call per declaration.
- If a skill ends up with both a migrated `depth=` and a residual structural
  `format=`, keep both. Regenerate mirrors; version bump + changelog.

## Acceptance Criteria

- [x] Every `format=` declaration classified; density ladders migrated to
      `depth=`; structural shapes retained as `format=`; borderline calls
      recorded.
- [x] No `format=` declaration remains that is purely a verbosity/density ladder.
- [x] `make test` + `make release-check` green; mirror regenerated; version bump
      + changelog citing A-006.
