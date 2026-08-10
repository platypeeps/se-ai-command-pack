# Directory Structure

> How Python installer code and shipped skill content are organized.

---

## Overview

This is a Python CLI and content pack, not a web backend. Keep the root entry
point thin, put installer behavior in the `installer` package, declare shipped
content in the registry, and generate the manifest from canonical templates.

## Directory Layout

```text
install.py                  # CLI parsing and lifecycle orchestration
package.json                # private, dependency-free local review-gate wrapper
installer/                  # installer domain modules
  registry.py               # platforms, skill families, paths, and policy constants
  manifest.py               # manifest parsing and path-safety validation
  fileops.py                # planning, atomic writes, backups, and file status
  provenance.py             # receipts and installed-content provenance
  removal.py                # removal and retired-target cleanup
  management.py             # installed status and source-checkout update
templates/skills/           # canonical shipped skill sources
  <skill>/SKILL.md          # required portable skill instructions
  <skill>/references/*.md   # optional directly linked progressive disclosure
  <skill>/scripts/*.py      # optional deterministic, stdlib-first helpers
generated/skills/claude/    # generated Claude runtime-profile entrypoints
  <skill>/SKILL.md          # canonical body plus validated host frontmatter
generated/references/       # generated references fanned into consuming skills
  skill-catalog.md          # generated bundled catalog installed with se-help
manifest.json               # generated payload inventory and release version
README.md                   # generated family-grouped catalog inside markers
scripts/                    # generation and release-validation tools
tests/                      # unittest modules mirroring installer concerns
```

## Module Organization

- Keep `install.py` responsible for arguments, high-level sequencing, and
  terminal output. Reusable domain behavior belongs under `installer/`.
- Put stable pack declarations in `installer/registry.py`; `SKILLS` owns each
  skill's single family and `SKILL_NAMES` is derived for compatibility. Do not
  duplicate platform, skill, or family lists in scripts or tests.
- Treat canonical skill frontmatter and `installer/registry.py` as sources of
  truth. Run `make generate` to update `manifest.json`, the marker-bounded
  README catalog, and the bundled `se-help` catalog from one parsed model.
- Keep portable runtime profiles in `installer/registry.py`. Generate Claude
  entrypoints under `generated/skills/claude/`; never edit those derived files
  or copy their bodies by hand. Codex and shared-agent entrypoints continue to
  use canonical template bytes until their hosts expose equivalent validated
  execution controls.
- Keep skill-owned resources one level below the skill directory. Only
  `references/*.md` and `scripts/*.py` are shipped; nested resource trees and
  other file types fail generation. A bundled script must expose a bounded,
  deterministic contract and leave semantic judgment and mutation authority in
  `SKILL.md`.
- Keep root `package.json` limited to dependency-free wrappers for shared SD
  tooling. Python and Make remain the repository's implementation and quality
  interfaces; do not add a package lockfile.
- Add focused modules when a lifecycle concern has its own data flow. For
  example, `installer/management.py` owns status and update rather than adding
  Git subprocess details to `install.py`.
- Mirror meaningful module boundaries in tests: `installer/management.py` is
  covered by `tests/test_management.py`, while shared installer behavior is
  covered by `tests/test_install_core.py`.

## Naming Conventions

- Python modules and functions use `snake_case`; constants use `UPPER_CASE`.
- Immutable domain records use frozen dataclasses such as
  `installer.manifest.PackFile` and `installer.fileops.InstallResult`.
- Skill directories use the `se-` prefix and kebab-case, enforced by
  `installer.registry.validate_registry()`.
- Test modules use `test_<concern>.py`; test classes group behavior and test
  methods describe the observable contract.

## Examples

- `installer/manifest.py`: cohesive parsing, schema validation, and safe-path
  helpers.
- `installer/fileops.py`: filesystem policy isolated from CLI parsing.
- `installer/management.py` with `tests/test_management.py`: a feature module
  paired with focused lifecycle tests.

## Avoid

- Do not hand-edit generated `manifest.json` rows.
- Do not hand-edit generated README or `se-help` catalog rows, or move skills
  into family subdirectories; taxonomy is metadata and installed paths remain
  flat.
- Do not add hand-maintained platform-specific copies of skill content;
  platform adapters must be generated from the registry and canonical body.
- Do not write generator output under `templates/`. That tree is the one place
  skills are edited, so a generated file there reads as hand-editable and
  invites the edit the next `make generate` silently discards. Generated
  surfaces belong under `generated/`, which is why the bundled catalog is
  registered as a `GENERATED_REFERENCES` source rather than a
  `SHARED_REFERENCES` one. `write_generated_surfaces` enforces this at the
  writer: every target must carry a `generated` path component or be one of
  the two in-place surfaces (`manifest.json`, `README.md`). Components are read
  relative to `ROOT` for any target inside the checkout, so a directory above
  the repository named `templates` or `generated` cannot decide the verdict;
  only a target outside `ROOT` — the tests redirecting output into a temporary
  tree — falls back to the whole path. Enforcing it there
  rather than by scanning for the do-not-edit marker is what makes it hold for
  non-Markdown output — the marker is an HTML comment and cannot appear in a
  generated `.json` or `.toml` at all.
- Do not hide semantic decisions, approvals, or unbounded external actions in a
  bundled script merely to shorten the skill text.
- Do not bury reusable filesystem, validation, or subprocess logic in the CLI
  entry point.
