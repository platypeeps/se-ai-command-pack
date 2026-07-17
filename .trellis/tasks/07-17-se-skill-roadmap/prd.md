# Expand SE skill families and workflows

## Goal

Plan and deliver the next general knowledge-work skill families, catalog taxonomy, and personal worklog boundary without disrupting flat installed skill paths.

## Background

The current shipped catalog covers research, briefs, meeting preparation,
landscape scans, and document digests. The next expansion should cover the
downstream work of deciding, planning, coordinating, monitoring, handing off,
and learning while keeping each skill's trigger and output distinct.

## Requirements

- Deliver the independently verifiable child tasks linked from this parent.
- Establish skill-family metadata before relying on families in later catalog
  additions.
- Keep canonical and installed skill paths flat and retain the `se-` prefix.
- Preserve framework-neutral skill wording and the existing generated-manifest,
  provenance, lifecycle, and release-gate contracts.
- Keep shipped product skills, installer lifecycle commands, and repo-local
  SD/Trellis development tooling as separate surfaces.
- Keep user-specific worklog settings outside the public core payload unless a
  reusable profile mechanism is explicitly designed and approved.

## Child Task Map

- `skill-family-taxonomy`: family metadata and grouped catalog foundation.
- `se-decide`, `se-status`, `se-fact-check`: first-priority workflow additions.
- `se-plan`, `se-handoff`, `se-monitor`, `se-retro`: follow-on workflows.
- `personal-worklog-profile`: private-profile boundary and feasibility design.

## Acceptance Criteria

- [ ] Every linked child task has testable requirements and can be implemented,
      checked, and archived independently.
- [ ] The catalog covers Understand, Decide, Coordinate, and Improve without
      ambiguous trigger overlap.
- [ ] Existing skill IDs and installed target paths remain compatible.
- [ ] Final integration review confirms generated surfaces, documentation,
      versioning, and the full repository quality gate are consistent.
- [ ] No user-specific path, identity, or private workflow contract is shipped
      in the public core by default.

## Out of Scope

- Implementing product behavior directly in this parent task.
- Plugin or marketplace packaging.
- Per-platform command adapters or category-based installer filtering unless a
  child task explicitly expands scope after separate approval.
