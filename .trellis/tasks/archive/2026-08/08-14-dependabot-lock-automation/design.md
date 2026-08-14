# Design — automated `requirements-dev.lock` regeneration for Dependabot PRs

## Decision

A `pull_request_target` workflow, isolated so that **no file from the bot
branch is ever placed in the working tree and no code from it is ever
executed**, which regenerates the lock and pushes the result to the bot branch.

This is the trigger and isolation model selected for the task. One amendment to
it is forced by a GitHub platform rule and is described under "The push
credential" below: the push itself cannot use `GITHUB_TOKEN`.

## Why `pull_request_target`

`pull_request` workflows triggered by Dependabot get a read-only
`GITHUB_TOKEN` and no secrets, so they cannot push. `pull_request_target` runs
in the context of the base repository, where an elevated token is available.

The standard hazard of `pull_request_target` is that people combine it with a
checkout of the PR head and then execute the head's code with a writable token.
This design does not check out the head at all. That is the whole security
argument, and it must not be weakened later for convenience.

## Answers to the questions the PRD requires

### Which trigger, and why

`pull_request_target`, filtered to `paths: [requirements-dev.txt]`. It is the
only trigger that yields a writable context for a Dependabot-authored PR.

### What the credential can write to, and how it is scoped down

Job-level `permissions: { contents: write }` and nothing else. The repository
default stays `contents: read` (`.github/workflows/tests.yml:8`), so this is a
single job's elevation, matching the existing precedent of `auto-tag-release`
(`.github/workflows/tests.yml:167-170`) rather than introducing a new pattern.

The job runs only when **all** of these hold:

- `github.event.pull_request.user.login == 'dependabot[bot]'` — the PR's author
- `github.actor == 'dependabot[bot]'` — whoever triggered *this* event
- `github.event.pull_request.head.repo.full_name == github.repository` — not a fork

The second condition is the one that is easy to omit and matters most. A PR
authored by Dependabot can still receive a `synchronize` event from a human
pushing to the bot branch; without the `actor` check, that human's content
would be processed by a job holding a writable token.

### What repository content the job executes, and from which ref

Executed code comes exclusively from the **base ref**: the workflow definition
(inherent to `pull_request_target`), the `Makefile` `lock` target, and `uv`.

From the head ref the job takes exactly one blob, `requirements-dev.txt`,
fetched and read without checking the branch out:

```
git fetch --no-tags --depth=1 origin "$HEAD_SHA"
git show "$HEAD_SHA:requirements-dev.txt" > requirements-dev.txt
```

Nothing else from the branch reaches disk. In particular no `uv.toml`, no
`pyproject.toml`, no `.python-version`, no `Makefile` — each of which could
otherwise redirect `uv` at an attacker-chosen index. `make lock` is additionally
run with `UV_NO_CONFIG=1` so a stray config file cannot take effect even if one
appears by another route.

The input is still attacker-influenced data: it names packages and versions.
That is bounded by `--only-binary :all:` in the `lock` target, which the
Makefile already documents as keeping resolution to wheels so "the compile
itself cannot build a source distribution and run its build hooks"
(`Makefile:20-25`). A wheel is downloaded and hashed, never executed. So the
worst an adversarial manifest achieves is naming a package that gets hashed
into a lock — which then faces normal review on the PR.

### How a malicious branch is prevented from escalating into a write

Three independent barriers, any one of which alone would stop it:

1. The head is never checked out, so there is no head-controlled script,
   Makefile, or config for the privileged job to run.
2. The actor/author/fork conditions prevent the job from running at all for
   anything but a Dependabot-authored, Dependabot-triggered, same-repo PR.
3. The push is a single ref update to the PR's own head branch, computed from
   a tree the job built itself (see below). It cannot touch `main`, which is
   additionally protected.

### Building the commit without checking out the head

To push a commit onto the bot branch, the naive route is to check that branch
out — which would put head files on disk and forfeit barrier 1. Instead the
commit is assembled with plumbing against a scratch index:

```
BLOB=$(git hash-object -w requirements-dev.lock)
# mktemp, not `mktemp -u`: the -u form returns a name without creating it, so
# anything could occupy that path before git does. git reads a zero-length file
# as an empty index, so creating it up front costs nothing.
GIT_INDEX_FILE="$(mktemp)"; export GIT_INDEX_FILE
trap 'rm -f "$GIT_INDEX_FILE"' EXIT
git read-tree "$HEAD_SHA"
git update-index --add --cacheinfo "100644,$BLOB,requirements-dev.lock"
TREE=$(git write-tree)
COMMIT=$(git commit-tree "$TREE" -p "$HEAD_SHA" -m "chore(deps): regenerate requirements-dev.lock")
git push origin "$COMMIT:refs/heads/$HEAD_REF"
```

