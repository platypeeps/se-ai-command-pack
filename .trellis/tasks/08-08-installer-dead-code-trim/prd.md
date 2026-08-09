# Installer dead weight: no-op flags, empty seams, dead exports

## Goal

Delete the repo-own installer code that demonstrably does nothing, so the
next reader doesn't have to re-derive that it does nothing. Each item is
delete-or-justify; the justification, where chosen, must be written down.

## Problem

All verified 2026-08-08 in repo-own installer code:

1. **`--user` is a no-op flag.** Declared at `install.py:88`; `args.user` is
   read nowhere (repo-wide grep: zero hits). `resolve_install_root()` branches
   only on `args.root`. Its sole effect is argparse mutual exclusion with
   `--root`. `Makefile:21` passes it, reinforcing the illusion it selects
   behaviour.
2. **`preflight_checks()` is a self-declared empty seam.**
   `install.py:167-174` takes `manifest_data` and discards it
   (`del manifest_data` at :173); its one real action,
   `require_install_root(root)`, was already executed at `install.py:331`
   before the seam is called, making the call redundant. The docstring says
   it is "the seam for future backends".
3. **`FORCE_PRESERVED_TARGETS` is a permanently empty frozenset**
   (`installer/registry.py:606`), making three membership tests dead by
   construction: `fileops.py:300`, `fileops.py:343`, `provenance.py:91`.
4. **`KNOWN_SCOPES = frozenset({USER_SCOPE})`** (`registry.py:602`) is **live
   validation, not dead code**: `validate_manifest` uses it at
   `manifest.py:116` to reject any manifest row with an unknown scope. What
   is questionable is the shape — a single-element set implying a multi-scope
   feature that does not exist. The choice is keep as-is or replace with an
   equally explicit `scope == USER_SCOPE` check; deleting the validation is
   not an option.
5. **`ENV_PREFIX`** (`registry.py:14`) is exported and read by nothing; a
   task doc already records that no env-var mechanism exists.

## Requirements

- For each of the five items: delete it, or keep it with a written reason in
  code or spec. Speculative "future backend" seams count as delete candidates
  unless a concrete consumer is named. Item 4's floor is stated in the item:
  scope validation itself must survive in some explicit form.
- If `--user` is removed: preserve the CLI contract deliberately — decide
  whether bare `python3 install.py` keeps installing to the user scope, and
  update `Makefile:21`, README install instructions, and any test asserting
  the flag. If it is kept as an explicit-intent flag, make the help text say
  it is the default rather than implying an alternative.
- If `FORCE_PRESERVED_TARGETS` is removed, simplify its dead call sites in
  the same change; do not leave the machinery minus the data.
- Items with existing owners are excluded (see Out of scope): the
  `se-ai-command-pack-skill-review.py` forwarder belongs to
  `07-25-audit-repo-tooling-ownership` [A-026], and `.opencode/package.json`
  to `07-25-audit-dependency-hygiene` [A-032] — the latter is additionally
  Trellis template-hashed, so it is not repo-own to delete here.
- No behaviour change to what gets installed where; this is deletion of
  never-taken paths only. `make check` (test, lint, release-check) is the
  gate.

## Acceptance Criteria

- [ ] Each of the five items has a disposition; deletions verified by
      repo-wide grep for the removed names returning only historical
      references (CHANGELOG, archived tasks).
- [ ] If item 4 changed shape: a manifest row with an unknown scope is still
      rejected, demonstrated by the existing tests (or an added one), not by
      inspection.
- [ ] `make check` passes after the trim; coverage does not drop below the
      80% floor (deleting dead branches should raise it, not lower it).
- [ ] `python3 install.py --help` and a `--dry-run` install behave
      identically to before except for removed/reworded flags; stated
      explicitly in the task record which flags changed.
- [ ] No file owned by another task's scope was touched: the forwarder,
      `.opencode/package.json`, and vendored `scripts/sd-ai-command-pack-*`
      are absent from the diff.

## Out of scope

- Vendored `scripts/sd-ai-command-pack-*` dead code (upstream; see
  `08-07-vendored-artifact-upstream-route`) — including the four-way
  `_bounded()` contract collision found in the same review.
- `scripts/se-ai-command-pack-skill-review.py` (owned by
  `07-25-audit-repo-tooling-ownership` [A-026]) and `.opencode/package.json`
  (owned by `07-25-audit-dependency-hygiene` [A-032]; Trellis
  template-hashed). Both were in this task's first filing; cut on
  adversarial review because active owners already exist.
- Registry data-table refactors (hand-maintained `SHARED_REFERENCES` is
  ledger A-007's subject).
- Any new capability (multi-scope install, env-var config); this task only
  removes the pretense of them.

## Notes

- Sourced from the 2026-08-08 deep review (code-quality lane); every line
  citation above was re-verified by grep the same day.
- The review's headline for repo-own code was positive — consistent
  `SystemExit` error idiom, argparse throughout, zero bare excepts. This task
  is a trim, not a cleanup of a problem area.
- Lightweight; PRD-only.
