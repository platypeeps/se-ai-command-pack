# Implement — close the `pack.review-scope` late-arrival gap for mixed diffs

Execution plan for the upstream change in **platypeeps/sd-ai-command-pack**.
Planning-time upstream head: `c9405f0d` on `main`, where `manifest.json` reads
`0.71.22` — so the bump target is `0.71.23`. Re-read `manifest.json` at
implementation time and bump from whatever it actually holds; upstream `main`
may have advanced since planning.

Approval standing: explicit per-PR approval was granted 2026-08-16 for one pull
request against `platypeeps/sd-ai-command-pack`. It does not extend to a second.

## Step 0 — isolate

```bash
cd ~/repos/platypeeps/sd-ai-command-pack   # the shared clone; do not work in it
git fetch origin
WT="$(mktemp -d)/sd-pack-late-arrival"
git worktree add "$WT" -b fix/pr-body-scope-mixed-diff origin/main
cd "$WT"
```

Work only inside the worktree. The shared clone is in use by other sessions and
must not be checked out, reset, or branched. Record `git rev-parse origin/main`
as `BASE` — every falsifiability check below restores from it.

**Rollback point R0:** `git worktree remove --force <path>` and delete the
branch. Nothing outside the worktree has been touched.

## Step 1 — tests first, red

Add to `tests/test_pr_body_scope.py`. Every case drives the real script through
`subprocess` the way the existing suite does (`SCRIPT` at `:20`).

| # | Case | Expect |
| --- | --- | --- |
| 1 | Mixed diff: `.trellis/spec/backend/x.md` + `.trellis/workspace/u/journal-4.md` + `.trellis/workspace/u/index.md` | exit `0`; body gains `Tooling/generated scope:`; lists both workspace paths sorted; does **not** contain `limited to`; does not list the spec path |
| 2 | No tooling path at all: only `.trellis/spec/backend/x.md` | exit `3`; body byte-identical |
| 3 | All-tooling diff | exit `0`; body gains the **existing** `limited to` text verbatim — regression guard on the unchanged branch |
| 4 | Empty changed set | exit `3`; body byte-identical |
| 5 | 25 tooling paths | exactly 20 enumerated, plus `...and 5 more`; assert the number is correct, not merely present |
| 6 | Run twice on the mixed diff | second run exit `0`, body unchanged, heading appears exactly once |
| 7 | Mixed-diff body then fed to the gate | `bash templates/scripts/sd-ai-command-pack-review-scope.sh` with `SD_AI_COMMAND_PACK_SCOPE_PR_BODY` set to the prepared body, against a diff containing the journal/index files, exits `0` |

Case 7 is the acceptance-criterion-1 reproduction: it joins the creation-time
body to the finalization-time diff, which is the actual defect.
Case 2 is the acceptance-criterion-3 companion — the proof the gate was not
weakened.

**Gate G1:** cases 1, 5, 6, 7 must **fail** at this point. Run them before
touching the script and record the failure output. A test that has never been
seen red proves nothing.

## Step 2 — implement

Edit **`templates/scripts/sd-ai-command-pack-pr-body-scope.py`** only — it is
the authored source; the other three copies are generated.

1. Add `MAX_ENUMERATED_SCOPE_PATHS = 20` beside the existing constants at
   `:71-76`.
2. Add the mixed-diff section renderer. It takes the sorted matched paths,
   caps at 20, and appends an explicit remainder bullet when it truncates.
   Keep `TOOLING_SCOPE_SECTION` as-is for the all-tooling case.