The working tree is never switched. `$HEAD_SHA` is pinned from the event
payload, so a branch that moves mid-run causes the push to be rejected as a
non-fast-forward rather than silently relocking a different commit.

## The push credential — the one amendment

**`GITHUB_TOKEN` cannot be used for the push.** GitHub suppresses workflow runs
for events generated by `GITHUB_TOKEN`, specifically to prevent recursion. A
lock commit pushed with it would therefore never trigger the `tests` workflow,
the PR's required checks would never report on the new head, and the PR would
sit permanently unmergeable — the exact state this task exists to eliminate.

So the push step needs a credential GitHub does not suppress: a GitHub App
installation token (preferred — scoped to this repository, `contents: write`
only, expires in about an hour) or a fine-grained PAT (simpler, but a
long-lived secret owned by a person).

This means the "no new secrets" property of the chosen option does not survive
contact with the platform. The isolation model is unaffected — the App token is
used **only** in the final push step, never for the checkout, and never while
head-controlled content is in play. But it is a real amendment and the task
should not proceed as though the credential question were free.

If that cost is judged too high, the honest fallback is to not automate: the
grouping already merged in #223 caps the manual step at once per week.

## Recursion

Two independent guards, because one is a platform behaviour that could change:

1. The job pushes only when the regenerated lock differs from what the branch
   already carries; an unchanged lock exits before the push.
2. After a push by the App token, the resulting `synchronize` event has
   `github.actor` set to the App, not `dependabot[bot]`, so the `if` condition
   fails and the job does not re-enter.

## Rollout and rollback

Additive: a new workflow file, no change to `tests.yml`. Rollback is deleting
the file — the manual `make lock` path is untouched and remains correct.

The lock-parity gate (`check-dev-requirements-lock.py`) is not modified,
relaxed, or made conditional. If the automation fails or is removed, that gate
still fails a mismatched PR exactly as it does today. The automation only
removes the human step; it never removes the check.

## Rejected alternatives

- **`workflow_run` follow-up.** Also yields a writable context, but it runs
  after `tests` completes, so the first run always reports red before being
  fixed — noisier, and the PR briefly looks broken.
- **Teaching Dependabot to update the lock natively.** Dependabot detects
  pip-compile outputs via the header comment that `make lock` strips with
  `--no-header`, and it invokes `pip-compile` rather than `uv`; matching
  `--universal --generate-hashes --only-binary :all:` byte-for-byte across two
  compilers is not a stable contract.
- **Committing to relax `--require-hashes`.** Ruled out by the PRD constraints.

---

## DECISION (2026-08-14): not building this

Resolved as **won't-do**. The design below is kept as the record of what was
evaluated, not as a plan awaiting execution.

What changed between writing this and deciding: the `GITHUB_TOKEN` finding.
`pull_request_target` was chosen partly because it needed no new secrets, and
that property does not survive — the push requires a GitHub App token, because
GitHub suppresses workflow runs for events `GITHUB_TOKEN` generates, so a lock
pushed with it would never re-trigger `tests` and the PR would sit permanently
unmergeable.

The arithmetic with that cost included:

- **Saved:** four pins, grouped into roughly one PR a week, a couple of minutes
  each — order of 2–3 hours a year.
- **Paid:** a GitHub App to create, install, own, and rotate; two repository
  secrets; a workflow whose correctness rests on git plumbing few reviewers will
  follow; and a standing `contents: write` credential reachable from
  `pull_request_target`, whose isolation holds only while nobody ever
  "simplifies" it into checking out the head.

The toil is bounded and visible; the risk is unbounded and quiet. Not worth it
at this scale.

**Shipped instead:** `make relock-pr PR=<number>` — the same manual step in one
command, with no new credential and no new attack surface. Guards refuse a
non-Dependabot PR and a dirty tree.

**Known consequence, accepted:** the `sd-update-deps` pip auto-merge class stays
structurally empty, so that skill still cannot auto-merge a bot PR for this
repository's only configured ecosystem. Revisit if ecosystems or pin count grow
enough to change the arithmetic; this design is still correct if so.
