# Add `se-review-skills` Implementation Plan

## Phase 1 — Confirm contracts

- [x] Re-read the converged PRD and design; start implementation only after user
      approval.
- [x] Load backend/project specs with `trellis-before-dev` before editing.
- [x] Confirm the canonical name `se-review-skills`, Improve-family placement,
      and roadmap child count.
- [x] Confirm arbitrary-skill discovery boundaries plus ownership routing for
      SD upstream, SE upstream, and generic repo-local skills.
- [x] Confirm the first-party template allowlists: SE `templates/skills/**` and
      SD `templates/**`. Record registries, generators, manifests, tests, and
      installed copies as read-only evidence rather than review/change targets.
- [x] Decide whether platform metadata overlays are required for the first
      release. Default: recommendations only; keep canonical frontmatter
      portable.
- [x] Record exact current official plugin and host-skill metadata behavior in a
      bounded research note so implementation does not rely on stale names.

## Phase 2 — Deterministic analyzer and ownership resolver

- [x] Keep one bounded, standard-library metadata parser portable across roots;
      keep the generator authoritative for SE write validation and pin the
      shared observable contract in tests.
- [x] Implement SE, SD, and generic adapters over one stable skill-record schema.
- [x] Classify every path as authored template, generated template adapter,
      installed copy, or local override; resolve installed observations back to
      a canonical template before producing selectable findings.
- [x] Build a registry-derived target capability matrix covering content
      sharing/adaptation, frontmatter, command format, UI metadata, context,
      model routing, and validation without assuming cross-host equivalence.
- [x] Add review signals and output fields for progressive disclosure,
      deterministic-helper opportunities, failure paths, portability, context
      cost, evaluation coverage, and bounded subagent decomposition.
- [x] Inventory existing bundled scripts and code/command blocks; require every
      script-extraction finding to define deterministic inputs, outputs, errors,
      side effects, portability, dependencies, idempotence or dry-run behavior,
      tests, and the judgment/approval boundary that remains in prose.
- [x] Implement read-only `inventory` JSON for explicit paths plus skill,
      family, repository, package, and all-within-root scopes.
- [x] Add source, ownership, and snapshot hashing with deterministic ordering.
- [x] Add signals for size, repeated text, trigger similarity, section/reference
      duplication, sibling names, and pinned tests; label them non-authoritative.
- [x] Resolve canonical ownership through Git roots, trusted provenance target
      mappings, manifest identity, and verified remotes; split drifted local
      copies from upstream-reproducible findings.
- [ ] Unit-test malformed frontmatter, invalid selectors, missing registry rows,
      path traversal, symlink/provenance boundaries, external plugin skills,
      absent families, empty repositories, stable hashes, and all 903 current SE
      pair candidates without treating similarity as a finding.
- [x] Test that SE review scope cannot escape `templates/skills/**`, SD scope
      cannot escape `templates/**`, installed copies remain read-only, symlinks
      cannot bypass the boundary, and generic repositories retain their own
      canonical-source rules.

## Phase 3 — Trellis task router

- [x] Reconcile selected findings against active and archived tasks in each
      destination as tracked-accurate, tracked-stale, or untracked.
- [x] Route SD-owned work only to the verified `sd-ai-command-pack` upstream and
      SE-owned work only to the verified `se-ai-command-pack` upstream.
- [x] Reject SD/SE task seeds whose affected paths are not allowed templates;
      report generator, installer, manifest, documentation, test, and
      consumer-copy concerns as non-selectable packaging/tooling limitations.
- [x] Route other canonical skills to their enclosing repository's local
      Trellis task system.
- [x] Create at most one task per affected skill and review snapshot, with
      priority derived from the highest selected finding and a PRD-ready seed.
- [x] Use `--no-start` or the destination equivalent and verify the operator's
      active Trellis task is unchanged after cross-repository task creation.
- [x] Preview every destination and task before writing. Return paste-ready
      proposals for unavailable/wrong/dirty upstreams, missing Trellis, or
      unresolved ownership; never clone or bootstrap implicitly.
- [ ] Test duplicate task reuse, stale task reporting, drift split, same-repo
      overlap, cross-repo overlap, partial multi-destination success, and exact
      task paths outside the current checkout.

## Phase 4 — Skill and references

