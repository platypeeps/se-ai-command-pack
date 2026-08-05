# Argument vocabulary shared reference

## Goal

Ship the three-axis canonical argument vocabulary + reserved-name registry as a
shared reference, and define the single source-of-truth constant, so the A-006
migration and enforcement children have one citable contract. No enforcement and
no *argument-name* changes in this child.

Parent decision + rationale: `07-25-audit-skill-arg-vocabulary/design.md`.
Land this child first (see parent `implement.md` ordering).

## Requirements

- Author a shared reference documenting the three covered axes + the
  reserved-name registry:
  - verbosity `depth=brief|standard|deep` (ladder; subset values allowed);
  - primary artifact under action `input=`;
  - redaction `sensitivity=minimal|restricted|standard`;
  - reserved names (value not enforced): `sources=` (reference material to
    consult), `min_sources=` (count), `coverage=` (editorial coverage),
    `privacy=` (distribution/audience ceiling), `evidence=` (authorized
    supporting material), `format=` (output shape), `mode=`, `scope=`,
    `audience=`, owned names — each bound to its concept.
- Define the canonical-vocabulary constant in one place (module constant in
  `.github/scripts/generate-skill-surfaces.py` importable by the tests, or
  `installer/registry.py` if the test cannot import the generator).
- Ship via `_shared/references/` + `SHARED_REFERENCES`. Note: existing
  `test_shared_reference_consumers_cite_registered_reference`
  (`tests/test_skills.py:390`) requires every consumer body to cite the doc, so
  this child adds a one-line citation to each consumer body — an expected
  `templates/**` change, distinct from an argument-name change.
- Include the manifest version bump + `CHANGELOG.md` entry citing A-006.

## Acceptance Criteria

- [x] Shared reference states all three canonical axes + ladders and the full
      reserved-name registry (incl. `input=` vs `sources=` vs `evidence=`, and
      `sensitivity=` vs `privacy=`).
- [x] Canonical vocabulary defined as one importable constant (no duplication).
- [x] No argument name changes; required consumer citations present;
      `make check` green; version bump + changelog present.
