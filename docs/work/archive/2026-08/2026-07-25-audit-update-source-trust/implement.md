# Harden install.py update source trust — Implementation Plan

## Execution Order

1. **`installer/management.py` — trust gate.**
   - Add `import os` and extend the registry import to include `ROOT`.
   - Change `_source_checkout(root: Path)` →
     `_source_checkout(root: Path, *, confirm_source: bool)`.
   - After the existing name/existence checks and before `return source_root`,
     add, in order:
     - git-repo + ownership gate (defense-in-depth): let `git_entry =
       source_root / ".git"`. Refuse via `SystemExit` if `git_entry` does not
       exist (accept both a `.git` directory and a `.git` file so git worktrees
       are not falsely refused); and, when `hasattr(os, "geteuid")`, if
       **either** `source_root.stat().st_uid != os.geteuid()` **or**
       `git_entry.stat().st_uid != os.geteuid()` (use `stat`, following
       symlinks, so a symlinked `.git` is judged by its target).
     - relocated-checkout gate: if `source_root != ROOT`:
       - if `confirm_source`: proceed;
       - elif `sys.stdin.isatty()`: prompt `y/N`, refuse on non-affirmative;
       - else: `SystemExit` naming `--confirm-source`, recorded, and running
         paths.
     - Ordering note: the git+ownership gate runs first, but it must not become
       the *only* thing that stops a foreign path. A foreign checkout that is a
       current-user-owned git repo passes this gate and is then stopped by the
       relocated-checkout gate — the test suite pins exactly that path so the
       principal control cannot silently regress.
   - Thread `confirm_source` into `update_pack(...)` signature and pass it to
     `_source_checkout(root, confirm_source=confirm_source)`. The dirty-checkout
     `_run_git` and every `subprocess.run` must remain strictly after
     `_source_checkout` returns (already true) so refusals never touch git/exec.
2. **`install.py` — CLI surface.**
   - Add `--confirm-source` (`action="store_true"`) to `parse_args`, with help
     text describing the relocated-checkout confirmation.
   - In the `update` dispatch, add `confirm_source=args.confirm_source` to the
     `update_pack(...)` call.
3. **Docs.** Document the confirmation path in the operator-facing update docs
   (grep for the existing `update` command description in `README.md` and
   `docs/SE_AI_COMMAND_PACK.md`; extend the one that documents `install.py
   update`). State: default same-checkout updates need nothing; a relocated
   checkout needs `--confirm-source` (or an interactive yes); the recorded
   source must be a git repository (current-user-owned on POSIX platforms).
4. **Release metadata.** Bump `manifest.json` version (patch) and add a dated
   `CHANGELOG.md` entry under the new version describing the update source-trust
   hardening and the new `--confirm-source` flag (installer = consumer
   contract).
5. **Tests** (`tests/test_management.py`): see Validation Plan.

## Validation Plan

