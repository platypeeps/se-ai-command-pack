# Harden install.py update source trust — Design

## Overview

`install.py update` re-derives the pack checkout from the `sourceRoot` string in
the plain-JSON provenance receipt (`installer/provenance.py` writes
`"sourceRoot": str(ROOT)`), then runs `git` against that path and executes
`<sourceRoot>/install.py` in a fresh process
(`installer/management.py:_source_checkout` → `update_pack`). The current gate
(`installer/management.py:98-106`) only checks that `install.py` and a
name-matching `manifest.json` exist under the recorded path. An attacker who can
write one file — the plain-JSON `provenance.json` — can point `sourceRoot` at a
checkout they control (trivially satisfying the name/file checks) and turn the
next `install.py update` into arbitrary code execution. This closes that
write-one-file-to-code-execution path (audit A-017, P2/S).

## Proposal

Add a trust gate inside `_source_checkout`, the single chokepoint that resolves
`sourceRoot` before any `git` invocation or `install.py` execution in
`update_pack`. After the existing existence/name validation and before
returning the path:

1. **Same-checkout trust.** Compute `running = installer.registry.ROOT`
   (already resolved). If the resolved `source_root` equals `running`, the
   update targets the checkout install.py is itself running from — trusted, no
   confirmation needed. This is the normal workflow and the case tests exercise.

2. **Relocated-checkout confirmation.** If `source_root != running`, require
   explicit operator confirmation:
   - `--confirm-source` flag present → authorized, proceed.
   - else if `sys.stdin.isatty()` → interactive `y/N` prompt; anything but an
     affirmative answer refuses.
   - else (non-interactive, no flag) → clean `SystemExit` refusal naming
     `--confirm-source` and the recorded vs running paths. No `git`, no exec.

3. **Git-repository + ownership gate (defense-in-depth).** Require the resolved
   `source_root` to contain a `.git` entry and, where the platform exposes
   `os.geteuid`, require that **both** `source_root` **and** its `.git` entry are
   owned by the current effective user
   (`p.stat().st_uid == os.geteuid()` for each; `stat`, not `lstat`, so a
   symlinked `.git` is judged by its resolved target). A recorded path that is
   not a git repo, or whose checkout or git directory is owned by another user,
   is refused before any `git`/exec. `update` fundamentally needs git (it runs
   `git pull`), so a non-git path was already unusable; this converts a late,
   noisy failure into an early, explicit refusal and blocks the
   foreign-owned-repo variant of the attack.

   **Control ordering and primacy.** The trust guarantee rests on the
   same-checkout / `--confirm-source` gate (control 1–2): the operator either
   updates the checkout they are already running (and therefore already trust),
   or explicitly confirms a relocated one. The git+ownership gate is
   supplementary — it narrows *which* foreign paths a confirmation can even
   apply to (a current-user-owned git repo), and it independently blocks
   other-user-planted foreign paths. Because it is supplementary, the two gates
   are evaluated so that a foreign, current-user-owned **git** checkout still
   reaches — and is stopped by — the confirmation gate; refusal must not depend
   on the foreign path happening to lack `.git`.

The gate is threaded as a keyword-only `confirm_source: bool` through
`update_pack(...)` into `_source_checkout(...)`; `install.py`'s `update` dispatch
passes `confirm_source=args.confirm_source`. A new `--confirm-source` store_true
flag is added to the shared argument parser.

## Boundaries And Non-Goals

- Only the `update` command's source-trust decision changes. `install`,
  `refresh`, `remove`, and `status` are untouched.
- No change to how provenance is *written* (`installer/provenance.py` still
  records `str(ROOT)`); this hardens how it is *consumed*.
- Not signing or checksumming the checkout, not verifying remote origin URLs —
  out of scope for A-017; can be a follow-up.
- Windows/no-`geteuid` platforms keep the git-repo requirement and the
  same-checkout / `--confirm-source` gate but skip the uid-ownership check. The
  ownership guarantee is therefore scoped to POSIX platforms; docs and the PRD
  wording are reconciled to say "current-user-owned git repository **on POSIX
  platforms**" so the claim does not overstate the no-`geteuid` case.

