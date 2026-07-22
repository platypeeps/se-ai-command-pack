# Expand SE skill families and workflows

## Goal

Coordinate the 50 linked roadmap children that expand the public SE catalog
across six outcome families, while preserving flat installed skill paths and an
explicit boundary between portable product skills and private personal context.

## Background

This roadmap began with nine children covering taxonomy, decision support,
delivery coordination, and a personal-worklog boundary. It now contains 50
independently planned children spanning Understand, Decide, Create, Coordinate,
Operate, and Improve.

The parent metadata is the source of truth for membership and completion. At
this reconciliation point, all 50 children are completed and archived, and
every linked child has a PRD, design, implementation plan, and planning/check
context files. The parent remains a coordination and integration envelope; it
does not implement product behavior directly.

## Requirements

- Deliver the independently verifiable child tasks linked from `task.json`.
- Keep parent planning synchronized with child membership, priority, status,
  and archive state whenever the roadmap expands or a delivery cohort closes.
- Use the six registered outcome families: Understand, Decide, Create,
  Coordinate, Operate, and Improve.
- Establish and preserve family metadata before relying on it in catalog or
  documentation changes.
- Keep canonical and installed skill paths flat and retain the `se-` prefix.
- Preserve framework-neutral skill wording and the existing generated-manifest,
  provenance, lifecycle, and release-gate contracts.
- Keep shipped product skills, installer lifecycle commands, and repo-local
  SD/Trellis development tooling as separate surfaces.
- Keep user-specific worklog settings outside the public core payload. Any
  reusable personal profile must use the approved portable profile contract,
  explicit consent, provenance, and correction controls.
- Treat the delivery cohorts below as planning groups, not permission to batch
  unrelated children into a single implementation or release.

## Child Task Map

| Delivery cohort | Children | State |
| --- | --- | --- |
| Foundation | `skill-family-taxonomy`, `se-decide`, `se-status`, `se-fact-check`, `se-help`, `personal-profile-contract` | 6 completed |
| Personal context boundary | `se-profile`, `se-ask-me`, `personal-worklog-profile` | 3 completed |
| Plan and coordinate | `se-plan`, `se-handoff`, `se-monitor`, `se-retro` | 4 completed |
| Capture and knowledge operations | `se-capture`, `se-video-notes`, `se-thread-digest`, `se-knowledge-capture`, `se-watchlist`, `se-weekly-review`, `se-action-inbox`, `se-knowledge-gap`, `se-publish`, `se-meeting-follow-through`, `se-bookmark-triage` | 11 completed |
| Understand and learn | `se-distill`, `se-explain`, `se-literature-map`, `se-compare`, `se-learn`, `se-study-guide`, `se-socratic-review` | 7 completed |
| Create and communicate | `se-author`, `se-topic-radar`, `se-technical-editor`, `se-paper`, `se-proposal`, `se-tutorial`, `se-presentation`, `se-diagram` | 8 completed |
| Coordinate and operate | `se-stakeholder-map`, `se-feedback`, `se-agenda`, `se-runbook`, `se-sop`, `se-checklist` | 6 completed |
| Improve and assure | `se-premortem`, `se-evaluate`, `se-red-team`, `se-postmortem`, `se-review-skills` | 5 completed |

These cohorts organize delivery and review. The family assigned to a shipped
skill remains owned by the taxonomy source of truth and the child's accepted
design; cohort placement does not create a second taxonomy.

## Acceptance Criteria

- [x] Every linked child task has testable requirements and can be implemented,
      checked, and archived independently.
- [x] The parent child map accounts for all 50 `task.json` children exactly
      once and distinguishes completed work from planned work.
- [x] The final catalog uses all six registered families without ambiguous
      trigger overlap. Evidence: `final-integration-review.md`, "Catalog and
      trigger-boundary accounting."
- [x] Existing skill IDs and installed target paths remain compatible.
      Evidence: `final-integration-review.md`, "Cross-layer evidence."
- [ ] The personal-profile and private-worklog boundaries remain consent-driven,
      provenance-backed, correctable, and absent from the public core by default.
      Blocked by FIR-01 in `final-integration-review.md`; resolution is routed
      to `07-22-roadmap-integration-findings`.
- [ ] Final integration review confirms generated surfaces, documentation,
      versioning, and the full repository quality gate are consistent. The
      mechanical gates pass, but FIR-01 and FIR-02 in
      `final-integration-review.md` remain open and are routed to
      `07-22-roadmap-integration-findings`.
- [ ] The parent is archived only after all deliverable children are complete or
      intentionally removed through an explicit roadmap decision. All children
      are complete; archive only after the blocking findings are resolved and
      post-merge finish-work runs.

## Out of Scope

- Implementing product behavior directly in this parent task.
- Treating a planning cohort as a hard runtime dependency or mandatory mega-PR.
- Plugin or marketplace packaging.
- Per-platform command adapters or category-based installer filtering unless a
  child task explicitly expands scope after separate approval.