- [x] Create `templates/skills/se-review-skills/SKILL.md` using the required
      frontmatter and section order.
- [x] Keep core orchestration concise and move the detailed review rubric and
      report/apply schema into directly linked references.
- [x] Pin capability-ledger rules, brevity safety, evidence requirements,
      context/model profiles, prompt-injection handling, and sibling boundaries.
- [x] Pin delegation rules: independently bounded roles only, portable
      role-level model profiles, minimum task-local context, raw-artifact
      independent validation, bounded fan-out, inherited authority, no recursive
      spawning, and parent verification/deduplication.
- [x] Pin numbered family/skill grouping and individual, skill, family, and
      package apply selectors.
- [x] Pin review-only default, ownership/task reconciliation, snapshot
      staleness, destination preview, skill-sized checkpoints, partial failure,
      and no commit/publish behavior.
- [x] Add optional independent-review capability wording. If a platform overlay
      is implemented, test the exact Claude plugin route without putting brand
      names in canonical content.
- [x] Document that the first release recommends portable profiles and verified
      host overrides but does not add Gemini support to SE or duplicate complete
      skill bodies per target.

## Phase 5 — Registration and generated surfaces

- [x] Register `se-review-skills` in the Improve family and any shared-reference
      consumers.
- [x] Add analyzer/help documentation and release notes.
- [x] Bump the release version, run generation, and inspect the manifest fan-out.
- [x] Reconcile the parent roadmap from 49 to 50 children and update completion
      counts without changing existing child state.
- [x] Regenerate the repository map only after authored sources are stable.

## Phase 6 — Validation

- [x] Focused analyzer unit tests.
- [x] Focused skill convention and safety-pin tests.
- [x] Generator tests for registration, references, platform targets, drift, and
      any overlay merge/failure behavior.
- [ ] Template-boundary tests for SD and SE task/apply previews, including
      installed-copy drift, generated adapter mismatch, stale canonical mapping,
      and a finding that has no valid template remediation.
- [x] Target-matrix fixtures for SE shared-agent/Claude/Codex and representative
      SD shared, Claude, Codex, Gemini, and GitHub surfaces; verify unknown and
      unsupported capabilities fail closed.
- [ ] Forward-test no-delegation, useful parallel family review, role/model
      profile selection, authority preservation, recursive-fan-out refusal, and
      parent reconciliation of conflicting or duplicate subagent findings.
- [ ] Forward-test one strong script-extraction candidate, one instruction that
      must remain semantic, and one case where scripting costs more than it
      saves.
- [ ] Forward-test an SE skill, an SD skill, a third-party/plugin skill, one
      family, one generic repository, and a multi-repository selection in fresh
      contexts using raw artifacts rather than expected findings.
- [ ] Forward-test no-findings, self-review, false-overlap, unsafe-compression,
      unavailable-plugin, stale snapshot, ambiguous provenance, drifted copy,
      missing local Trellis, dirty upstream, task deduplication, and partial
      task/application scenarios.
- [x] Verify an isolated install contains the expected new skill files on every
      supported platform and no unsupported frontmatter keys.
- [x] Run `make check`, deterministic full check, install audit, knowledge-base
      freshness, release gate, and generated-drift checks.

## Phase 7 — Release and follow-up

- [ ] Ship the reviewer without bulk-editing the existing 42 skills.
- [ ] After merge, run the reviewer package-wide and save the numbered report.
- [ ] Convert accepted P0/P1 findings into focused remediation tasks or PRs by
      skill/family in their owning repositories; do not use one unreviewable
      package-wide or cross-repository content rewrite.
- [ ] Re-run the reviewer after remediation to measure resolved findings and
      capability-preserving size reduction.

## Risky files and rollback points

- `installer/registry.py` and `.github/scripts/generate-skill-surfaces.py` own
  cross-platform fan-out; checkpoint before any metadata-overlay change.
- Canonical skill frontmatter affects all platforms; reject unsupported keys
  before generation.
- Cross-repository task creation is additive but not atomic; persist and report
  each destination result before attempting the next.
- `manifest.json`, README catalogs, help catalog, and repository map are
  generated/release surfaces; regenerate them from sources rather than editing
  them independently.
- If optional provider integration destabilizes the portable release, remove
  the platform-specific route and retain the native independent-review path.
