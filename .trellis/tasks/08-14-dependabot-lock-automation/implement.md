# Implementation plan — Dependabot lock regeneration

Blocked until the App credential decision in `design.md` ("The push credential")
is settled. Step 0 is that decision; nothing below is worth starting without it.

## Step 0 — settle the credential (human, blocking)

- [ ] Decide: GitHub App installation token, fine-grained PAT, or abandon the
      automation and keep the weekly manual `make lock`.
- [ ] If App: create it, install it on `platypeeps/se-ai-command-pack` with
      `contents: write` and nothing else, store `LOCK_BOT_APP_ID` and
      `LOCK_BOT_PRIVATE_KEY` as repository secrets.
- [ ] Record the choice and its scope in `CONTRIBUTING.md` in the same PR that
      adds the workflow — the PRD requires the credential model be documented
      where the manual instruction lives today.

Rollback point: nothing has changed in the repository yet.

## Step 1 — the workflow, gated off

- [ ] Add `.github/workflows/dependabot-lock.yml` with the trigger, the three
      `if` conditions, `permissions: { contents: write }`, base-ref checkout,
      single-blob fetch of `requirements-dev.txt`, `UV_NO_CONFIG=1 make lock`,
      the plumbing commit, and the push.
- [ ] Land it with the push step behind an explicit `if: false` (or a
      `DRY_RUN` repository variable) so the first landing cannot write.

Validation:

```bash
# YAML parses and has the shape intended
.venv/bin/python -c "import yaml,json;print(json.dumps(yaml.safe_load(open('.github/workflows/dependabot-lock.yml')),indent=1))"
make check
SD_AI_COMMAND_PACK_REVIEW_PREFLIGHT_BASE_REF=origin/main node scripts/sd-ai-command-pack-review-preflight.mjs
```

Rollback point: delete the file; nothing else references it.

## Step 2 — prove the gate before arming the write

The conditions are the security boundary, so they get evidence, not reasoning.

- [ ] Open a throwaway human-authored PR touching `requirements-dev.txt`.
      Expected: job does not run (author is not Dependabot).
- [ ] Push a commit to a live Dependabot branch as a human. Expected: job does
      not run (`github.actor` is not Dependabot) — this is the condition most
      likely to be wrong, and the one a reviewer cannot verify by reading.
- [ ] Confirm on a real Dependabot PR that the job *does* reach the (still
      disabled) push step.

Do not proceed while any of these three disagrees with the expectation.

## Step 3 — arm the push

- [ ] Remove the `if: false` / flip the dry-run variable.
- [ ] On the next real Dependabot pip PR, verify end to end:
      - a lock commit appears on the bot branch, authored by the App;
      - the `tests` workflow **runs on the new head** (this is what the
        `GITHUB_TOKEN` suppression rule would break, so it is the acceptance
        criterion that actually discriminates);
      - `lint` passes, meaning `check-dev-requirements-lock.py` is satisfied;
      - the PR reaches `CLEAN` with no human commit on the branch.
- [ ] Diff the CI-produced lock against a locally produced one for the same
      pins; require byte equality.

```bash
git fetch origin <bot-branch> && git checkout <bot-branch>
make lock && git diff --exit-code requirements-dev.lock   # must be empty
```

Rollback point: re-disable the push step. Any lock commit already pushed is a
normal commit on a bot branch and can be dropped by closing the PR.

## Step 4 — prove the gate still bites

- [ ] Push a deliberately mismatched lock to a branch and confirm `lint` fails
      with `pin-mismatch`. The automation must not have made the check
      conditional or advisory.

## Step 5 — recursion and documentation

- [ ] Confirm the relock push does not re-trigger the relock job (inspect the
      `synchronize` run list for a second invocation).
- [ ] Confirm an unchanged lock exits before pushing (re-run on an
      already-relocked PR).
- [ ] Update the `CONTRIBUTING.md` "Lock regeneration" section: it currently
      instructs the maintainer to run `make lock` by hand for bot PRs, which
      becomes wrong the moment this lands.
- [ ] Update `sd-update-deps` expectations if the pip auto-merge class is now
      reachable — but do not change that skill's merge authority.

## Out of scope

npm; changing the lock's guarantees; auto-merging majors; touching the
`sd-update-deps` merge path.
