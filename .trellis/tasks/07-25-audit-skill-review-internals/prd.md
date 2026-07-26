# skill_review internals cleanup

## Goal

The shipped skill_review.py has one path-containment predicate and one authoritative frontmatter grammar, so its boundary checks stay auditable and its metadata classification cannot diverge from what the generator validated.

## Requirements

- Collapse _is_relative_to (:211) and _is_within (:1545) into one helper used at every call site. [A-009]
- Declare the generator's YAML grammar authoritative; make the shipped dependency-free parser a strict subset that rejects (rather than reinterprets) constructs outside it. [A-010]
- Add a shared conformance test asserting both parsers agree over all canonical and generated SKILL.md frontmatter in the repo.
- Payload change: version bump + changelog per release discipline.

## Acceptance Criteria

- [ ] One containment helper remains, all call sites migrated.
- [ ] Conformance test passes over every SKILL.md in templates/ and generated/; out-of-subset construct is rejected with a clear error.

## Notes

- Audit findings: A-009 (P3/S), A-010 (P3/M) — .trellis/audit/report-2026-07-25.md.
- Evidence: templates/skills/se-review-skills/scripts/skill_review.py:211, :1545, :509, :1690, :412, :1532; .github/scripts/generate-skill-surfaces.py:161.
