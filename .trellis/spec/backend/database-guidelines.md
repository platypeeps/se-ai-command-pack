# Database Guidelines

> Database guidance for this project.

---

## Overview

This project has no database, ORM, migrations, tables, transactions, or query
layer. Persistent state is a small set of UTF-8 JSON and text receipts under
`.se-ai-command-pack/` in the selected install root.

Do not introduce a database abstraction for pack state. The filesystem receipt
contract is intentionally inspectable and portable across supported platforms.

## State Access Patterns

- Read installed `manifest.json`, `provenance.json`, and
  `installed-targets.txt` through the focused helpers in
  `installer/provenance.py` and `installer/management.py`.
- Treat malformed, missing, symlinked, or unreadable receipts conservatively.
  Status helpers return unavailable/not-installed state; mutating operations
  fail before writing when required provenance cannot be trusted.
- Write generated receipts through the same plan/apply and atomic-file paths as
  other installed content. `installer/fileops.atomic_write_bytes()` writes a
  temporary file, fsyncs it, sets its mode, and replaces the destination.
- Store relative installed targets, content hashes, pack identity, version, and
  source checkout data in the existing receipt formats. Schema changes require
  compatibility tests for prior installations.

## Schema and Migration Policy

There is no migration framework. Receipt evolution is handled in installer
code that can read installations produced by earlier pack releases. The
manifest has an integer `schemaVersion`; `installer/manifest.py` rejects schema
versions newer than the installer supports.

When changing persistent fields:

1. Keep old receipts readable or fail with an actionable error.
2. Add fixtures/tests for missing, malformed, and prior-shape data.
3. Update install, status, update, removal, and provenance behavior together.
4. Bump the release version when the shipped payload or manifest changes.

## Examples

- `installer/management._read_json_object()` accepts only regular JSON-object
  receipt files and returns `None` for untrusted input.
- `installer/provenance.py` records and reads the installed-target receipt and
  content provenance used to vouch safe updates and removals.
- `installer/manifest.load_manifest()` validates the generated payload schema
  before any installation plan is applied.

## Common Mistakes

- Treating arbitrary receipt values as trusted paths without resolving and
  validating them.
- Writing receipt files directly and non-atomically.
- Adding a new receipt field without tests for installations where it is absent.
- Describing this project as having database conventions when it has none.