3. In `prepare_tooling_body` (`:677-730`), replace the single `if unmatched:`
   early return at `:696-706` with the three-way branch from `design.md`:
   `matched` empty → `3` with a message naming *why* ("no generated or
   repository-bookkeeping paths to declare"); `unmatched` empty → existing
   behavior untouched; otherwise → render and append the enumerating section,
   return `0`.
4. Update the module docstring exit-code table (`:30-38`) and the
   `--prepare-tooling-body` help string (`:838-846`), both of which currently
   say "empty or mixed scope exits 3".

Reuse `_append_tooling_scope`'s separator logic and `_atomic_write_body`
unchanged — no new write path.

**Gate G2:** cases 1–7 all green.

```bash
.venv/bin/python -m unittest tests.test_pr_body_scope -v
```

**Gate G3 — falsifiability.** Restore the pre-change script and confirm the new
cases go red again. Use `git checkout`, not `git stash` — `git stash push -- <file>`
silently does nothing once the change is committed, a trap recorded in the
precedent's C-11.

```bash
git checkout "$BASE" -- templates/scripts/sd-ai-command-pack-pr-body-scope.py
.venv/bin/python -m unittest tests.test_pr_body_scope -v   # cases 1,5,6,7 must fail
git checkout HEAD -- templates/scripts/sd-ai-command-pack-pr-body-scope.py
```

**Rollback point R1:** revert this file; tests return to red; nothing generated
yet.

## Step 3 — update every surface stating the old contract

Enumerate by grep, not memory (acceptance criterion 4):

```bash
grep -rn -- 'prepare-tooling-body' templates/ docs/ README.md CONTRIBUTING.md \
  | grep -v '^templates/scripts/'
grep -rn 'mixed' templates/.agents/skills/sd-create-pr/SKILL.md templates/docs/SD_AI_COMMAND_PACK.md
```

Known at planning time — re-run the grep, do not trust this list:

- `templates/.agents/skills/sd-create-pr/SKILL.md` — "Exit `3` is the helper's
  non-error mixed-scope result." The `case` block itself needs no change; only
  the prose describing what `3` means.
- `templates/docs/SD_AI_COMMAND_PACK.md:823-826` — "exit `3` means a mixed or
  empty diff and leaves the body unchanged."
- The script docstring and `--help` (already done in Step 2).

New meaning to state in all of them: exit `3` means *there was nothing to
declare* — an empty diff, or a diff with no generated or bookkeeping path. A
mixed diff now gets a section naming its tooling paths.

## Step 4 — regenerate mirrors and bookkeeping

```bash
make generate      # plugins/sd/bin + plugins/sd/machine-payload
make sync          # scripts/ dogfood mirror
```

Then, because the edited file lives under both `templates/` and `plugins/`, the
version gate fires and these are mandatory:

- `manifest.json` → `"version": "0.71.23"`
- `CHANGELOG.md` → new top heading `## 0.71.23 - <date>` describing the
  behavior change and the new exit-`3` meaning
- `docs/fleet/candidate-validation.json` → regenerated all-pass ledger matching
  the exact payload (the `.githooks/pre-push` gate rejects a stale one)
- `plugins/sd/.claude-plugin/plugin.json` version — written by `make generate`;
  confirm rather than hand-edit

**Gate G4:**

```bash
.venv/bin/python .github/scripts/generate-plugin.py --check   # no drift
make check                                                    # includes run_pack_source_drift_gates
```

Expected: drift gates report compared pairs with zero `template drift:` lines,
and no `release version drift` error.

**Rollback point R2:** `git checkout -- .` inside the worktree returns to the
post-Step-3 state; regeneration is deterministic and repeatable.

## Step 5 — full validation

```bash
.venv/bin/python -m unittest tests.test_pr_body_scope tests.test_review_scope \
  tests.test_review_controller tests.test_pack_drift tests.test_generate_plugin
make test
bash .github/scripts/check-shipped-script-coverage.sh   # pr-body-scope.py floor is 78
```

Coverage is the live risk: the new branch adds lines to a file already held to
78%. If the floor breaks, the fix is more test cases, never lowering the floor.

**Report the actual numbers.** A partial pass is not a pass; if `make test` is
too slow to complete, say so and name what did run rather than implying full
coverage.

## Step 6 — upstream PR

Conventional commit, e.g.
`fix(pr-body-scope): declare the tooling subset of a mixed diff`, plus the
release commit if the repo separates them. Open the PR against `main`.

The PR body must itself carry a `Tooling/generated scope:` section — this change
touches `templates/**`, `plugins/**`, and `docs/**`, so it trips its own gate.

Record in the PR: the defect, the five observed PRs (#156, #163, #172, #203,
#208), the exit-code contract change, and the falsifiability evidence from G3.

## Step 7 — close out in this repository

1. Update the "late arrival" section of
   `.trellis/spec/backend/quality-guidelines.md` to document the new mechanism,
   **replacing** the manual-workaround guidance rather than sitting beside it
   (acceptance criterion 2). This is the only repo-owned deliverable. It must
   state the residual gap from `design.md` — a creation-time diff with zero
   tooling paths is still uncovered — rather than claiming the gap is closed
   unconditionally. Keep enough of the manual workaround to serve that case.
2. Write `disposition.md` in this task directory following
   `08-10-review-check-cache-pr-body/disposition.md`: route, upstream PR URL,
   branch, base and head SHAs, and each acceptance criterion ticked with quoted
   evidence and the exact head it was taken at.
3. Do **not** edit the vendored copies in this repository. They stay
   byte-identical to upstream until a pack refresh brings `0.71.23`.
4. Do not open a follow-up task for the refresh; the fleet lane owns it.

## Validation summary

| Gate | Command | Pass condition |
| --- | --- | --- |
| G1 | `unittest tests.test_pr_body_scope` before Step 2 | cases 1, 5, 6, 7 fail |
| G2 | `unittest tests.test_pr_body_scope` after Step 2 | all 7 pass |
| G3 | `git checkout $BASE -- <script>` then rerun | cases 1, 5, 6, 7 fail again |
| G4 | `generate-plugin.py --check`; `make check` | no drift, no version drift |
| G5 | `make test`; coverage script | suite green, `pr-body-scope.py` ≥ 78 |