- New tests (each patches `installer.management._run_git` **and**
  `installer.management.subprocess.run` with side effects that fail if called,
  so every refusal asserts zero git and zero exec). Helper: build a
  "foreign-but-valid" checkout = temp dir containing `install.py` +
  name-matching `manifest.json` + a `.git` dir, owned by the runner, whose path
  != `ROOT`; point `provenance.json.sourceRoot` at it.
  - **PRINCIPAL CONTROL** —
    `test_update_refuses_foreign_owned_git_checkout_without_confirmation`: use
    the foreign-but-valid checkout above (passes the git+ownership gate), non-tty
    stdin, no `--confirm-source`; assert `SystemExit` mentioning
    `--confirm-source` and **zero** `_run_git`/`subprocess.run` calls. This is
    the test that fails if the relocated-checkout gate is absent or broken —
    it must not be able to pass at the `.git` check.
  - `test_update_refuses_non_git_foreign_source`: foreign dir with no `.git`;
    assert refusal, zero git/exec (git-repo gate).
  - `test_update_refuses_foreign_owned_source`: on POSIX, monkeypatch/stat so
    `source_root` (or its `.git`) reports a different `st_uid`; assert refusal,
    zero git/exec (ownership gate). Skip where `os.geteuid` is absent.
  - `test_update_same_checkout_proceeds`: default install (sourceRoot == ROOT ==
    PACK_ROOT, a real user-owned git repo); assert
    `update_pack(..., confirm_source=False)` runs the normal git+exec sequence
    (AC2 — normal path unaffected).
  - `test_update_relocated_source_confirmed_with_flag`: foreign-but-valid
    checkout; `confirm_source=True`; assert it proceeds into the git+exec
    sequence.
  - `test_update_relocated_source_interactive_yes_proceeds` /
    `_interactive_no_refuses`: patch `sys.stdin.isatty` → True and
    `builtins.input` → `"y"` / `"n"`; assert proceed vs refuse (zero git/exec on
    refuse).
  - `test_update_accepts_git_file_worktree`: foreign-but-valid checkout whose
    `.git` is a *file* (worktree form), confirmed; assert the git-repo gate
    accepts it.
  - `test_update_skips_ownership_check_without_geteuid`: patch
    `hasattr(os,"geteuid")`/delete attr; assert the ownership branch is skipped
    while git-repo + confirmation gates still apply.
  - CLI: `test_update_cli_forwards_confirm_source` (extend the existing
    `test_cli_forwards_platform_selection` pattern): `main(["update", "--root",
    ..., "--confirm-source"])` forwards `confirm_source=True` to the mocked
    `update_pack`; and a parse test that `--confirm-source` defaults False.
  - Update existing `update_pack(...)` call sites in `tests/test_management.py`
    to pass `confirm_source=...` (or rely on the same-checkout default) so the
    new keyword-only parameter does not `TypeError` them.
- Commands:
  - Focused: `python -m unittest tests.test_management -v`.
  - Broad: `make check` (generator `--check`, release payload gate, full suite,
    coverage). Must exit 0.

## Documentation And Spec Updates

- Operator guide / README `update` section: relocated-source confirmation path;
  ownership requirement worded as POSIX-scoped ("current-user-owned git
  repository on POSIX platforms").
- `tests/test_installer_docs.py`: if it pins the `update` command's
  contract-bearing README/operator-guide section, update the expected text.
- `.trellis/spec/backend/quality-guidelines.md`, "Pack Lifecycle CLI Changes":
  update the `update` contract bullet (source-trust gate + `--confirm-source`),
  add error-matrix rows (foreign/unconfirmed source → refuse before git/exec;
  non-git or foreign-owned source → refuse), and extend Tests-Required to name
  the source-trust refusal/confirmation cases. This is a required spec update,
  not optional — the scenario already governs this surface.
- `.trellis/audit/ledger.md`: mark A-017 addressed per the existing ledger
  convention when the work lands (verify the convention before editing).
- `CHANGELOG.md`: dated entry for the bumped version.

## Review Notes

- Reviewer-sensitive: the refusal must happen strictly before any `git` or
  `subprocess.run`; every refusal test asserts zero calls to both.
- The principal-control test uses a *current-user-owned git* foreign checkout so
  refusal is forced through the confirmation gate, not the `.git` gate.
- Ownership check covers both `source_root` and its `.git` entry; guarded by
  `hasattr(os, "geteuid")`; the git-repo requirement and confirmation gate apply
  everywhere. Ownership claim is POSIX-scoped in docs/PRD wording.
- Confirm `.git`-as-file (worktree) is accepted (existence check, not dir-only).
- TOCTOU residual is accepted and documented; fd-hardening is a follow-up task.
- Keep messages in the existing `error: ...` style used by `_source_checkout`.

## Rollback Points

- Each numbered step is an isolated commit-sized change; reverting
  `installer/management.py` + `install.py` restores prior behavior. Docs and
  changelog/version revert independently. No data migration, fully reversible.

## Follow-Ups (outside this PR)

- **TOCTOU hardening** (accepted residual in design): fd/`O_NOFOLLOW`-based
  check-then-use so `git`/exec operate on the exact validated directory. Needs a
  larger rework because `git -C` and `subprocess` cannot take a dir descriptor;
  file as a new task.
- Optional deeper trust: verify the checkout's git remote/origin or sign the
  provenance receipt (new task if desired).
- Consider applying an analogous recorded-path trust check to `pack_status`'s
  checkout-version read (read-only today, lower risk).
