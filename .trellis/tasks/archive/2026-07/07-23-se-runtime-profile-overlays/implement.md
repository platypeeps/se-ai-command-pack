# Implementation plan: per-target runtime profile overlays

## 1. Add and validate registry declarations

- Add portable runtime value allowlists and a frozen `RuntimeProfile` record to
  `installer/registry.py`.
- Declare named reviewed profiles and grouped skill membership.
- Derive `SKILL_RUNTIME_PROFILES` with explicit duplicate, missing, and unknown
  membership validation.
- Add focused registry tests for exact coverage and invalid declarations.

## 2. Add deterministic platform rendering

- Extend `.github/scripts/generate-skill-surfaces.py` with a Claude capability
  map, portable-to-Claude model translation, and deterministic YAML rendering.
- Preserve the canonical body exactly and keep canonical validation limited to
  `name`/`description`.
- Represent `fresh-session` as a deliberate unsupported context translation,
  not `context: fork`.
- Reject unsupported keys and unknown model/effort values.
- Add generator tests for each translation branch and canonical preservation.

## 3. Generate and inventory Claude payloads

- Render all `generated/skills/claude/<skill>/SKILL.md` files in memory.
- Extend check mode to report missing, changed, and unexpected generated files.
- Include generated payload writes in coordinated rollback.
- Point only Claude `SKILL.md` manifest rows at generated sources.
- Run `make generate` and inspect the generated/manifest diff.

## 4. Verify installer behavior

- Update installer tests to derive expected installed bytes from each manifest
  source instead of assuming every platform uses the canonical template.
- Assert a representative forked Claude skill, inline Claude skill,
  fresh-session profile, Codex skill, and shared-agent skill.
- Retain refresh idempotence, plan-before-apply conflict, force, and backup
  behavior.

## 5. Update release and contracts

- Bump the manifest patch version and add a matching `CHANGELOG.md` entry.
- Document the generated overlay ownership and validation rules in the backend
  specs.
- Update `se-review-skills` runtime-routing guidance to distinguish applied
  Claude overlays from advisory Codex/shared-agent recommendations.
- Regenerate after all canonical/reference changes.

## 6. Complete verification and lifecycle

- Run focused registry, generator, and installer unit tests.
- Run `make generate` twice and confirm the second run is diff-free.
- Run `make check` and `git diff --check`.
- Review the final diff for unrelated or hand-edited generated content.
- Record implementation context, finish the Trellis task, and hand the change to
  the normal PR/housekeeping workflow only when separately requested.
