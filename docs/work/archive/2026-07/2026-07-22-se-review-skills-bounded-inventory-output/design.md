# Design: bounded se-review-skills inventory output

## Boundaries

The existing `build_inventory()` API remains the single producer of the full
schema-version-3 payload and `snapshotId`. The CLI gains an optional bounded
transport mode; inventory discovery, ownership, deduplication, hashing, and
semantic interpretation do not change.

Canonical implementation remains limited to:

- `templates/skills/se-review-skills/scripts/skill_review.py`
- `templates/skills/se-review-skills/SKILL.md`
- `tests/test_skill_review.py`

Generated manifest targets, version metadata, changelog, and repository maps
change only through the existing release/generation workflow.

## CLI Contract

```text
skill_review.py inventory ... [--pretty]
skill_review.py inventory ... --output PATH --output-root PATH [--pretty]
```

- Omitting `--output` preserves legacy full-payload stdout byte behavior.
- `--output` selects bounded mode and requires `--output-root`.
- `--output-root` without `--output` is invalid.
- A relative output path resolves below `--output-root`; an absolute output
  path must still resolve below it.
- `--pretty` formats the selected stdout object. The complete artifact remains
  compact canonical JSON so formatting cannot affect snapshot identity.

## Data Flow

1. Parse and validate ordinary inventory selectors.
2. Build the full inventory exactly once with `build_inventory()`.
3. In legacy mode, emit the full payload as today.
4. In bounded mode, derive forbidden mutation roots from the payload's
   repositories and installed roots, then validate the caller-supplied output
   root and destination.
5. Serialize the full payload as compact, sorted UTF-8 JSON with one trailing
   newline.
6. Atomically replace or create the destination.
7. Emit a bounded envelope to stdout.

## Bounded Envelope

```json
{
  "artifactWritten": true,
  "coverageLimits": [],
  "error": null,
  "installedCopies": 0,
  "inventoryPath": "/bounded/path/inventory.json",
  "inventorySchemaVersion": 3,
  "selectedSkills": 1,
  "snapshotId": "...",
  "status": "success",
  "transportSchemaVersion": 1
}
```

Failure uses the same keys with `status="error"`,
`artifactWritten=false`, and a bounded actionable `error`. Fields that cannot
exist because inventory construction failed are `null`; an unsafe destination
is never presented as a validated artifact locator.

The envelope never contains skill records, installation records, repository
records, or candidate-signal details.

## Destination Validation

- The output root must already exist, be a real directory, and be neither the
  filesystem root nor the user's home directory.
- No component of the supplied root path, destination parent chain, or
  destination may be a symlink.
- The destination must remain lexically and canonically below the output root;
  `..` escapes are rejected before resolution.
- The destination must be outside every reviewed repository and installed root
  reported by the inventory.
- A destination directory or non-regular file is rejected.
- Existing content is replaceable only when it parses as a complete analyzer
  inventory and its `snapshotId` matches the canonical hash of the remaining
  payload. Arbitrary existing content is preserved.
- Validation records the existing destination fingerprint. The atomic writer
  rechecks absence or that fingerprint immediately before replacement so a
  changed path fails closed.

## Atomic Write Contract

- Create a private temporary file in the destination directory and reinforce
  mode `0600` with descriptor chmod when the platform provides it.
- Write UTF-8 JSON, flush, and `fsync` the file.
- Revalidate the destination state.
- Replace with `os.replace()` only after all checks pass.
- Remove the temporary file in `finally` on every failure.
- Return nonzero and emit an error envelope when validation or writing fails;
  the old artifact remains intact or the new artifact remains absent.

## Compatibility And Release

- Python 3.9 remains supported; use only the standard library.
- Existing `build_inventory()` callers and legacy/pretty CLI output remain
  compatible.
- The payload schema and snapshot calculation remain unchanged.
- Changing the shipped analyzer and canonical skill requires a manifest version
  bump, dated changelog entry, `make generate`, and generated-target parity.

## Rollback

The feature is isolated behind optional CLI arguments. Reverting the analyzer,
skill documentation, tests, version/changelog entry, and regenerated manifest
fully restores the prior behavior; no migration or persisted default state
exists.
