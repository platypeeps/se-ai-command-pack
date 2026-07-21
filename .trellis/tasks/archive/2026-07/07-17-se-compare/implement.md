# Implement se-compare Implementation Plan

## Execution Order

1. Re-read the PRD/design, source standards, canonical `se-scan`, and planned
   `se-decide`/`se-evaluate` boundaries. Prepare synthetic comparison fixtures
   for comparable, complementary, version-mismatched, and evidence-asymmetric alternatives.
2. Add focused failing tests for criterion contracts, fair-frame discipline,
   cell states, missing/conflicting evidence, neutral ordering, no aggregate
   winner, sensitivity, and handoff boundaries.
3. Create `templates/skills/se-compare/SKILL.md` with the required section order,
   unknown-argument stop rule, and a minimal two-alternative table workflow.
4. Add source/version inventory, common-unit validation, six-state cells,
   confidence/caveats, and evidence-asymmetry reporting.
5. Add contextual strengths/weaknesses, tradeoffs, eligibility, qualitative
   sensitivity, dominance-under-frame, and highest-value missing evidence.
6. Add explicit routing for open candidate discovery (`se-scan`), rubric
   judgment (`se-evaluate`), and requested recommendation (`se-decide`).
7. Register under Understand/current flat paths, fan in `source-standards.md`,
   and add external-input safety pins.
8. Update the grouped catalog/operator documentation, run `make generate`, and
   inspect every platform payload plus shared-reference copy.
9. Select the release version from the then-current base, update manifest and
   changelog metadata, regenerate, and run the full validation gate.

The first implementation slice is a two-alternative, same-frame evidence table
with explicit unknown/conflicting cells and no recommendation. Sensitivity and
dominance language follow only after neutrality is pinned.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manual fixtures: same-category alternatives, complementary layers,
  mismatched versions/tiers, user-biased criteria, dependent criteria, private
  metric, conflicting benchmarks, stale evidence, unknown hard constraint,
  no meaningful difference, frame-dependent dominance, and requested winner.

## Documentation And Spec Updates

- Add `se-compare` under Understand in the generated/grouped catalog.
- Document its neutral artifact and boundaries from `se-scan`, `se-evaluate`,
  and `se-decide` with trigger examples.
- Document the six evidence states, criterion contract, missing-evidence rule,
  sensitivity language, and no-aggregate-winner rule.
- Update backend quality guidance only if implementation establishes a reusable
  fair-comparison convention beyond this skill.
- Record the new skill and selected release version in `CHANGELOG.md`.

## Review Notes

- Look for recommendations hidden in criterion choice, row order, adjectives,
  summaries, eligibility language, or a weighted/aggregate score.
- Challenge every normalization for equivalent units, dates, versions,
  configurations, denominators, and measurement methods.
- Verify missing evidence stays unknown and conflicting evidence stays visible.
- Confirm each alternative receives the same criteria and parallel prose, while
  genuinely non-applicable criteria retain an evidence-backed reason.
- Confirm dominance is labeled as frame-dependent and the user-specific choice
  routes to `se-decide`.
- Confirm no open-ended market discovery or live mutation/benchmarking occurs.

## Follow-Ups

- Add machine-readable comparison export only after a concrete downstream
  consumer requires it.
- Let `se-decide` consume the neutral comparison artifact without duplicating
  evidence gathering when both skills are implemented.
- Consider specialized benchmark protocols only as separate domain tasks with
  validated measurement rules.
