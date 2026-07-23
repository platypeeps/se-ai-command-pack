# Bound se-review-skills inventory output

## Goal

Add a safe bounded-output preservation path for the `se-review-skills`
analyzer so full repository and installed-copy inventories remain complete and
parseable when ordinary tool transport cannot carry the full response.

## Background

- Review snapshot:
  `230ef6a407b002089a70addee2f3d1eaa0e6df1bf5a65e89fd15f4450d0e7255`.
- Finding: `1.7.9.1`; routing state was `untracked` during snapshot
  reconciliation.
- A default repository-plus-installed-roots inventory measured 364,977 bytes
  and ordinary tool transport truncated it twice before a high-budget recovery
  path preserved it.
- The analyzer already produces deterministic schema-version-3 inventory JSON
  and a content-derived `snapshotId`; existing stdout behavior is compatible
  and must remain available.

## Requirements

- Provide an explicit analyzer mode that preserves the complete inventory JSON
  outside ordinary transcript output while returning a small, parseable result
  envelope to stdout.
- Keep the inventory payload and `snapshotId` deterministic and semantically
  identical regardless of whether the caller selects legacy stdout, pretty
  stdout, or bounded-output mode.
- The bounded stdout envelope must identify success or failure and include the
  `snapshotId`, selected-skill and installed-copy counts, coverage limits, and
  the locator of the complete inventory artifact. It must not repeat the full
  skill or installation records.
- Persist inventory JSON only when the caller explicitly supplies a destination.
  Do not silently create a report, cache, workspace file, or repository artifact.
- Validate the destination before writing. Refuse symlinks, directories,
  escaped or unbounded destinations, and unsafe replacement of unrelated
  content. Write atomically so interruption cannot leave a successful-looking
  partial JSON artifact.
- Update the canonical `se-review-skills` workflow with the bounded-output path,
  safe destination rules, verification step, and recovery behavior for hosts
  whose normal tool transport cannot preserve the complete analyzer response.
- Preserve the analyzer's existing read-only relationship to reviewed skills:
  no reviewed-content execution, imports, network access, installation changes,
  repository-source mutation, or inferred persistence authority.
- Keep existing selectors, schema fields, ownership evidence, installed-copy
  mapping, snapshot hashing, and legacy stdout behavior compatible unless a
  separately documented breaking change is unavoidable.
- Limit implementation changes to the canonical skill and analyzer under
  `templates/skills/se-review-skills/**`; use `tests/test_skill_review.py` only
  to establish and protect behavior.

## Technical Notes

- Bounded-output mode requires both an explicit destination and an explicit
  bounded destination root. It must reject paths outside that root and paths
  within reviewed repositories or installed-skill roots.
- An existing destination may be replaced only when it is a valid analyzer
  inventory whose embedded snapshot matches its content.
- The complete artifact is written atomically; stdout carries only a bounded
  success/failure envelope and never repeats skill or installation records.

## Out of Scope

- Changing inventory selection, ownership, deduplication, candidate signals,
  schema-version-3 fields, or snapshot hashing inputs.
- Persisting inventory by default, choosing destinations implicitly, or
  creating repository reports, caches, or workspace artifacts.
- Editing installed copies or executing, importing, or contacting reviewed
  content.

## Acceptance Criteria

- [x] A fixture whose complete inventory exceeds the ordinary transcript budget
      produces bounded, parseable stdout and a complete parseable JSON artifact.
- [x] The bounded envelope reports the same `snapshotId`, counts, and coverage
      limits as the preserved full payload.
- [x] Legacy, pretty, and bounded-output modes calculate the same snapshot for
      the same source and installation state.
- [x] The analyzer creates no inventory artifact unless the caller explicitly
      supplies an output destination.
- [x] Destination tests reject symlinks, directories, unsafe roots or escapes,
      and replacement of unrelated existing content without leaving partial
      output.
- [x] An interrupted or failed write cannot be mistaken for a complete
      inventory, and the skill documents the safest rerun and verification path.
- [x] Existing inventory, ownership, path-boundary, installed-copy, no-execution,
      and snapshot tests remain green.
- [x] Focused analyzer tests, skill contract tests, generated-target checks, and
      the repository quality gate pass.

## Notes

- Planning was published separately in PR #99 before implementation began.
