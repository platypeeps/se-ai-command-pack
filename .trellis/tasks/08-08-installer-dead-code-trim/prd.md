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
   (`installer/registry.py:606`), making two membership tests and one
   iterable expansion dead by construction: `fileops.py:300`,
   `fileops.py:343`, `provenance.py:91`.
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

## Dispositions (recorded 2026-08-09)

Citations below re-verified 2026-08-09; drift from the 2026-08-08 filing:
`preflight_checks` now at `install.py:175-183` with its call at `:441` and the
prior `require_install_root` at `:422`; the Makefile `--user` use is at
`Makefile:24`.

1. **`--user` — keep, as an explicit-intent flag.** Written reason: the flag
   is a documented public contract (fourteen README occurrences, the Makefile
   dogfood target) with one live, tested behaviour — argparse mutual
   exclusion with `--root` (`tests/test_install.py:397`,
   `test_root_and_user_are_exclusive`). Its help text already states it is
   the default ("Install into the current user's home directory (the
   default)."), satisfying this task's keep-condition verbatim. Deleting it
   would break every documented invocation to remove nothing but a guard.
   No flags change; the PRD's "stated explicitly which flags changed"
   record is: none.
2. **`preflight_checks` — delete.** The seam discards `manifest_data` and
   its only action, `require_install_root(root)`, already runs for every
   command at `install.py:422` before the seam's call site at `:441`. No
   concrete future backend consumer is named anywhere. Remove the function,
   its call, its `__all__` entry (`install.py:50`), and the README extension
   bullet that names it as "the single seam where a future backend
   prerequisite would land" (`README.md:314-315`) — the seam's
   documentation must not outlive the seam.
3. **`FORCE_PRESERVED_TARGETS` — delete, with its machinery.** Remove the
   empty frozenset (`installer/registry.py:606`), the two dead membership
   tests and one empty expansion (`fileops.py:300`, `:343` reduce to the
   `IF_NOT_EXISTS` check; `provenance.py:91` drops the empty splat), both imports (`fileops.py:19`,
   `provenance.py:24`), and the `__all__` entry (`registry.py:703`). The
   `never_vouched_targets` docstring sentence explaining force-preserved
   targets (`provenance.py:86-88`) is rewritten to cover only the remaining
   generated-file entries.
4. **`KNOWN_SCOPES` — keep as-is.** Live validation (`manifest.py:116`)
   feeding the "known scopes: ..." diagnostic at `manifest.py:119`. The
   diagnostic could be reproduced with `USER_SCOPE` directly (already
   imported at `manifest.py:15`), so the keep is not forced; it is chosen
   for table-driven consistency with `KNOWN_MANIFEST_KINDS` one line above
   (`manifest.py:114`) and README's documented `project`-scope extension
   path. A one-line comment at the definition records that single-element
   is intentional until a second scope exists.
5. **`ENV_PREFIX` — delete.** No executable reader exists (definition
   `registry.py:14` and `__all__` entry `:700` are the only code
   references; remaining mentions are task records). The
   `SE_AI_COMMAND_PACK_*` namespace reservation in
   `docs/SE_AI_COMMAND_PACK.md:1093-1094` is forward-looking prose that
   reads no constant and stays as-is.

## Acceptance Criteria

- [ ] Each of the five items has a disposition; deletions verified by
      repo-wide grep for the removed names returning only historical or
      task-record references (CHANGELOG, archived tasks, and this task's
      own artifacts) — no executable or generated-surface reader remains.
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

- Sourced from the 2026-08-08 deep review (code-quality lane); the Problem
  section's citations were grep-verified that day, and the Dispositions
  section re-verified them 2026-08-09 (drift noted there).
- The review's headline for repo-own code was positive — consistent
  `SystemExit` error idiom, argparse throughout, zero bare excepts. This task
  is a trim, not a cleanup of a problem area.
- Lightweight; PRD-only.
