# Preserve unverified claims in evidence audits

## Goal

Review snapshot 726d2d57c275b1d600940fbd523528081a43a898bfdaac2cdad34dec06fba0ae; finding 5.1.2. Preserve unsupported load-bearing claims as unverified in claim and evidence-gap ledgers while excluding them from conclusions. Affected templates: templates/skills/_shared/references/verification-protocol.md and templates/skills/se-fact-check/SKILL.md; focused tests under tests/test_skills.py. Coordinate shared-reference edits with the tracked-stale se-shared-evidence-claim-sensitive task.

## Requirements

- Keep every audited claim in the claim ledger, including unsupported
  load-bearing claims.
- Mark an unsupported load-bearing claim `unverified`, preserve its evidence
  gap, and prevent it from supporting a conclusion.
- Preserve the existing two-source corroboration rule, source-quality rules,
  conflict handling, and honest failure behavior.
- Reconcile wording in the shared verification protocol with the exact-one-
  verdict and complete-ledger contracts in `se-fact-check`.
- Coordinate changes to the shared verification protocol with the active
  `07-22-se-shared-evidence-claim-sensitive` task before implementation; do not
  let the two tasks make conflicting edits.
- Change only canonical templates under `templates/skills/**`, then regenerate
  supported targets through the repository's normal sync path.

## Acceptance Criteria

- [ ] An unverifiable load-bearing claim remains visible as `unverified` in the
      claim and evidence-gap ledgers.
- [ ] That claim cannot support the summary conclusion or recommendation.
- [ ] Contextual and verified load-bearing claims retain their current handling.
- [ ] Shared-protocol wording and `se-fact-check` wording cannot be interpreted
      as permitting silent claim removal.
- [ ] Focused skill-contract tests cover the unsupported load-bearing case.
- [ ] Generated target checks and the repository quality gate pass.

## Notes

- Routing state: `untracked` for current finding `5.1.2`; the overlapping shared
  file is already named by a `tracked-stale` task from snapshot
  `4e4619ac8aab4220a5390e039393b8f58a5af36f34e44efe30be85ac498cd968`.
- Primary risk: preserving a claim in the ledger must not accidentally elevate
  it into a conclusion.