## Affected Files

- `installer/management.py` — trust gate in `_source_checkout`; thread
  `confirm_source` through `_source_checkout` and `update_pack`; import `os` and
  `ROOT`.
- `install.py` — add `--confirm-source` flag; pass `confirm_source` in the
  `update` dispatch.
- `README.md` and/or `docs/SE_AI_COMMAND_PACK.md` — document the relocated-source
  confirmation path (POSIX-scoped ownership wording).
- `.trellis/spec/backend/quality-guidelines.md` — the "Pack Lifecycle CLI
  Changes" scenario currently states *"`update` trusts only the
  provenance-recorded `sourceRoot`, requires the expected pack manifest…"* and
  carries an error matrix + Tests-Required list. Update its contract text,
  error-matrix rows, and required-tests to reflect the source-trust gate and
  `--confirm-source`.
- `tests/test_installer_docs.py` — documentation contract test; update if it
  pins the `update` command's contract-bearing README/operator-guide section.
- `CHANGELOG.md` + `manifest.json` version bump (installer is consumer contract).
- `tests/test_management.py` — new refusal/confirmation/same-checkout/ownership
  tests (see implement.md).

## Data And Command Contracts

- `provenance.json.sourceRoot` (string): recorded checkout path. Now trusted
  only when it resolves to `ROOT`, or the operator confirms a different path,
  and it is a git repository (current-user-owned on POSIX platforms).
- New CLI surface: `install.py update [... existing flags ...] [--confirm-source]`.
  `--confirm-source` authorizes updating from a recorded checkout that differs
  from the running checkout.
- Refusal contract: all new rejections raise `SystemExit` with an `error:`
  message and perform no `git` call and no subprocess exec.

## Risks And Edge Cases

- **Legitimate relocated checkout** (user moved/renamed the clone, runs update
  from a different copy): preserved via `--confirm-source` or interactive
  confirmation; documented. Verified by a confirmation-path test.
- **Symlinked provenance**: already returns `None` (untrusted) via
  `_read_json_object`; unchanged.
- **`.git` as a file (worktrees)**: accept `.git` existing as file *or* dir so
  git worktrees are not falsely refused; require existence, not dir-only.
- **Non-interactive automation** relying on a relocated source without the flag
  will now refuse — intended; the flag is the documented seam.
- **uid check portability**: guarded by `hasattr(os, "geteuid")`; absent →
  ownership check skipped, git-repo check and the same-checkout / confirmation
  gate retained. Ownership claim is POSIX-scoped in docs and PRD wording (see
  Boundaries) so no contradiction remains.
- **TOCTOU (accepted residual, follow-up).** The gate validates `source_root`
  and returns a pathname; `update_pack` then runs `git` and executes
  `install.py` from that path later, without re-validation, and an interactive
  prompt widens the window. A same-user attacker who could swap the checkout
  already holds the victim's privileges, so that case is outside the threat
  model. The cross-user swap requires a user-writable ancestor of a
  now-user-owned checkout; the ownership check on `source_root` narrows but does
  not fully close it. This is a strict improvement over the status quo (no trust
  check at all) and is not a blocker. Full fd/`O_NOFOLLOW`-based
  check-then-use hardening is recorded as an explicit follow-up rather than
  attempted here, because `git -C <path>` and `subprocess` cannot consume a
  directory descriptor without a larger rework.

## Validation

- `python -m unittest tests.test_management -v` — new + existing update tests.
- `make check` (generator `--check`, release payload gate, full suite) green.
- Manual/asserted: a crafted foreign `sourceRoot` — including the principal
  case of a current-user-owned git checkout that differs from `ROOT` — refuses
  with zero `_run_git` and zero `subprocess.run` calls (mock-asserted), so the
  confirmation gate, not merely the `.git` gate, is what stops it.
