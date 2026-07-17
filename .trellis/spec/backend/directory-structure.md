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
installer/                  # installer domain modules
  registry.py               # platforms, skills, paths, and policy constants
  manifest.py               # manifest parsing and path-safety validation
  fileops.py                # planning, atomic writes, backups, and file status
  provenance.py             # receipts and installed-content provenance
  removal.py                # removal and retired-target cleanup
  management.py             # installed status and source-checkout update
templates/skills/           # canonical shipped skill sources
manifest.json               # generated payload inventory and release version
scripts/                    # generation and release-validation tools
tests/                      # unittest modules mirroring installer concerns
```

## Module Organization

- Keep `install.py` responsible for arguments, high-level sequencing, and
  terminal output. Reusable domain behavior belongs under `installer/`.
- Put stable pack declarations in `installer/registry.py`; do not duplicate
  platform or skill lists in scripts or tests.
- Treat `templates/skills/` and `installer/registry.py` as sources of truth.
  Run `make generate` to update `manifest.json`.
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
- Do not add platform-specific copies of skill content; generate fan-out from
  the registry and canonical templates.
- Do not bury reusable filesystem, validation, or subprocess logic in the CLI
  entry point.
