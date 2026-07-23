# Implementation plan: Session evidence for skill reviews

1. Update `templates/skills/se-review-skills/SKILL.md` with the session
   arguments, reference link, post-inventory session pass, finding gate, final
   report coverage, and privacy rules.
2. Add `references/session-evidence.md` with bounded discovery, invocation
   verification, causal classes, provenance, structural recommendations,
   gotchas, privacy, and unavailable-history behavior.
3. Extend `review-rubric.md`, `report-schema.md`, and `runtime-routing.md` so
   observed-use evidence is reviewed, reported, and delegated consistently.
4. Add focused behavior pins to `tests/test_skills.py`; rely on existing generic
   generation coverage to prove the new bundled reference fans out to every
   registered platform.
5. Bump the minor release version and changelog, then run `make generate` twice
   to confirm idempotence.
6. Run focused skill tests, generator/resource tests, `make check`, the release
   gate, task validation, and `git diff --check`.
7. Run `trellis-check`, review the full diff for privacy/portability regressions,
   and use `trellis-update-spec` if the session-evidence contract establishes a
   reusable repository convention not already captured here.

## Rollback points

- Before generation: revert only canonical skill/reference/rubric/schema/
  runtime/test edits.
- After generation: revert the canonical batch plus all generated manifests
  and catalogs together; never leave a partial payload fan-out.
- Do not change `skill_review.py` unless implementation proves a deterministic
  inventory contract is necessary. Session-history discovery remains semantic
  and conditional.
