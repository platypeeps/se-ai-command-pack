# Quality Guidelines

> Code quality standards for backend development.

> **Reading the sd-ai-command-pack paths below.** This checkout installs the
> pack in **thin** mode, so `scripts/sd-ai-command-pack-*`,
> `docs/SD_AI_COMMAND_PACK.md`, `.agents/skills/sd-*`, and `.claude/skills/sd-*`
> are not in this tree. Findings recorded before the conversion cite them by
> the repository-relative path they had at the time; those citations are kept
> verbatim because they are what the commit and the line numbers refer to.
> Resolve any of them against the machine install with
> `.sd-ai-command-pack/bin/sd-ai-command-pack-review-layout.py --resolve <name>`.
> Cite the machine form, `~/.agents/...`, in anything written from here on.

---

## Overview

Changes must preserve safe, deterministic installation across supported Python
and operating-system versions. Prefer small modules, explicit data flow,
immutable result records, plan-before-apply operations, and tests at the same
boundary users exercise.

---

## Forbidden Patterns

- Hand-editing generated `manifest.json` rows instead of changing the registry
  or canonical templates and running `make generate`.
- Hand-editing `generated/skills/claude/` instead of changing the canonical
  skill or its registry-owned runtime profile and running `make generate`.
- Hand-editing the marker-bounded README skill catalog instead of changing
  `SKILLS` or canonical skill frontmatter and running `make generate`.
- Writing outside the validated install root or following untrusted symlinked
  receipt/destination paths.
- Destructive overwrite/removal without hash or template provenance, except
  when the user explicitly requests `--force`.
- Network/Git mutation during a dry-run.
- Broad exception catches that hide actionable filesystem or subprocess errors.
- Adding a shipped payload change without a manifest version bump and matching
  `CHANGELOG.md` entry.

---

## Required Patterns

- Validate manifest, registry, source, and destination paths before mutation.
- Preview a multi-file lifecycle operation before applying it.
- Use atomic writes for installed files and receipts.
- Replace differing installed payload bytes without `--force` only when a
  regular-file destination matches its prior provenance hash; keep preserve
  policies authoritative and revalidate the destination digest at apply time.
- Keep canonical skill content under `templates/skills/` and pack declarations
  in `installer/registry.py`.
- Keep every registered skill in exactly one portable runtime profile. Apply
  host fields only through an allowlisted generator adapter; unknown values or
  unsupported fields fail before any output is written.
- Keep family membership singular and canonical in `SKILLS`; derive
  `SKILL_NAMES`, preserve flat skill paths, and generate grouped catalog prose
  from validated frontmatter.
- When sibling skills intentionally share a request noun, route by the user's
  intended outcome instead of deleting accepted capability from either skill.
  For tutorials, original thesis, argument, firsthand experience, or publication
  contribution belongs to `se-author`; ordered teaching that completes and
  verifies an observable result belongs to `se-tutorial`.
- If the intended outcome leaves those workflows materially ambiguous, ask one
  focused routing question before selecting a skill.
- For portable comparison state, define staleness from an explicit caller
  freshness policy or an unrecoverable source-specific continuity gap. Never
  select a stale-state recovery branch from age alone when no freshness
  horizon is part of the accepted contract; preserve source boundaries and use
  qualified comparison when continuity fails.
- Review structured user input semantically, not from question-related
  keywords. Require a blocking question only when undiscoverable input,
  materially different choices, consequential-action approval, or an accepted
  preference without a safe default makes assumption unsafe. Keep discoverable
  answers, explicit safe defaults, and reversible optional corrections
  non-blocking or question-free, and express host tools through portable
  capability semantics plus verified target guidance.
- Preserve compatibility with Python 3.10; use postponed annotations where
  modern typing syntax appears.
- Format for Ruff's 88-character line length and selected `E4`, `E7`, `E9`,
  `F`, `I`, and `B` rules; keep mypy clean for `installer` and `install.py`.

---

## Testing Requirements

- Add focused unittest coverage for every observable behavior change, including
  failure and preservation paths when filesystem state is involved.
- Pin both positive sides of any overlapping-skill routing boundary plus its
  materially ambiguous clarification path.
- Pin fresh, explicit-policy stale, continuity-gap stale, and no-policy paths
  whenever a shared state contract selects normal versus qualified comparison.
- For interaction-design review, pin a consequential unresolved choice, a
  discoverable or safely defaulted non-finding, a keyword-only candidate, and
  option-versus-free-form suggestion behavior.
- Use temporary install roots; never target the developer's real home directory
  from tests.
- For receipt-vouched refreshes, pin prior-payload upgrades, user drift,
  untrusted receipts, preservation-policy precedence, and a destination change
  between planning and application.
- Mock Git/subprocess boundaries when asserting lifecycle sequencing, while
  retaining end-to-end CLI tests for parsing, exit codes, and installed files.
- Run `make check`: generation parity, Ruff, mypy, the unittest suite, the
  release payload/version gate, and vendored-shell syntax (`bash -n` via
  `shell-syntax`) must all pass.
- `sd-check` runs the repo-own gates registered in
  `.sd-ai-command-pack/check.json` (`repo.test`, `repo.lint`,
  `repo.shellsyntax`). Registered commands must stay guard-safe: `gate-test`
  and `gate-lint` are the cache-free variants of `test`/`lint` (no
  `.coverage`, no `.ruff_cache`) because sd-check's state guard fails any
  check that writes a guarded path. Do not "simplify" them back to
  `test`/`lint`, and keep `gate-lint`'s path list on the shared
  `LINT_PATHS`/`MYPY_PATHS` Makefile variables so it cannot drift from
  `lint`. `check.json` is repo-authored configuration, not pack payload —
  `provenance.json` must never list it. CI's `ci-result` lane aggregates via
  `.github/scripts/aggregate-ci-result.py`: required lanes must be exactly
  `success` (a skipped required lane fails), `auto-tag-release` is
  conditional, and an undeclared or missing lane fails closed — a job rename
  in `tests.yml` must update the script's lane sets. Vendored shell gets
  syntax checking only; deep lint (shellcheck) is deliberately declined for
  upstream-owned files. Branch protection stays `strict: false` with zero
  required approvals — accepted disposition recorded in
  `08-08-ci-gate-fail-softs/design.md`, revisit if a second maintainer joins
  or a stale-merge breakage reaches `main`.

### Prose contracts: prove the pin can fail

Most of this pack's behavior lives in Markdown, so its tests are substring pins
against `SKILL.md` and skill-owned references (`normalized()`,
`normalized_resource()`). Such a pin has a silent failure mode a code assertion
does not: **if the file already contains the token, the assertion passes before
the change and can never fail.** It then reads as coverage while proving
nothing.

Two rules, both cheap:

1. Before adding a pin, `grep` the token against the *unedited* file and confirm
   it is absent. Prefer a token that is distinctive to the new contract over one
   that merely sounds like it.
2. After writing both the edit and the pin, prove the pair: restore the source
   files from `HEAD`, run the new tests, confirm they fail, restore the edits,
   confirm they pass.

Runnable as written — set `FILE` to the source file the pin asserts against and
`TEST` to the new test class, then paste the block:

```bash
FILE=templates/skills/<skill>/SKILL.md
TEST=<TestClass>
TMP="$(mktemp)"

cp "$FILE" "$TMP" && git checkout HEAD -- "$FILE"
.venv/bin/python -m unittest discover -s tests -p test_skills.py -k "$TEST"   # expect FAILED
cp "$TMP" "$FILE" && rm -f "$TMP"
.venv/bin/python -m unittest discover -s tests -p test_skills.py -k "$TEST"   # expect OK
```

With more than one source file, list them all in the `git checkout` and restore
each from its own copy; the pin is only proved when every file the tests read is
back at its pre-change state for the failing run.

Real example: a pin of `## Gotchas` against
`se-review-skills/references/session-evidence.md` was accepted in review and
would have been permanently green — the file's existing
`## Gotchas and regression records` heading contains that substring. The
heading-shaped token looked more rigorous than the phrase that actually carried
the contract, which is exactly why the grep is not optional.

Note that `normalized*()` collapse whitespace, so a pinned phrase survives
rewrapping. Pin the shortest phrase that carries the contract: long enough that
deleting the contract breaks it, short enough that rewording does not.

### Test hermeticity: the machine's state is not the fixture

A test that reads the developer's git configuration or an untracked file is
green here and red — or worse, silently different — everywhere else. PR #206
merged a suite that read `.trellis/.template-hashes.json`, which is gitignored:
`make check` was green locally while every CI lane failed. Two rules, both
enforced by `tests/test_test_hermeticity.py`.

**1. Every `git` subprocess passes `env=git_env()`.** `git_env()`
(`tests/install_test_support.py`) is built from a `GIT_*`-stripped copy of
`os.environ`, then sets `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` to `os.devnull`,
`GIT_CONFIG_NOSYSTEM=1`, an author/committer identity, and
`GIT_TERMINAL_PROMPT=0`. The strip is the load-bearing half:
`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` and
`GIT_CONFIG_PARAMETERS` enter at **command-line scope**, which outranks every
configuration file — pointing the file scopes at `/dev/null` alone leaves them
live. Use `hermetic_git_environment()` (the same values via
`mock.patch.dict(..., clear=True)`) when git is reached through a child script
or through production code that passes no `env=`. `GIT_CONFIG_GLOBAL` needs
git ≥ 2.32; a version assertion makes an older git fail loudly instead of
running unscrubbed.

**2. A read of an untracked repository path must be declared.** A module that
legitimately reads one declares it in its own module-level
`HERMETICITY_UNTRACKED_PATHS` tuple and tolerates its absence
(`tests/test_repo_tooling_ownership.py`, `tests/test_repomix.py`). An entry for
a *tracked* path fails too, so the tuple cannot become a general bypass.

Both guards are AST walks over `git ls-files -- tests/*.py`, so a newly tracked
module is covered on landing, and both carry a measured floor
(`MIN_GIT_CALL_SITES`, `MIN_PACK_ROOT_PATHS`) so a half-broken walk fails
instead of reporting zero violations over zero inspected sites. Raise a floor
when you add sites; never lower one to make a walk pass.

Structural guards cannot see a path or argv assembled at runtime. `make
test-hermetic` closes that gap empirically: it copies `git ls-files` into a
temporary directory, runs `git init`/`add`/`commit` there (without it, every
`git ls-files` on `PACK_ROOT` exits 128), and runs the whole suite under a
hostile `HOME` plus a `GIT_CONFIG_COUNT` command-scope triple. **The lane's own
setup must carry the same scrub as the code it tests** — an ambient
`core.hooksPath` failed the setup commit and the lane exited before running a
test — but scope it to a shell function, never an exported block: a
`GIT_CONFIG_GLOBAL` still in scope during the hostile run outranks the hostile
`HOME` and silently defangs the lane. Use
`$(abspath $(RUN_PYTHON))` for the interpreter — a `$(CURDIR)`-relative path
resolves against the temporary directory and breaks CI. The lane is deliberately
**not** in `make check` (~40 s); CI runs it as the `test-hermetic` job. Adding
or renaming a lane touches four places, not one: `tests.yml` (the job plus
`ci-result.needs`), `REQUIRED_LANES` in `.github/scripts/aggregate-ci-result.py`,
and the fixture in `tests/test_aggregate_ci_result.py`. Assertions about how
many lanes exist must enumerate from the workflow rather than hardcode a count.

---

## Review And Retry Conventions

Six ship-loop conventions that cost rounds when a run rediscovers them.

### The `pack.review-scope` gate: three categories, three headings, late arrival

The check lives in `scripts/sd-ai-command-pack-review-scope.sh` (vendored,
`install: "always"` — re-locate by symbol, not line, after any pack refresh).
It fails when the branch diff contains a scoped file and the PR body lacks a
recognized scope heading. Two distinct lists matter, and conflating them is
the recurring mistake:

**Categories** — what makes the section *required*, classified in `main`'s
dispatch, one predicate each:

1. Copied/generated Trellis or sd-ai-command-pack files
   (`is_copied_review_scope_path`: any exact installed pack target via
   `is_pack_target_path`, or a Trellis runtime path via
   `is_trellis_runtime_path` — which excludes `.trellis/tasks/**` task
   artifacts).
2. Known repository-map files (`is_repository_map_scope_path`: exactly
   `docs/repomix-map.md` and `.github/scripts/update-repomix`).
3. Trellis workspace journal/index files (`is_trellis_journal_scope_path`:
   `.trellis/workspace/*/journal-*.md` and `.trellis/workspace/*/index.md`).

**Headings** — what the PR body may *say*, matched case-insensitively by
`github_pr_body_mentions_scope` (leading blockquote/heading/list markers and a
trailing colon are tolerated): `Tooling/generated scope`,
`Generated/tooling scope`, or `Copied/generated scope`.

The third category arrives late by construction: finalization commits the
session journal and workspace index, so a body that correctly needed no
section at PR-creation time fails `pack.review-scope` on the successor-head
re-entry — after the body was authored and judged complete. The diff that
decides the requirement does not exist yet when the PR is opened (PR #162
passed with a proactive section, PR #163 burned two rounds without one).

**From pack 0.71.23 the preparer closes this for the ordinary case.**
`--prepare-tooling-body` (`scripts/sd-ai-command-pack-pr-body-scope.py`) used
to append the section only when *every* changed path matched a tooling
pattern; a diff mixing tooling with authored prose (e.g. `.trellis/spec/**`,
which matches no tooling pattern) exited `3` and wrote nothing. That refusal
was a truthfulness guard rather than an oversight — the canned sentence claims
the change is *limited to* generated surfaces, false once authored files are
present.

A mixed diff now gets a section naming only the paths proven to be generated,
worded as a non-exhaustive `include:` list so it stays true after finalization
adds more. Because the gate tests for heading *presence* and never checks that
declared paths match the triggering ones, a heading written at PR creation
satisfies it at the finalization head. `sd-create-pr` already routes exit `0`
into `gh pr edit --body-file`, so nothing above the script changed
(platypeeps/sd-ai-command-pack#480 — routing and evidence in the
`08-10-review-scope-late-arrival` task's `disposition.md`).

Check the **behaviour**, not a version string. This repository is a `thin`
consumer (`"mode": "thin"` in `.sd-ai-command-pack/manifest.json`), so that
manifest holds the *pin* while the script that actually runs is the
machine-scope copy in `~/.agents/bin/`. The two diverge in practice, not merely
in principle — a machine-scope refresh moves the runtime without touching the
pin, and this section was itself written with the pin one release behind the
script that was executing. `sd-status` reports "pin versus machine install" as
its own skew row for exactly this reason. Reading the pin can therefore report a
version that is not what executes, in either direction, so no version number is
recorded here: the probe below is the authority.

Probe the script that runs:

```bash
d="$(mktemp -d)"; trap 'rm -rf "$d"' EXIT
printf 'body\n' > "$d/body.md"
printf '.trellis/tasks/archive/2026-08/08-10-review-scope-late-arrival/prd.md\0.trellis/spec/backend/quality-guidelines.md\0' \
  > "$d/paths.nul"
python3 ~/.agents/bin/sd-ai-command-pack-pr-body-scope.py --prepare-tooling-body \
  --body-file "$d/body.md" --changed-files "$d/paths.nul"; echo "exit=$?"
cat "$d/body.md"
```

Both paths are real files in this repository, one bookkeeping and one authored,
so the probe stays valid if the script ever starts checking that paths exist.

`exit=0` with a `Tooling/generated scope:` heading appended to `$d/body.md` is
0.71.23 or later — the preparer handles mixed diffs and no hand-authoring is
needed. `exit=3` with `info: ... not tooling/generated-only` is the **old**
behaviour: hand-author the section.

In 0.71.23 and later, exit `3` means *nothing to declare*: an empty diff, or one
with no generated path at all. Below 0.71.23 it carried a wider meaning and a
mixed diff landed in it. Either way it is a non-error and its `info:` line is
descriptive, not directive.

**Two cases still need the section hand-authored**, and both keep the manual
workaround alive:

- **No generated path at PR-creation time.** The preparer will not declare what
  it cannot prove, so a branch that carries no generated path when the PR is
  opened but acquires journal/index files at finalization still fails at the
  successor head. Closing that would require asserting a future diff. Write the
  section proactively on such a branch.
- **Custom-bodied PR**: `sd-create-pr` forbids running automatic preparation
  against a user-provided body (byte-for-byte preservation), so for such PRs
  the preparer is deliberately never consulted — even when the diff is
  all-tooling and the preparer would have matched every path. Blaming the
  diff shape here points at the wrong remedy: hand-authoring the section is
  the standing requirement for custom-bodied PRs.

**Fixing the body off-head is provable at the same head.** From v0.66.1 the
coordinator recomputes the deterministic check on every invocation instead of
serving a stored verdict, precisely because `pack.review-scope` reads the PR
body — an input the attempt key does not cover. Editing the body and rerunning
reports the current verdict; no new head, no fresh `--attempt-id`, no deleted
state file (platypeeps/sd-ai-command-pack#417). Earlier guidance here described
the replay trap and the `durationMs`-identical tell from PR #210; that behavior
predates v0.66.1 and no longer applies. Confirming the gate by hand is still
worth the ten seconds before concluding anything about the branch:

```bash
bash ~/.agents/bin/sd-ai-command-pack-review-scope.sh   # exit 0 once the body is fixed
```

### The Obsidian KB refresh point: after the last documentation-shaped mutation

`knowledge.obsidian-kb` compares the gitignored local `.obsidian-kb` copies
against the current tracked documentation set. It goes stale — and blocks the
typed `sd-check` mid-ship — after *any* documentation-affecting mutation that
lands later than the last refresh, which in practice means it fires twice per
ship if refreshed only once: documentation edits made after `sd-update-spec`
already ran, and the `task.py archive` commit that moves the task directory
under `.trellis/tasks/archive/` (task `start` metadata writes count too).

Remediation is one idempotent command that touches only gitignored paths and
needs no commit:

```bash
python3 ~/.agents/bin/sd-ai-command-pack-update-spec-kb.py --if-present
```

The ordering rule: refresh after the **last** documentation-affecting mutation
of the branch — including the archive commit — not merely once during
`sd-update-spec`.

### The `_example` scaffold row is sanctioned, not leftover

`task.py create` seeds a planning task's `implement.jsonl` and `check.jsonl`
with one `_example` row whose own text says to delete it once real entries are
added. The review preflight exempts that pristine scaffold deliberately —
`validateBookkeepingTaskContexts` in
`scripts/sd-ai-command-pack-review-preflight.mjs` gates on
`!archived && isPlainObject(record) && record.status === 'planning'` — so
creating a task never fails either lane. The `isPlainObject` term is not
incidental: a missing or unparsable `task.json` leaves the planning status
unproven, so the exemption switches off and the scaffold row is reported.
`.prism/rules.json` carries the matching `trellis-scaffold-convention` rule.

Empty and scaffold-bearing are both acceptable resting states, and neither is a
finding. The preflight exemption turns the scaffold row into a non-issue; an
empty file has no row to object to. Measured across the 15 planning tasks: 12
have empty context files, 3 carry the scaffold, 0 have real entries.

What the convention forbids is the *transition* — emptying a scaffold-bearing
file in response to a review comment. That is churn that contradicts the
tooling, and it is the specific move this section exists to stop. Do not
normalize in the other direction either: mass-adding scaffold rows to the 12
empty tasks would touch a dozen unrelated tasks to satisfy a consistency no
gate asks for.

Report such a file only when a row is malformed JSONL, references a path
outside the allowed spec/research roots, or mixes real entries with the
scaffold row.

### Rebutting a verified-wrong local finding: `--local-disposition`

Since pack v0.64.26 (installed v0.64.32), a local provider finding that a run
has **verified to be wrong against the checkout** can be closed with
`--local-disposition '<stable-id>=rebutted'` on the review coordinator. This is
the only sanctioned way to clear a local finding without changing code. Before
that version no control reached a local finding, and two still do not:

- `--remote-disposition` validates against remote receipt rows only; it never
  touches the local receipt.
- The `--finding-family` / `--family-evidence` route admits evidence only when
  `audit["localOutcome"] == "clean"` — and a local finding is by definition why
  the outcome is not clean. It is a repeated-family round-extension gate, not a
  disposition mechanism.

Rules of use:

- **Only after verification.** Rebut a finding only when the run has checked it
  against the checkout and can state why it is wrong. State those grounds in
  the run's report; the receipt records the disposition, the report records the
  reasoning. When verification is not conclusive, do not rebut — stop the chain
  and report.
- **Fail-closed grammar.** One flag per finding, `<stable-id>=rebutted`.
  Malformed values ("local dispositions must use <stable-id>=rebutted"),
  duplicate ids ("local disposition ids must be unique"), and ids matching no
  finding at the current head ("local disposition ids match no finding at this
  head") each fail the invocation. There is no bulk form, severity threshold,
  or waiver, deliberately.
- **Per-head contract.** Finding ids are stable across heads, but dispositions
  are **not inherited**: a rebuttal applies to the head it was recorded
  against. Re-supplying a still-matching id on a new head is permitted but
  obliges the run to re-verify the finding is still wrong at that head.
- **Unchanged-head rebuttal reaches the stage; a *rejected* one used to poison
  the attempt.** The coordinator memoizes the local result in its per-attempt
  state, but supplying `--local-disposition` re-enters the local stage anyway
  (`state.get("local") is None or args.local_disposition`, verified in the
  installed v0.64.33 coordinator), and the stage reuses the stored receipt
  after exact-match validation and applies the rebuttal without re-running any
  provider. A fresh `--attempt-id` is **not** required for this. Earlier
  guidance here said the opposite; it predated the fix, which landed upstream on
  2026-08-09 as `7beccf32` ("apply local-disposition reruns and gate on
  outstanding findings") and first shipped in **v0.64.33** — the version this
  repository has installed. Issue platypeeps/sd-ai-command-pack#397 closed the
  same day.
  What survived is the failure one step over: a disposition set whose ids match
  no finding at the current head returns `invalid`, and below pack v0.66.1 the
  coordinator persisted that verdict *over* the good report, so the next
  invocation replayed the rejection even with no dispositions at all. Two ways
  out, in preference order. **Re-invoke with a disposition set that does match**
  — `or args.local_disposition` re-enters the stage regardless of what is
  cached, so a corrected set replaces the rejection in the same attempt. That
  works only when a valid id exists to supply; when the receipt has no finding
  to rebut, it does not. **Then** a fresh `--attempt-id`, which costs less than
  it sounds: it discards the *coordinator's* attempt state — remote request,
  receipt, observation, recorded dispositions — while the local stage's durable
  provider receipt survives and is reused, because its identity is
  `_receipt_identity(target, plan)` and carries no attempt id
  (`scripts/sd-ai-command-pack-review-local.py`, `execute`). From v0.66.1
  neither is
  needed: the rejection is not persisted, so the next invocation reuses a prior
  stored report or recomputes when none exists — never replays the rejection
  (platypeeps/sd-ai-command-pack#417 — routing and evidence in the
  `08-10-review-check-cache-pr-body` task's `disposition.md`).
  Neither behaviour is something to patch locally: the coordinator is vendored.
- **Auditable, not silent.** The finding stays in the receipt with
  `disposition: rebutted` under `disposition.localDispositions`; the
  `outstanding` count that drives `_remote_gate` is recomputed from remaining
  outstanding rows. A later reader can see what was rejected.
- **No interaction with the family gate.** A rebuttal does not satisfy the
  repeated-family round-extension requirement; `_remote_gate` still blocks on
  the family gate after outstanding findings are cleared. The two mechanisms
  answer different questions.
- **Still forbidden:** contriving a code change purely to clear the gate. When
  a finding is correct, fix the code; when it is verified wrong, rebut it with
  grounds; when neither is established, stop with a report.

### Repository prism rules govern the shell review lane only

`.prism/rules.json` is delivered to exactly one of the two prism code paths.
A prism finding that contradicts a rule in that file is therefore **expected**
when it comes from the sd-review lane — it is not evidence the rule is broken,
malformed, or unwired (both hypotheses were chased and refuted on PR #158
before the real cause was found).

**The two lanes, shipping branch delta:**

- **Shell lane** — *retired*. Pack 0.65.0 removed the vendored `sd-review-local`
  shell runner along with the `SD_AI_COMMAND_PACK_REVIEW_LOCAL_*` environment
  keys, and the 0.71.1 refresh deleted the copy here. It was the only lane that passed
  `--rules`, `--fail-on`, and `--exclude`, so its removal makes the
  divergence below total rather than partial: no shipped lane delivers
  `.prism/rules.json` to prism any more.
- **sd-review lane** — the lane `sd-ship` Stage 2 runs, and so the lane that
  gates shipping. The built-in adapter in
  `scripts/sd-ai-command-pack-review-local.py` (`_expand_argv`, `:1376`)
  builds `prism review range <base>..<head> --format json` with **none** of
  `--rules`, `--exclude`, `--fail-on`, and never reads `.prism/`. Prism does
  not auto-discover the file (`prism config show` reports no rules entry).

Both lanes also build other scope templates (worktree/codebase/`--paths`
variants); the flag asymmetry is the same in each.

**Gate mechanics, so the divergence is priced correctly:** `--fail-on`
governs prism's *exit status*, not the coordinator's gate. The adapter maps
any non-empty findings list to a `findings` outcome for the non-terminal exit
codes 0/1 (`scripts/sd-ai-command-pack-review-local.py:254-260`,
`:1752-1756`; exits 3/4 stay `unavailable`, unmapped codes `failed`). Low
findings alone block shipping (`remoteGate: blocked
(actionable-local-findings)`), so an inert rule converts directly into a
blocked round; since pack v0.64.26 the round is recoverable with a
per-finding verify-and-rebut via `--local-disposition` (previous section),
which softens the consequence without delivering the rule.

**Degradation behaviour of the rules file.** In the surviving sd-review lane
the file is never read, so every degradation case — missing, unreadable,
malformed — is indistinguishable from the healthy one. No case converts a
findings outcome into a clean one. Do not assert a fail-closed property this
code does not have. (The retired shell lane fell back to prism's defaults
when `[ -f "$rules" ]` failed, and handed an unreadable-but-regular or
malformed file straight to prism; both behaviours left with the script.)

**Ownership.** `.prism/rules.json` is Registry B `install: "if-not-exists"` —
repository-owned after first install; a pack refresh will not discard its
edits, and rules added to it are durable, only undelivered to the sd-review
lane. `scripts/sd-ai-command-pack-review-local.py` is Registry B
`install: "always"` (vendored); its shell sibling was retired in 0.65.0.

**Local-only record** (per the four-field format in "Vendored-Artifact
Ownership And Upstream Route"):

- Owning pack: sd-ai-command-pack.
- Files: `scripts/sd-ai-command-pack-review-local.py` (Registry B,
  `kind: script`, `install: "always"`).
- Behaviour: the built-in prism adapter builds its argv with no `--rules`,
  `--exclude`, or `--fail-on` and never reads `.prism/rules.json`, so
  repository-owned prism rules are inert in the review lane that gates
  shipping, with silence as the only symptom.
- No upstream PR was opened; relay issue:
  <https://github.com/platypeeps/sd-ai-command-pack/issues/409>.

### Stop retrying on a repeated failure signature

A CI lane that fails without running a step — GitHub's `Set up job` erroring
with `Failed to resolve action download info` or `Service Unavailable`, or
several lanes dying at an identical duration — is infrastructure, not the
change. One retry is correct. A second identical signature is the answer:
report the blocker instead of retrying again.

The tell is duration, not conclusion. Four independent lanes finishing at
`15m2s` while the one lane that acquired a runner passes in `8m51s` is a queue
timeout, and no number of retries changes it. Check job steps
(`gh api repos/<owner>/<repo>/actions/jobs/<id>`) before assuming a red lane
ran anything: a `Set up job` failure means zero test evidence either way, so it
is neither a passing nor a failing signal about the code.

#### One `settled-blocked` spans three conditions: classify before responding

The Stage 3 watch coordinator's `settled-blocked` outcome — usually carrying
`merge_state_not_clean` — does not say which of three distinct conditions
produced it, and each demands a different response. The coordinator is
vendored (its outcome vocabulary is an upstream change; see the disposition
in the `08-06-watch-coordinator-infra-classification` task record), so the
classification is performed by the consumer. Scope: this is **post-coordinator
diagnosis**, run once on a delivered `settled-blocked` report after the watch
loop has ended. It adds nothing to the coordinator's own probe procedure —
the coordinator's ban on supplementary thread queries and second pagination
paths governs the polling loop, not what an operator reads afterwards. Never
guess from the check name.

Classify in this order:

1. **Read the reason code and check conclusions from the probe's own
   evidence.** The current eligibility script already names the thread
   case: an all-green-but-BLOCKED PR triggers its own thread collection and
   returns `merge_blocked_conversation` (unresolved threads, with a
   `reviewThreads` evidence block) or `merge_blocked_review` instead of the
   generic code (`scripts/sd-ai-command-pack-pr-eligibility.py:706-721`).
   A specific code is the answer; act on it directly. The result also
   carries `checks.items` — every CheckRun `conclusion` and StatusContext
   `state` from the script's bounded fail-closed pager. Non-blocking
   conclusions are `SUCCESS`, `SKIPPED`, and `NEUTRAL` (`:474-480`); treat
   only items outside that set as red. (`gh pr checks <N>` is a
   human-readable cross-check; it renders the same facts as
   `pass`/`skipping`.)
2. **Generic `merge_state_not_clean` with all checks non-blocking: fall back
   to a manual thread query.** This is the legacy/degraded path — an older
   probe, or one whose thread collection failed (the historical PR #157
   report predates the specific codes: six green checks, `threads: null`,
   five unresolved Copilot threads discoverable only by hand; an absent
   thread list is never "no threads"). Run
   `gh pr view <N> --json mergeStateStatus,mergeable,reviewDecision` plus
   the unresolved-thread count:
   `gh api graphql -f query='query{repository(owner:"<owner>",name:"<repo>"){pullRequest(number:<N>){reviewThreads(first:100){pageInfo{hasNextPage endCursor}nodes{isResolved}}}}}'`
   — paginate with `after: <endCursor>` while `hasNextPage` is true, so the
   count covers every thread; a nonzero `isResolved: false` count with
   `mergeable: MERGEABLE` is **unresolved threads**: resolve or rebut them;
   no retry, no code change. An undercounted page must not be read as "not
   threads".

If instead some check is red, split infrastructure from a real failure with
job-step evidence: `gh api repos/<owner>/<repo>/actions/jobs/<id>` returns
each step's name, conclusion, and timestamps; the error *text* lives in the
separate logs endpoint (`gh api repos/<owner>/<repo>/actions/jobs/<id>/logs`)
or the run's web UI, not in the jobs payload.

- **Infrastructure**: no test step ever ran — the `Set up job` step failed
  or the job died with `steps: []`, and several lanes ended at one identical
  duration while any lane that acquired a runner passed. The PR #155
  signature was both, across two attempts: four lanes at an identical
  `15m2s` (cancelled, zero steps) with the runner-acquiring lane passing at
  `8m51s`, and `Set up job` failures whose logs read `Service Unavailable` /
  `Failed to resolve action download info`. Either form means zero test
  evidence about the code. One retry; a second identical signature is the
  answer.
- **Real failure**: a test or lint step executed and failed. Retrying is
  never the fix; fixing without reading the failure is how an
  infrastructure-red gets "fixed" into new code that was never the problem.

Fail toward blocking, explicitly: classification selects the *response*,
never the merge. Misread a real failure as infrastructure and the cost is one
wasted retry that ends red and still blocks. Misread infrastructure as a real
failure and the cost is time spent reading logs that show no executed step.
Neither direction can turn a red suite green: merging stays behind the
housekeeping gate's own atomic eligibility recomputation, which none of this
classification feeds.

#### A review that exists is not a review that happened

An automated reviewer can post a review whose entire body is `Copilot
encountered an error and was unable to review this pull request. You can try
again by re-requesting a review.` It is a real review object: the reviews array
grows, `state` reads `COMMENTED`, and it carries zero inline comments. Nothing
was reviewed.

Nothing in the merge-readiness signals contradicts it. `mergeStateStatus:
CLEAN` means no unresolved threads and no failing checks; it does not assert
that a review happened. A poller that waits on `reviews | length` therefore
reports a cleared review loop at exactly the moment the reviewer failed -- the
same species of error as reading an absent thread list as "no threads".

Poll the body, not the count, and classify it:

```bash
gh pr view <N> --json reviews \
  --jq '[.reviews[]|select(.author.login|test("copilot"))]|last|.body'
```

- contains `unable to review` -> the reviewer errored. Not a verdict; re-request.
- contains `generated no new comments` -> reviewed, nothing found.
- contains `generated <n> comment` -> findings to read and answer.

A reviewer that fails repeatedly is the blocker, not the gate: by the rule
above, a second identical failure signature is the answer. Report it and let
the maintainer decide, rather than dropping the review requirement quietly. On
2026-08-17 three consecutive requests on PR #248 returned only the error
string; it was merged without a review by explicit maintainer decision, and the
pull request carries a comment saying so. An unobtainable review is a stated
gap in the record, never an implied pass.

### A stopped work-loop run is inert, not pending cleanup

`sd-work-backlog`'s status helper reports `recovery.reasonCode: run_stopped`
for any run left in `status: stopped`, and that code routes to a recovery
reference. On a run whose `branch`, `head`, `prNumber`, and `lastShippedSha`
are all null and whose lock is absent, there is nothing to reconcile and no
cleanup to perform. The recorded `task` may still name the last selected task,
which may since have been parked, and that pointer is equally inert.

The proof is in the helper's own `start` path: it resumes an existing run only
when `state["status"] in {"active", "paused"}`
(`scripts/sd-ai-command-pack-work-loop.py:2864`). A `stopped` run falls through
to `new_state(...)`, so the next invocation begins a fresh run and never
resumes into the stale task. Read that branch before treating a stopped run as
an anomaly; the status collector already agrees, printing a bare `none` under
its `==> Anomalies` header.

This is documented here rather than in the recovery reference itself because
`references/run-recovery.md` is installed from the sd-ai-command-pack (see
`.sd-ai-command-pack/manifest.json`), so an edit in this repository would be
overwritten by the next pack refresh. Fixing it at the source is an upstream
change to that pack, not a change to this one.

### Merge-boundary evidence after housekeeping deletes the branch: two steps

Local-only record (format per "Vendored-Artifact Ownership And Upstream
Route" below; task `08-06-work-loop-shipped-sha-after-branch-delete`):

1. **Owning pack**: sd-ai-command-pack.
2. **File**: `scripts/sd-ai-command-pack-work-loop.py` (`install: "always"`),
   with the documented call shape in `.agents/skills/sd-work-backlog/SKILL.md`
   (`install: "always"`) and `.claude/skills/sd-work-backlog/SKILL.md`
   (no `install` key = `if-anchor-exists`) — all pack-vendored.
3. **Behaviour**: the one-shot merge-boundary evidence call the skill
   documents fails after housekeeping deletes the merged branch — the branch
   flip requires `lastShippedSha` in the same call, but the ancestry check
   resolves the deleted branch to `None` and falls back to the stale
   remembered head, so every one-shot ordering is rejected. Same helper:
   `LEGAL_TRANSITIONS` gives `selected` no route back to `inventory`, so the
   skill's documented pre-mutation `skip current` has no sanctioned
   implementation.
4. **Upstream**: relayed as platypeeps/sd-ai-command-pack#404 (issue, not a
   pull request). No upstream PR was opened; a PR needs explicit per-PR
   approval.

Operator procedure that works today, from a green or amber ledger — both
steps are `evidence` subcommand calls, in this exact order:

```bash
# 1. same-phase descendant update: head only, nothing else
bash ~/.agents/bin/sd-ai-command-pack-toolchain.sh run-python -- \
  ~/.agents/bin/sd-ai-command-pack-work-loop.py evidence --repo . \
  --run-id <id> --head <final feature commit>
# 2. verified merge-boundary flip: all five evidence flags in one call
bash ~/.agents/bin/sd-ai-command-pack-toolchain.sh run-python -- \
  ~/.agents/bin/sd-ai-command-pack-work-loop.py evidence --repo . \
  --run-id <id> --branch main --head <merge commit> --base-branch main \
  --pr-number <N> --last-shipped-sha <final feature commit>
```

Step 1 refreshes the remembered head so step 2's fallback tip resolves to a
commit that actually has the shipped SHA as an ancestor. Do not use
`reconcile` for this: a run already holding a blocked recovery checkpoint
from rejected `reconcile` calls must satisfy reconcile's
complete-recovery-evidence requirement instead — partial `evidence` updates
do not clear a recovery checkpoint.

### Planning-mode finalization stranded by a post-finalization review fix

**Failing shape.** An `sd-ship until=merge` chain under **planning-mode**
finalization stops at Stage 4 with `bundle_scope_invalid` ("finalization delta
contains a non-bookkeeping path") when a remote review — typically the Copilot
auto-reviewer, since this repository's review router is absent — lands after
Stage 2b's journal commit and its fix touches an authored path:

```
81fc2cb fix(docs): ...          <- review fix, authored spec path
a63a871 chore: record journal   <- Stage 2b planning finalization
392954f docs: ...               <- captured finalization base
```

Stage 4 must recompute the planning receipt from the **captured base**
(`.agents/skills/sd-ship/SKILL.md:179-186`), the fix commit put an authored
path inside that range, and Stage 4 is forbidden from invoking any finish-work
flow — so no receipt the chain may compute is valid, and the chain stops with
the validator's report. The trigger is review *timing*, not content; the trap
recurs whenever a review lands post-finalization. It is planning-mode-specific:
completion mode recomputes with base equal to the current head, whose empty
delta activates the post-archive-review-successor recovery for an eligible
successor.

**Sanctioned recovery — never restart the chain.** The in-chain rerun is
forbidden (`sd-ship` runs finish-work exactly once per chain, and a rerun
under planning finalization could archive a deliberately open task); a
**fresh** `sd-finish-work` invocation outside the stopped chain is not — the
do-not-rerun rule binds the chain, not the operator. In order:

1. Confirm the fix commits are pushed and checks are green on the PR branch.
2. Run a fresh `sd-finish-work`. It re-captures the base at the current tip
   and writes a second journal session. When its delta is exactly the one new
   journal session plus its sibling `index.md`, the receipt validates as
   `evidence.planningSubtype: journal-only-recovery` (that key lives under
   `evidence` in the validator JSON, not top-level). The recovery has
   eligibility bounds — exactly one newly completed session, bounded
   published single-parent cited commits — so a failed recovery recomputation
   is a real blocker to report, not a retry candidate.
3. Push the fresh journal commits, wait for green, then invoke
   `sd-housekeeping` directly with the fresh receipt via
   `--finish-work-receipt`. Housekeeping remains the sole merge authority; the
   stopped `sd-ship` chain is never resumed.

**Explicitly excluded.** A post-finalization fix that touches only bookkeeping
paths does not need this recovery: the existing captured-base recomputation
already passes the path-scope check there (later validator checks — file
modes, whitespace, journal structure — can still fail it for independent
reasons). Observed end-to-end on PR #157 (2026-08-06), where the merge
succeeded only after the fresh invocation.

**Local-only record** (per the four-field format in "Vendored-Artifact
Ownership And Upstream Route"):

- Owning pack: sd-ai-command-pack.
- Files: `.agents/skills/sd-ship/SKILL.md` and
  `.agents/skills/sd-finish-work/SKILL.md` (Registry B, `kind: skill`,
  `install: "always"`); `.claude/skills/sd-ship/SKILL.md` and
  `.claude/skills/sd-finish-work/SKILL.md` (Registry B, `kind: skill`,
  `anchor: ".claude"`, if-anchor-exists); and
  `scripts/sd-ai-command-pack-review-preflight.mjs` (Registry B,
  `kind: script`, `install: "always"`).
- Behaviour: Stage 4's planning-mode moved-head recomputation reuses the
  captured base and forbids in-chain finish-work, so a post-finalization
  authored-path fix leaves the chain no valid receipt and the stopping report
  names only the validator failure, not the recovery route.
- No upstream PR was opened; relay issue:
  <https://github.com/platypeeps/sd-ai-command-pack/issues/408>.

### task.json ends without a trailing newline: expected, do not hand-fix

Every `task.json` Trellis writes ends mid-line: `write_json`
(`.trellis/scripts/common/io.py:37`) writes
`json.dumps(data, indent=2, ensure_ascii=False)` verbatim, while the same
script family's `active_task.py:428` appends `"\n"` to an otherwise
identical call. A `\ No newline at end of file` marker on a `task.json`
diff is therefore expected machine output, not a defect. Do not hand-add
the newline: any later mutating `task.py` command that rewrites the file silently
reverts it (observed — four hand-corrected files on 2026-08-06, all
reverted by ordinary commands by 2026-08-07), producing a second
no-op-looking diff. No `.gitattributes` or `.editorconfig` rule papers over
this; that would mask the writer inconsistency at the diff layer.

Four-field record (task `08-06-task-json-trailing-newline`): owning pack —
upstream Trellis; file — `.trellis/scripts/common/io.py` (Registry A,
`.trellis/.template-hashes.json`); behaviour — `write_json` omits the
trailing newline that `active_task.py:428` appends, so hand edits render
two-line diffs where the expected no-newline marker becomes review noise,
and the fix is one character
(`+ "\n"`) with the `mkstemp`/`os.replace` atomicity, error handling, and
return contract unchanged; no upstream PR was opened — the proposal is
relayed as
[sd-ai-command-pack#413](https://github.com/platypeeps/sd-ai-command-pack/issues/413).

### task.py create seeds base_branch from the checkout: correct it before the source branch dies

**Behaviour (installed Trellis 0.6.7).** `task.py create` records whatever
branch is checked out as the new task's `base_branch`
(`.trellis/scripts/common/task_store.py:296-298`, written at `:325`). In this
repository's dominant flow — follow-up tasks created mid-ship-cycle from a
feature branch — that records a branch that will be deleted at merge. The
`or "main"` fallback is legacy: it fires only on empty output (detached HEAD,
or a discarded `git` failure) and hardcodes a name that may not be the
default.

**Upstream status.** Fixed in Trellis v0.6.8
(mindfold-ai/Trellis#399, merged PR #448): `create` resolves the repository
default branch (`origin/HEAD`) and takes an explicit `--base-branch` for
deliberate stacking. The fix reaches this repository only through a Trellis
upgrade and changes seeding for **new** tasks only. Until that upgrade, every
mid-cycle `create` here still seeds wrongly — a green sweep of stored values
is not evidence the defect is gone.

**Correction — command and deadline.** Correct with
`python3 ./.trellis/scripts/task.py set-base-branch <dir> <branch>`, never a
hand edit of `task.json`, and do it **before the source branch is deleted** —
in practice, inside the same ship cycle that created the task, where the
wrong value is still recognizable as the current feature branch.

**Detection today.** `create` and `start` stay silent. At PR time, the
preflight hard-gates a changed root-task record whose `base_branch` is not
the repository default (`validateTrellisRootTaskBaseBranch`,
`scripts/sd-ai-command-pack-review-preflight.mjs:3331-3354`, wired at
`:3159-3188`); child tasks are checked permissively against their parent
(`:3294-3328`), and the shape checks (`:3409-3420`) are guarded off while
`branch` is `null`. Consumption is narrow: `sd-create-pr` resolves the PR
base independently and never reads the field; `sd-finish-work` uses it only
as an inequality guard, which a stale value silently degrades to a no-op.

**The gate's version-conditioned trap.** The root gate's diagnostic
recommends `task.py set-meta <task-dir> base_branch_exemption "<reason>"`
(`:3353`). `set-meta` shipped in Trellis **v0.6.9** and is absent from the
installed 0.6.7 (and v0.6.8), so on this install the exemption is
unreachable through any sanctioned command — a deliberate stacked root base
cannot pass the gate without a hand edit until a ≥ v0.6.9 upgrade lands.

**Sweep check** (run after `git fetch --prune`, normalizing
`main`/`origin/main`/`remotes/origin/main` to one form): every active
`task.json` `base_branch` must name the repository default branch or carry a
documented stacked-base/exemption reason. Liveness against unpruned
`git branch -a` is not the check — cached remote-tracking refs vouch for
deleted branches.

**Local-only record** (per the four-field format in "Vendored-Artifact
Ownership And Upstream Route"):

- Owning pack: upstream Trellis for the seeding surface
  (`.trellis/scripts/common/task_store.py`, Registry A) and
  sd-ai-command-pack for the gate diagnostic
  (`scripts/sd-ai-command-pack-review-preflight.mjs`, Registry B,
  `kind: script`, `install: "always"`).
- Files: as above, each with its registry entry.
- Behaviour: pre-v0.6.8 `create` seeds `base_branch` from the checkout, and
  the pack's root-gate diagnostic recommends a Trellis ≥ v0.6.9 command
  without stating or checking that floor, leaving the exemption unreachable
  on this install.
- No upstream PR was opened; the seeding defect was already fixed upstream
  (Trellis v0.6.8 via #399/#448 — no duplicate filed); relay issue for the
  version-floor gap:
  <https://github.com/platypeeps/sd-ai-command-pack/issues/410>.

---

## Vendored Pack Lifecycle

> **Historical for this checkout since the thin conversion.** There is no
> vendored payload here any more: the executables, skills, and manual live in
> the machine install and this repository keeps only its pin, its prompts, and
> the layout resolver. A refresh updates the machine install, and the conflict
> class all three contracts below are about — an installer overwriting payload
> files tracked in this tree — cannot occur. Keep the section: a consumer that
> converts back, or one still fat, is governed by it, and the reasoning behind
> the `.bak` audit failure and the silent local-fork revert is what justifies
> the current shape. Read it as the fat-install contract, not as this
> checkout's procedure.

**On a fat install** the sd-ai-command-pack payload
(`scripts/sd-ai-command-pack-*`, `.claude/skills/sd-*`, `.agents/skills/sd-*`,
`docs/SD_AI_COMMAND_PACK.md`, `.claude/sd-ai-command-pack/`) is installed into
the consumer tree and vouched via `.sd-ai-command-pack/manifest.json` +
`provenance.json`. Three contracts, learned on the v0.64.3 → v0.64.32 refresh
(2026-08-09):

### Convention: refresh only from a clean pinned source

**What**: Run `install.py <target> --force --backup` from a worktree checked
out at a tag (or exact recorded clean commit) of the upstream repo — never
from a sibling checkout with uncommitted changes.

**Why**: Post-refresh provenance vouches that the consumer matches the
*source checkout*, whatever it contained. A dirty source launders uncommitted
upstream edits into vouched provenance. Record the tag/commit in the task.
Capture `--check --json` (structured) and `--dry-run` (per-file) before
forcing; a pre-refresh audit line "vouched file hashes match" proves every
conflict is an upstream-version difference, not local drift.

### Gotcha: installer `.bak` backups fail the structural audit

> **Warning**: `--backup` writes `<file>.bak` beside each overwritten target,
> and the very next `--check` fails with "pack-like file is not listed in
> installed targets: <file>.bak" for each one.
>
> Archive the `.bak` files elsewhere and remove them from the tree before
> re-running the audit. Git HEAD already holds every pre-refresh original, so
> `git checkout <pre-refresh-sha> -- <file>` is the durable restore path.

### Gotcha: a refresh silently reverts local forks of payload files

> **Warning**: Any locally committed edit to a vendored payload file is
> overwritten without a distinct notice — it surfaces only as one more
> "conflict" row in the dry run. The v0.64.32 refresh reverted local commit
> `bc01bc2` (`_resolve_check` in `scripts/sd-ai-command-pack-review.py`) and
> stranded the local `test_review_coordinator.py` regression tests (since
> deleted) pinning the removed symbol.
>
> Before any refresh, `git log --oneline -- <payload paths>` for local
> commits, and review the refresh diff as a unit for reverted local fixes.
> Local tests that pin vendored internals go down with the fork they pin;
> prefer upstreaming the fix (see `08-07-vendored-artifact-upstream-route`).

---

## Vendored-Artifact Ownership And Upstream Route

Eight tasks independently re-derived the same three facts: which registry owns
an installed file, what a run may do about a defect in one, and what it writes
down when it takes the local-only route. This section records all three once.
Canonical membership list: the table in
`.trellis/tasks/archive/2026-08/08-07-vendored-artifact-upstream-route/prd.md`.

### 1. Ownership lookup: given a repository-relative path

Consult the two ownership registries in this order; `provenance.json` is not
one of them (see step 3). Registry B is tracked in the repository; Registry
A's hash file is **gitignored and machine-local** (`.gitignore:87`, written
by the Trellis installer), so a clean checkout does not have it — its absence
means "no Registry A evidence on this machine", never "not a member". Both
lookups are runnable as written:

```bash
P=<repository-relative path>
# Registry A: upstream Trellis (machine-local file; guard for absence)
if [ -f .trellis/.template-hashes.json ]; then
  jq --arg p "$P" '.hashes | has($p)' .trellis/.template-hashes.json
else
  echo "registry A unavailable (.trellis/.template-hashes.json absent)"
fi
# Registry B: sd-ai-command-pack
jq --arg p "$P" '[.files[] | select(.target==$p)] | first // "absent"
                 | if . == "absent" then . else {kind, install, anchor} end' \
  .sd-ai-command-pack/manifest.json
```

1. **Registry A hit** (`.trellis/.template-hashes.json`, `hashes` key): the
   file is installed from upstream Trellis. Vendored — do not edit. If
   Registry B *also* matches, the file is dual-owned (step 4).
2. **Registry B hit** (`.sd-ai-command-pack/manifest.json`, `files[].target`):
   classification depends on two entry fields, and the **default matters
   more than the explicit values** — an entry with no `install` key is
   `install: "if-anchor-exists"` (`installer/manifest.py:87`,
   `IF_ANCHOR_EXISTS` in `installer/registry.py:590`): 694 of the 776 entries
   in the installed `0.64.33` manifest, the majority case. Anchor gating
   affects only whether the file is installed at all; on refresh it is
   overwritten exactly like `install: "always"` — only `if-not-exists`
   targets are preserved (`installer/fileops.py:300`).

   | Entry shape | Ownership | Editable locally? |
   | --- | --- | --- |
   | `install: "always"` | pack-vendored | No — refresh overwrites |
   | no `install` key (= `if-anchor-exists`) | pack-vendored | No — refresh overwrites |
   | `install: "if-not-exists"` | repo-owned after first install | Yes — refresh preserves |
   | `kind: "managed-block"` | pack owns the marker-bounded block only | Outside the block, per the file's other registry |
3. **`provenance.json` is drift evidence, not an ownership decider.** Its
   per-file hashes tell you whether an installed file still matches what the
   pack shipped; membership and editability come from the manifest entry.
4. **Both registries match: dual-owned.** Worked example, the only current
   instance: `.github/copilot-instructions.md` is recorded as a whole-file
   hash by Trellis (Registry A) while the sd-pack's `kind: "managed-block"`
   entry (anchor `.github`) legitimately appends its own marker-bounded
   block. The Trellis hash therefore reports **permanent drift that is not
   drift** — classify that hash mismatch as expected, do not investigate it
   as tampering, and edit neither the block nor the Trellis-hashed body.
5. **Neither registry matches: repo-owned.** Edit freely under normal review.
   This file (`.trellis/spec/backend/quality-guidelines.md`) is the standing
   example.
6. **Repo-owned does not mean nobody upstream wrote it.** `AGENTS.md` is the
   sharp case: its entire body is a Trellis-generated
   `<!-- TRELLIS:START -->`…`<!-- TRELLIS:END -->` block, yet it classifies
   repo-owned because Trellis writes no receipt for it and
   `.github/trellis-provenance.json` covers only the platform directories plus
   `.gitignore`. The registries say "edit freely"; the file's own closing line
   says "Edits outside this block are preserved; edits inside may be
   overwritten by a future `trellis update`." Both are true, and the second is
   the operative one — a repo-owned file can still carry an upstream-managed
   region. Put repo content **below the closing marker**, never inside it, and
   guard it, because no receipt will notice when a refresh eats an in-block
   edit. `AGENTS.md`'s routing section and `tests/test_agent_routing.py` are
   the worked example; the pack's own `.github/copilot-instructions.md`
   managed block is the same shape with a receipt behind it.

Verified against six real files with known, differing classifications — each
lookup above yields exactly this row:

| File | Classification |
| --- | --- |
| `scripts/sd-ai-command-pack-review.py` | Registry B, `install: "always"` — vendored |
| `.claude/rules/sd-planning-adversarial-review.md` | Registry B, no `install` key (`if-anchor-exists`) — vendored |
| `.prism/rules.json` | Registry B, `install: "if-not-exists"` — repo-owned after first install |
| `.github/copilot-instructions.md` | Registry A + Registry B `managed-block` — dual-owned, drift expected |
| `.trellis/scripts/common/task_store.py` | Registry A — upstream-Trellis vendored |
| `.trellis/spec/backend/quality-guidelines.md` | no registry — repo-owned |

Getting the lookup wrong is costly in both directions: treating a repo-owned
file as vendored abandons a fix that was always allowed; treating a vendored
file as repo-owned produces an edit the next pack refresh silently reverts
(see the refresh gotcha in Vendored Pack Lifecycle above).

### 2. Disposition rule for a defect in a vendored file

Four parts, each load-bearing:

1. **Local-only is a legitimate terminal outcome for a *record*** — guidance,
   an operator procedure, a documented constraint — not a partial failure or
   a lesser ending. Most vendored-defect tasks end here.
2. **For a *code change*, local-only is not terminal**: an edit committed
   into a vendored file survives only until the next pack refresh, which
   reverts it silently (observed: local commit `bc01bc2` reverted by the
   v0.64.32 refresh). A local fork is a liability with an expiry date, never
   a resting state.
3. **Do not edit a vendored file in place as a workaround**, whether it sits
   inside `.trellis/` or outside it.
4. **An upstream pull request requires explicit per-PR approval.** The
   autonomous run-level authority excludes it; this section documents the
   route and does not grant, presume, or create any standing approval.

### 3. The local-only record: format and worked example

When a task takes the local-only route, the unproposed upstream change must
stay discoverable. Record all four fields, in the task's disposition and in
whatever guidance section carries the constraint:

1. **Owning pack** — which upstream owns the file (sd-ai-command-pack, or
   upstream Trellis).
2. **File** — the repository-relative path, with the registry entry that
   classifies it.
3. **Behaviour** — the defect or missing behaviour, precisely enough that an
   upstream proposal could be drafted from the record alone.
4. **No upstream PR was opened** — stated explicitly, so a later reader knows
   the proposal was never made rather than made-and-lost.

Worked example, each field filled in (the full record is this file's
"Scenario: SD Status Pack-Freshness Signal" section):

1. Owning pack: sd-ai-command-pack.
2. File: `scripts/sd-ai-command-pack-status.py`, manifest entry
   `install: "always"`.
3. Behaviour: local-mode `collect_versions` resolves no target pack version
   in a consumer repository, so a stale installed pack reports
   `packState: "installed"` with no anomaly, follow-up, or recommendation.
4. No upstream PR was opened; upstream approval was not sought. The section
   heading records the disposition as "local-only guidance".

Filed upstream relays (approved per-PR, the other side of the route) are
precedented in the 08-07 task's relay log: platypeeps/sd-ai-command-pack#397,
#398, #399 — each an issue reporting a defect for upstream to fix.

A relay may also carry the fix. platypeeps/sd-ai-command-pack#417 is the first:
it implements the change in the upstream repository, with its regression tests
and the release-payload bookkeeping upstream requires, rather than describing
the defect and waiting. Use it when the defect is understood well enough to fix
and the upstream repository is available to work in; use the issue form when it
is not. Either way the per-PR approval in part 4 above is required first, and
the originating task records the route in its own `disposition.md`
(`08-10-review-check-cache-pr-body` for #417).

---

## Code Review Checklist

- Is the change made in the canonical registry/template/module rather than a
  generated or duplicated surface?
- Are all paths constrained to the intended source/install roots?
- Does dry-run avoid mutation, and does apply reuse or revalidate its plan?
- Are user-modified files preserved by default?
- Do errors include actionable context without leaking sensitive contents?
- Do tests cover success, invalid input, conflicts, and compatibility state?
- If payload changed, are `manifest.json`, version, and `CHANGELOG.md` aligned?

---

## Scenario: Skill Family Registry And Generated Catalog

### 1. Scope / Trigger

- Trigger: adding, retiring, reordering, or reclassifying a shipped skill, or
  changing either generated skill catalog.
- Why: family metadata crosses the registry, canonical frontmatter, generator,
  README, tests, and manifest-order compatibility even though it does not alter
  installed paths or the manifest schema.

### 2. Signatures

```text
FAMILY_LABELS: dict[str, str]
FAMILY_DESCRIPTIONS: dict[str, str]
SKILLS: tuple[SkillInfo, ...]
SKILL_NAMES = tuple(skill.name for skill in SKILLS)
make generate
python .github/scripts/generate-skill-surfaces.py --check
<!-- SE_SKILL_CATALOG:START --> ... <!-- SE_SKILL_CATALOG:END -->
generated/references/skill-catalog.md
assert_generated_write_target(path: Path) -> None
_boundary_parts(path: Path) -> tuple[str, ...]
IN_PLACE_WRITE_NAMES = frozenset({"manifest.json", "README.md"})
python .github/scripts/check-release-payload.py --base <rev|auto>
check_single_version_step(repo: Path, merge_base: str) -> None
VERSION_HEADING_PATTERN = re.compile(r"^## (?P<version>\S+)")
```

`FAMILY_LABELS` order is public catalog order. `FAMILY_DESCRIPTIONS` must have
the same keys in the same order. `SKILLS` order remains canonical
manifest/install order, and grouping must not reorder generated manifest rows.

### 3. Contracts

- Every `SkillInfo.name` is non-empty, unique, `se-` prefixed, and backed by a
  flat `templates/skills/<name>/SKILL.md` directory.
- Every skill has exactly one family from Understand, Decide, Create,
  Coordinate, Operate, or Improve. Empty families remain valid: the compact
  README catalog omits them, while the bundled help catalog renders every
  family with its canonical outcome description.
- `SKILL_NAMES` is derived for compatibility; no consumer owns a second skill
  list.
- The source/generated boundary is a location rule, not a comment rule.
  `templates/` holds hand-edited sources only; every generated surface is
  written under `generated/`. The bundled catalog therefore lives at
  `generated/references/skill-catalog.md` and is registered in
  `GENERATED_REFERENCES` (repo-relative keys), while `SHARED_REFERENCES` keeps
  its `templates/skills/`-relative keys for authored references. Both fan out
  identically, so the split costs nothing at install time and buys one
  invariant: a registered `SHARED_REFERENCES` source that is missing from disk
  is unconditionally an error, with no generated-file exemption to weaken it.
- The catalog description comes from the already validated frontmatter parse.
  Markdown table pipes are escaped deterministically; descriptions are not
  duplicated in registry code.
- Generation computes and validates manifest, README, bundled help-catalog, and
  the generated `registry-snapshot.json` results before writing any of them. A
  later write failure rolls earlier surfaces back to their committed state.
  README content outside one ordered marker pair is preserved.
- Family-only metadata and catalog changes do not require a release bump only
  when every shipped payload path stays byte-identical. The gated surface is
  `templates/**`, `generated/**`, `installer/**`, `install.py`, and
  `manifest.json`. Because `FAMILY_DESCRIPTIONS` and `FAMILY_LABELS` live in
  `installer/registry.py` (gated), a family-description or family-label source
  edit does require a bump.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Empty skill name, family, or family description | Raise a registry `RuntimeError` before generation. |
| Family-description keys or order differ from family labels | Raise a registry `RuntimeError` before generation. |
| Unknown family | Raise a registry `RuntimeError` naming the skill and family. |
| Duplicate skill name, including cross-family membership | Raise a registry `RuntimeError`; never choose one row implicitly. |
| Missing, duplicate, or reversed README markers | Fail generation before either surface is written. |
| A registered `SHARED_REFERENCES` source is absent from `templates/skills/` | Raise a generation error naming the path; there is no exemption for generated sources, which are registered in `GENERATED_REFERENCES` instead. |
| A file under `templates/` carries the generator's do-not-edit marker | `test_no_generated_file_lives_under_templates` fails, naming the offending path. |
| The generator is asked to write any path with a `templates` component, whatever its format | `write_generated_surfaces` raises `GenerationError` before mutating anything. The marker walk cannot cover this: the marker is an HTML comment, so a generated `.json` or `.toml` under `templates/` carries no marker in any syntax. |
| The generator is asked to write outside `generated/` and outside `manifest.json`/`README.md` | `GenerationError`; generator output nobody would look for when reconciling drift is refused at the writer. |
| A degenerate write target reaches the guard — empty, bare name, option-like, or the filesystem root | `GenerationError` in every case. The guard performs no filesystem access at all, deciding purely from components, so the symlink, oversized-file, and TOCTOU arms of the path-filesystem matrix have no surface in it; that exposure lives in `atomic_write_text` and is unchanged. What the guard owes is a verdict on every shape a caller can reach it with. |
| A stray write is named `README.md` or `manifest.json` outside its configured path | `GenerationError`. The in-place surfaces are the two exact paths `MANIFEST_PATH` and `README_PATH`, not two basenames; matched on the name alone the boundary comes apart on the two commonest filenames in any repository. The comparison reads the module globals so the sandbox tests that patch both constants into a temporary tree still exercise the arm. |
| A write target reaches outside `generated/` through a `..` component | `GenerationError` before the boundary rules are consulted. A component check reads what was written, not where the OS lands, so `generated/../docs/stray.md` carries a `generated` component and would otherwise be accepted while the file appears in `docs/`. Nothing the generator builds contains a `..`; refusing is cheaper than proving that stays true. |
| The checkout sits under a host directory named `templates` or `generated` | The verdict is unchanged: `assert_generated_write_target` reads components relative to `ROOT` for any target inside the checkout, and only falls back to the whole path for the temporary trees the generator's own tests redirect output into. Nobody chooses where a clone lands, so no directory above the repository root may decide it. |
| Frontmatter description contains a table pipe | Escape it as `\|` in the README cell. |
| Manifest, README, bundled help catalog, or registry snapshot drifts | `--check` reports each drifted surface and exits nonzero. |
| Registry snapshot `schemaVersion` is a non-`int`, unsupported int, or the payload is malformed | Consumer raises `ReviewError` and fails closed. |
| The snapshot is absent in a first-party pack checkout (`name` in `FIRST_PARTY_REMOTES`) | Consumer raises `ReviewError` naming the expected path. A pack owes a snapshot, so its absence is a packaging defect. Keyed on the declared name rather than `owner_kind`, so a fork whose remote does not match cannot delete its snapshot and silently review with an empty registry. |
| The snapshot is absent in any other checkout | Consumer resolves an empty `RegistryData` and succeeds; skills report `Uncategorized`. Non-pack checkouts ship no registry at all, and the reviewer supports them. |
| The snapshot path crosses a symlink boundary, at the leaf or any parent | Consumer raises `ReviewError` and never opens the target, in every checkout including `repo-local`. Not conditional on pack identity: a symlinked path is a rejected input, not a packaging gap. |
| Family metadata edited at its source in `installer/registry.py` (`FAMILY_DESCRIPTIONS`, `FAMILY_LABELS`), or a change that alters `generated/registry-snapshot.json`, `manifest.json`, or any `templates/**`/`generated/**`/`installer/**`/`install.py` byte | The source and snapshot are shipped payload; the release gate requires a version bump and dated CHANGELOG heading. |
| A change that touches no shipped payload byte at all (no diff under `templates/**`, `generated/**`, `installer/**`, `install.py`, or `manifest.json`) | Manifest and changelog stay unchanged; release gate passes without a bump. |
| A branch bumps the version twice and stacks two `## <version> - <date>` headings | Release gate exits nonzero: the intermediate version never becomes a merge-base state, so the auto-tag workflow never tags it (this is how `0.53.0` was left untagged). Collapse into the one heading being released, or split into separate PRs. |
| A branch bumps the version but adds no new heading, adopting one pre-written on the base | Release gate exits nonzero; the entry must be written on the branch that releases it. |
| An already-shipped changelog entry's date is corrected | Not a release: the one-step check compares version tokens, not whole heading lines. |

### 5. Good/Base/Bad Cases

- Good: add one `SkillInfo` row with one valid family, run `make generate`, and
  receive a grouped README entry while flat installed targets remain stable.
- Base: rerun `make generate` with unchanged inputs and receive no file diff.
- Bad: hand-edit a catalog row, duplicate the description in the registry,
  move a skill under a family subdirectory, or add family fields to manifest
  rows.

### 6. Tests Required

- Registry tests pin family and description order, all valid identifiers,
  derived name order, prefix rules, and rejection of empty, unknown, or
  duplicate membership.
- Generator tests pin README grouping, all-family bundled-help output,
  frontmatter sourcing, version identity, pipe escaping, marker validation,
  independent drift reporting (including the registry snapshot), coordinated
  rollback (including a snapshot write failure), and patched temporary output
  paths.
- Consumer tests pin snapshot-only resolution: fail-closed `ReviewError` for an
  absent snapshot in a pack checkout, for a symlinked leaf and a symlinked parent
  directory, and for unsupported/mistyped `schemaVersion` and malformed
  payloads; plus an empty registry for a non-pack checkout. The symlink test
  proves the content was never consumed by paired arms -- identical bytes
  refused through a link and resolved as a regular file -- because an error
  message is not evidence about which files were read.
- One boundary test walks `templates/` from disk and fails on any file carrying
  the generator's do-not-edit marker. It enumerates rather than checking known
  paths, so it also catches a generated surface nobody thought to look for.
  Because that walk can only see Markdown, a second pair of tests drives
  `write_generated_surfaces` directly: a `.json` target under `templates/` and
  a target outside `generated/` must both raise before anything is written, and
  the accepted set (both in-place surfaces plus any `generated` component,
  including a redirected temporary tree) must still pass. A third test patches
  `ROOT` to a checkout nested under a host directory named `templates` and then
  one named `generated`, pinning that neither inverts the verdict, and a fourth
  drives a `..` traversal through `generated/`. That one is the only guard test
  whose write reaches the filesystem when it regresses, so it cleans the target
  up rather than leaving the next run to trip over it. Sandbox
  fixtures place generated surfaces at their real relative paths for the same
  reason — a fixture parking one at the tree root would test a shape the
  generator never produces.
- Release-gate tests pin the one-version-step rule from both sides: a branch
  stacking two headings fails, a branch collapsing its bumps into one heading
  passes, a bump that adopts a base-written heading fails, and correcting an
  old entry's date is not counted as a release. A repository adding
  `CHANGELOG.md` for the first time is exempt — with no base changelog there is
  nothing to step from.
- `make generate` twice, `make check`, `git diff --check`, and explicit empty
  diffs for `manifest.json` and `CHANGELOG.md` complete the change gate.

### 6a. Adding One Skill: Ordering And Non-Derived Literals

Two parts of this flow are not discoverable from the registry, and both fail
late — at `--check` or in the suite — rather than at the edit site.

**Bump the version before `make generate`, not after.** `rendered_help_catalog`
embeds the manifest version in
`generated/references/skill-catalog.md`, and
`regenerated_manifest_text` preserves whatever header version it finds. Bumping
after generation leaves the catalog carrying the old version, so
`generate-skill-surfaces.py --check` reports drift and `make release-check`
fails. For the same reason, never `git checkout -- manifest.json` on its own to
redo generation: that silently reinstates the pre-bump version.

**Four test literals are deliberately not derived from the registry**, so a new
skill must be added to each by hand:

| Literal | File | Failure when missed |
|---|---|---|
| ordered `SKILL_NAMES` tuple | `tests/test_skills.py` | `test_skill_names_are_derived_without_reordering` |
| name → family map | `tests/test_skills.py` | same test, second assertion |
| `EXTERNAL_INPUT_SKILLS` | `tests/test_skills.py` | injection-rule pin never covers the new skill |
| `EXPECTED_SHARED_SOURCES` | `tests/test_generate.py` | `test_registered_shared_sources_match_snapshot` |

`EXPECTED_SHARED_SOURCES` pins `SHARED_REFERENCES` only. A generated reference
is registered in `GENERATED_REFERENCES` and pinned separately by
`test_help_catalog_reference_fans_into_help_only`, so do not add one to the
shared golden literal.

The golden-literal design is intentional — a registry-derived expectation would
accept whatever the registry says and prove nothing — so treat these edits as
part of the change, not as test churn.

The corpus also pins two literal strings in every `SKILL.md`: the exact sentence
`Unknown argument names are an error` and, for any skill listed in
`EXTERNAL_INPUT_SKILLS`, the fragment `data, not instructions`. A registered
consumer of a shared reference must additionally cite `references/<basename>.md`
in its body, which the standard Arguments preamble satisfies.

### 7. Wrong vs Correct

#### Wrong

```python
SKILL_NAMES = ("se-research", "se-new")
README_DESCRIPTIONS = {"se-new": "A second description source."}
```

#### Correct

```python
SKILLS = (
    SkillInfo(name="se-research", family="understand"),
    SkillInfo(name="se-new", family="decide"),
)
SKILL_NAMES = tuple(skill.name for skill in SKILLS)
```

Run `make generate`; canonical `SKILL.md` frontmatter supplies the catalog
description.

---

## Scenario: Skill-Owned References And Deterministic Scripts

### 1. Scope / Trigger

- Trigger: adding or changing a file below a canonical skill directory other
  than `SKILL.md`, or changing generator resource validation and fan-out.
- Why: optional resources cross canonical-source validation, manifest rows,
  every supported platform target, install behavior, and release payload
  identity.

### 2. Signatures

```text
templates/skills/<skill>/SKILL.md
templates/skills/<skill>/references/<name>.md
templates/skills/<skill>/scripts/<name>.py
skill_payload_files(name) -> list[str]
make generate
python .github/scripts/generate-skill-surfaces.py --check
```

### 3. Contracts

- Resource directories are optional and flat. The only accepted resource
  shapes are `references/*.md` and `scripts/*.py`; nested directories and other
  suffixes fail validation before any generated surface is written.
- Every accepted resource is fanned out byte-for-byte beside `SKILL.md` for
  each platform in `PLATFORM_REGISTRY`, with deterministic ordering and a
  manifest row using the skill's normal scope and anchor.
- References hold conditional detail that is directly reachable from the skill.
  Scripts hold bounded deterministic work such as parsing, normalization,
  validation, hashing, inventory, or stable transformation. Judgment, dialogue,
  approvals, and mutation authority remain explicit in `SKILL.md`.
- Bundled scripts should be Python 3.10-compatible and standard-library-first.
  Their user-facing contract defines inputs, outputs, failure behavior, side
  effects, portability, idempotence or dry-run behavior, and tests.
- Adding or changing a resource changes shipped payload bytes and therefore
  requires a manifest version bump and matching changelog entry.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Flat `references/*.md` or `scripts/*.py` file | Validate and fan out to every declared platform. |
| Nested resource directory or unsupported suffix | Fail generation with the unexpected path; write no partial surfaces. |
| Resource exists but is absent from a platform manifest target | `--check` reports drift and exits nonzero. |
| Script requires an undeclared runtime dependency | Reject the design or document and validate the dependency before shipping. |
| Script performs semantic judgment or exceeds caller authority | Keep that operation in the skill; do not extract it. |
| Resource payload changes without version/changelog alignment | Release gate fails. |

### 5. Good/Base/Bad Cases

- Good: move repeated JSON inventory logic into a read-only, standard-library
  script with stable JSON output, focused failure tests, and direct invocation
  from the skill.
- Base: keep a short one-off judgment instruction in `SKILL.md`; no helper is
  created because scripting adds more maintenance than reliability.
- Bad: add a nested helper directory below the skill's scripts resource, ship
  an executable that silently edits files, or move user approval logic into
  code to reduce prompt length.

### 6. Tests Required

- Generator tests accept and fan out each allowed resource type to every
  platform and reject nested directories, wrong suffixes, and unregistered
  files without partial writes.
- Skill-specific tests pin the helper's deterministic output, invalid-input
  behavior, boundary protections, and read-only or dry-run guarantees.
- Run the helper in an isolated install and assert that every declared platform
  receives the same payload bytes and no unsupported frontmatter is introduced.
- Run `make generate` twice, `make check`, the release payload/version gate, and
  `git diff --check`.

### 7. Wrong vs Correct

#### Wrong

```text
templates/skills/se-example/scripts/lib/decide.py
# The script chooses whether the user-approved action is safe and performs it.
```

#### Correct

```text
templates/skills/se-example/scripts/inventory.py
# The script validates bounded inputs and emits stable, read-only JSON facts.
# SKILL.md interprets the facts and retains approval and mutation decisions.
```

---

## Scenario: Decision Skill Evidence And Authority Boundary

### 1. Scope / Trigger

- Trigger: adding or changing a skill that recommends one option, scores a
  choice, or turns evidence into user-specific judgment.
- Why: recommendation language can hide assumptions, upgrade weak evidence,
  blur neutral comparison with decision authority, or imply permission to act.

### 2. Signatures

```text
question=<bounded choice>
options=<two or more known alternatives>
criteria=<comparison axes>
constraints=<hard limits>
evidence=<authorized sources>
format=brief|memo
```

The final report exposes the decision, option comparison, tradeoffs,
confidence, reversibility, missing evidence, next action, sources, and
assumptions.

### 3. Contracts

- Decision work starts from at least two known options. Candidate discovery,
  open research, supplied-corpus synthesis, neutral comparison, and execution
  planning remain separately owned workflows.
- Hard constraints are evaluated before preference criteria and cannot be
  hidden inside an aggregate score.
- Sourced fact, inference, assumption, and judgment remain visible. Unknown
  evidence stays unknown and weak evidence is never normalized upward.
- Use only user-supplied weights or clearly labeled provisional assumptions;
  do not invent scores or numeric precision.
- Stress-test the leading option against the strongest counterargument and
  state what would change the recommendation.
- Recommendation skills are read-only. A choice never grants authority to
  purchase, message, schedule, publish, modify, or otherwise execute it.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Fewer than two known options | Ask for another option or route to candidate discovery. |
| Materially ambiguous goal or constraint | Stop for clarification before evaluating. |
| Missing criteria | Derive only from stated goals and label them provisional. |
| Constraint disqualifies an option | Keep the option visible with the disqualification reason. |
| Evidence is missing or asymmetric | Mark the affected cells unknown and lower confidence. |
| No defensible winner | Return an explicit no-decision result and the evidence needed. |
| User asks to act on the choice | Require a separate request and the relevant action authority. |

### 5. Good/Base/Bad Cases

- Good: compare known options on one consistent frame, apply constraints first,
  expose assumptions, challenge the leading option, and recommend with
  calibrated confidence and reversal conditions.
- Base: evidence is insufficient, so the report makes no recommendation and
  names the smallest evidence-gathering step.
- Bad: silently discover a preferred option, invent weights, turn unknowns into
  zeros, present judgment as fact, or execute the recommendation.

### 6. Tests Required

- Pin the unknown-argument stop rule, prompt-injection boundary, read-only
  authority, and explicit sibling-workflow routing.
- Pin the counterargument and recommendation-change conditions.
- Pin every required final-report field and the distinction between unknown,
  assumption, inference, and judgment.
- Run focused skill/generator tests, `make generate`, `make check`, and the
  release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
Option A scores 87 and wins. I will purchase it now.
```

The score has no owned weighting contract, uncertainty is hidden, and the
recommendation is incorrectly treated as execution authority.

#### Correct

```text
Recommend Option A with medium confidence. Constraint X disqualifies B;
criterion Y remains unknown; evidence Z or a change in deadline would reverse
the recommendation. Next action: validate Y before committing.
```

The decision is explicit, evidence limits remain visible, reversal conditions
are testable, and execution is separate.

---

## Scenario: Project Status Evidence And Authority Boundary

### 1. Scope / Trigger

- Trigger: adding or changing a skill that reports progress, current state,
  blockers, risks, decisions, asks, or next actions for a project or objective.
- Why: status prose can turn activity into outcomes, hide missing or stale
  sources, invent ownership or dates, and imply authority to update or send.

### 2. Signatures

```text
project=<initiative or workstream>
objective=<intended outcome>
since=<date, duration, or last-status>
sources=<authorized project evidence>
audience=<intended readers>
length=short|standard
```

The final report exposes the reporting window, objective, confidence, outcomes,
activity, current state, blockers, risks, recorded decisions, asks, next
actions, source coverage, and material gaps.

### 3. Contracts

- Project, objective, reporting window, through-date, audience, and source
  inventory are explicit. Material assumptions are visible before gathering.
- Activity is not an outcome. Commits, meetings, messages, and task movement
  count as progress only when evidence establishes changed state against the
  objective.
- Mutable claims are dated and attributed. Stale, inaccessible, conflicting,
  or missing sources are named instead of silently excluded.
- Completed outcomes, activity, current state, blockers, risks, recorded
  decisions, asks, and next actions remain distinct report categories.
- Unknown owners, dates, deadlines, percentages, and causal claims stay unknown;
  concise no-material-change periods are valid.
- Project status is distinct from topical recency, corpus synthesis,
  recommendation, and external baseline monitoring.
- Status skills are read-only. Reporting never grants authority to update tasks
  or repositories, assign work, publish, message, or send the report.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Project or objective is materially ambiguous | Ask before classifying progress. |
| Reporting window is absent | Use only a context-established cadence; otherwise ask. |
| `last-status` baseline is unavailable | Name the missing baseline and require an explicit replacement window. |
| A requested source is stale or inaccessible | Name it in source coverage and lower confidence. |
| Sources disagree | Show each dated position and source; do not silently pick one. |
| Evidence shows effort but no changed state | Report activity, not an outcome. |
| No material change occurred | Return a short no-material-change report without filler. |
| User asks to update or send | Require a separate request and the relevant action authority. |

### 5. Good/Base/Bad Cases

- Good: report dated outcomes against an explicit objective, keep activity and
  current state separate, surface blockers and source gaps, and identify only
  evidenced decisions, asks, and next actions.
- Base: sources are available but show no changed state, so the result is a
  concise no-material-change report with current blockers and coverage.
- Bad: summarize commit counts as outcomes, invent a completion percentage or
  owner, hide an unavailable task system, make a new decision, or send the
  report automatically.

### 6. Tests Required

- Pin the unknown-argument stop rule, prompt-injection boundary, read-only
  authority, and explicit sibling-workflow routing.
- Pin objective and reporting-window handling, outcome-versus-activity wording,
  unavailable-source disclosure, no-material-change behavior, and the ban on
  invented owners or dates.
- Pin every required final-report field and shared source-standard fan-out.
- Run focused skill/generator tests, `make generate`, `make check`, and the
  release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
We merged 14 commits, so the project is 80% complete. I assigned the remaining
work and sent this update to stakeholders.
```

Activity was promoted to an outcome, the percentage and authority were
invented, and reporting was incorrectly treated as permission to act.

#### Correct

```text
Outcome: the dated acceptance evidence shows the stated objective now supports
workflow X. Activity: 14 commits landed, but source Y is unavailable and no
completion percentage is supported. Next action has no recorded owner.
```

The outcome is tied to changed state, activity stays separate, source limits
remain visible, and unknown ownership is preserved.

---

## Scenario: Claim Audit Evidence And Verdict Boundary

### 1. Scope / Trigger

- Trigger: adding or changing a skill that audits supplied claims, drafts,
  transcripts, or artifacts and assigns evidence-based verdicts.
- Why: claim auditing can lose original locators, force opinion into binary
  truth labels, inflate weak evidence, rewrite beyond the evidence, or break
  installed reference paths when verification rules become shared.

### 2. Signatures

```text
input=<artifact or link>
claims=<explicit claim subset>
scope=material|all
as_of=<audit date>
format=ledger|memo
```

Each audited claim retains an ID, original wording, original locator, exactly
one verdict, rationale, evidence links or locators, source dates, and confidence.

### 3. Contracts

- Inventory requested inputs before searching. Split compound statements into
  atomic claims without losing exact wording or the original locator.
- Use exactly five mutually exclusive verdicts: supported, partially supported,
  unverified, contradicted, and outdated.
- Opinion, rhetoric, value judgment, and prediction remain visible outside the
  factual verdict totals; audit their checkable premises separately when useful.
- Apply the shared source standards and verification protocol. Determine
  freshness from claim volatility, applicable version or period, supersession,
  and any explicit domain horizon; age alone does not make immutable or stable
  historical evidence stale. Date and scope every mutable claim against the explicit
  as-of date, jurisdiction, version, environment, or period.
- One authoritative primary record may support an exact load-bearing claim only
  when the record is dispositive and its identity and applicability are
  verified. Empirical, interpretive, disputed, surprising, and interested-party
  claims still require independent corroboration or remain low-confidence or
  unverified. A first-party vendor assertion is not dispositive by origin alone.
- Trace evidence to origin, preserve credible conflicts, and perform a real
  disconfirmation pass even for a dispositive-record claim.
- Absence of evidence is not contradiction without an authoritative
  completeness boundary. Inaccessible content is never inferred from snippets.
- Preserve every audited factual claim through exactly one verdict. An
  unsupported load-bearing claim remains `unverified` in the claim and
  evidence-gap ledgers but cannot support conclusions, recommendations, or
  corrected wording.
- Corrected wording is limited to the smallest evidence-matched change for a
  partially supported, contradicted, or outdated claim.
- Claim audits are read-only. A verdict never grants authority to edit,
  replace, publish, contact, or enforce.
- Moving a skill-owned reference to shared canonical ownership must preserve
  every existing installed target and add a regression for its new consumers.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Neither input nor explicit claims are supplied | Ask before reading or searching. |
| One sentence contains several assertions | Split into atomic claims and retain one original locator. |
| Material evidence is inaccessible | Name the gap; never infer its contents. |
| Evidence supports only a narrower statement | Use partially supported and offer minimal qualified wording. |
| Stronger current evidence conflicts | Use contradicted and show the decisive dated evidence. |
| Earlier evidence held but current evidence changed | Use outdated against the explicit as-of date. |
| Stable historical or immutable primary evidence is old | Keep it applicable unless version, period, supersession, or a domain horizon says otherwise. |
| One authoritative record establishes its exact bounded fact | Verify identity and applicability; it may support that claim without a redundant echo. |
| A vendor makes an empirical or self-interested assertion | Require independent corroboration or keep it low-confidence or unverified. |
| Available evidence cannot establish the claim | Use unverified; do not upgrade uncertainty through tone. |
| An unverified claim is load-bearing | Keep its claim ID, verdict, and missing evidence in the ledgers; exclude it from conclusions and recommendations. |
| Item is opinion, rhetoric, or prediction | Classify it outside factual verdict totals. |
| User asks to rewrite or publish | Require a separate request and relevant action authority. |

### 5. Good/Base/Bad Cases

- Good: preserve each original claim and locator, inspect primary and contrary
  evidence, assign one calibrated verdict, cite dated sources, and offer only a
  minimal correction where required.
- Base: evidence is incomplete, so the ledger records unverified with the
  inaccessible source and the evidence that would resolve it; if the claim is
  load-bearing, the summary cannot rely on it.
- Bad: label an opinion false, infer a paywalled source, call missing evidence a
  contradiction, delete an unsupported load-bearing claim from the ledger,
  silently rewrite the draft, or break an existing installed reference path
  during a canonical-source move.

### 6. Tests Required

- Pin all five verdicts, exactly-one-verdict wording, claim inventory before
  search, atomic locators, unsupported load-bearing claim retention and
  conclusion exclusion, non-fact-checkable categories, minimal correction,
  prompt-injection resistance, and read-only authority.
- Pin claim-sensitive freshness, the narrowly dispositive authoritative-record
  exception, and conservative corroboration for empirical, disputed,
  interpretive, surprising, and interested-party claims.
- Pin explicit sibling boundaries from open research and corpus synthesis.
- Pin every required final-report field and both shared reference citations.
- When a reference source moves, assert the canonical shared source plus every
  old and new installed target across supported platforms.
- Run focused skill/generator tests, `make generate`, `make check`, and the
  release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
The paragraph is false. I rewrote it and published the correction; the
paywalled source probably agrees.
```

The claims were not split, no evidence or locator is traceable, inaccessible
content was invented, and auditing was treated as action authority.

#### Correct

```text
C-03 at paragraph 4 is partially supported: the primary source supports the
narrower dated statement, while the broader quantity is unverified. Suggested
minimal correction: replace only that quantity; no source file was changed.
```

The original claim remains traceable, evidence strength controls the verdict,
the correction is bounded, and execution stays separate.

---

## Scenario: Installed Skill Review Inventory

### 1. Scope / Trigger

- Trigger: changing `se-review-skills` discovery, installed-copy ownership,
  deduplication, snapshot inputs, or task-routing evidence.
- Why: this shipped analyzer crosses repository manifests, user installation
  roots, Git identity, shared resources, and mutation-routing boundaries.

### 2. Signatures

```text
skill_review.py inventory [--root PATH] [--skill NAME_OR_PATH]...
  [--family FAMILY] [--scope skill|family|repo|package|all]
  [--installed auto|off] [--installed-root PATH]...
  [--output PATH --output-root PATH] [--pretty]
```

The CLI defaults to `--installed auto`. The Python `build_inventory()` API
defaults installed discovery to `off` so callers and tests must opt in.

### 3. Contracts

- Automatic discovery derives bounded user skill roots only from verified
  manifest `target` rows and inspects direct child `*/SKILL.md` files. It never
  recursively searches a home directory or plugin cache.
- A copy maps to the current repository only through verified manifest target,
  provenance, package identity, and Git ownership evidence. The canonical
  repository file remains `reviewPath` for both matching and drifted installs.
- Verified copies deduplicate by canonical repository identity. Unowned copies
  deduplicate only when normalized skill name and content hash both match.
- Every collapsed copy retains path, root, platform, observed hash, drift, and
  mapping evidence. Installed copies are evidence, never mutation targets.
- Resolve the registry (families, family order, skill order, platforms, and
  shared references) from the generated `generated/registry-snapshot.json`
  payload alone. There is no AST fallback: the consumer never reads
  `installer/registry.py`. A path crossing a symlink boundary — the leaf or any
  parent component, via `_crosses_symlink` — raises without opening the target.
  An absent snapshot raises in a first-party pack checkout and resolves an empty
  registry in any other, so non-pack checkouts keep working while a pack that
  fails to ship its snapshot is caught. The snapshot's `schemaVersion` must be an
  exact `int` in `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS` before use —
  `bool`, `float`, or a string version, an unsupported integer, malformed JSON,
  or a mistyped field fails closed with a `ReviewError`. Hash each selected canonical shared source into `relatedTemplates` and
  snapshot identity without importing or executing reviewed repository code. The
  producer (`generate-skill-surfaces.py`) is the sole writer of the snapshot;
  `--check` fails when the committed snapshot drifts from `installer/registry.py`.
- Inventory schema version 3 exposes `installationRoots`, per-skill
  `installations`, `installedCopies`, `reviewPath`, `testTextReferences`, and
  deduplication coverage. Test-text references are bounded substring locators,
  not verified behavioral pins; callers must inspect the cited assertion before
  claiming behavioral coverage.
- The analyzer supports Python 3.9 and newer. When that runtime is unavailable,
  the skill reports the prerequisite and uses the documented bounded manual
  ownership, path, hash, and selector checks without executing reviewed files.
- Snapshot inputs exclude ignored directories, `__pycache__`, and `*.pyc` so
  interpreter side effects cannot change inventory identity.
- A safely resolved unowned installed copy remains reviewable evidence, but it
  is not changeable and cannot route task creation. Changeability requires a
  verified repository owner and a canonical source within its allowed template
  root.
- Omitting `--output` preserves the complete schema-version-3 inventory on
  stdout and never creates an artifact. Bounded mode requires both `--output`
  and an existing caller-owned `--output-root`, writes the same complete
  payload, and emits only a transport-schema-version-1 envelope to stdout.
- The bounded envelope reports status, artifact state and path, snapshot,
  inventory schema, selected-skill and installed-copy counts, coverage limits,
  and a bounded error. It never embeds skill, repository, installation, or
  candidate-signal records.
- Output roots must be real non-home directories whose supplied path contains
  no symlink component. Destinations must remain lexically and canonically
  below that root, cross no symlink, and remain outside reviewed repositories
  and installed roots. Existing files are replaceable only when their complete
  inventory schema and recomputed snapshot are valid.
- Artifact writes use the private temporary-file mode supplied by `mkstemp`,
  reinforce mode `0600` with descriptor chmod where the platform supports it,
  flush and `fsync` before replacement, recheck the prior destination
  fingerprint, replace atomically, and remove temporary files after failure.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Automatic install root is absent | Record `missing`; continue with bounded coverage. |
| Automatic root or skill is symlinked | Skip it and report the coverage limit. |
| Explicit root is missing, unbounded, non-directory, or symlinked | Reject before scanning. |
| Same name lacks verified ownership | Keep it unowned and disable task creation. |
| Unowned copy resolves safely | Keep it reviewable, but set `changeable=false`. |
| Installed hash differs from canonical | Report `installed-drift`; still review the verified canonical source. |
| Shared reference is missing, escaped, or symlinked | Fail closed before snapshot creation. |
| Test source contains the skill name | Emit a `substring-reference` locator with `behavioralPinVerified=false`. |
| Bytecode appears below a reviewed skill | Exclude it from related resources and snapshot identity. |
| Python is older than 3.9 | Exit with an actionable prerequisite and bounded manual-fallback instruction. |
| Installed discovery is `off` with explicit roots | Reject the contradictory arguments. |
| `--output` or `--output-root` is supplied alone | Reject without creating or replacing an artifact. |
| Output escapes its root, crosses a symlink, or enters a reviewed/install root | Reject and do not claim an artifact path. |
| Existing destination is arbitrary, malformed, or has a stale snapshot | Preserve it and return an error envelope. |
| Destination changes after validation or replacement fails | Preserve the prior state, remove the temporary file, and return an error envelope. |

### 5. Good/Base/Bad Cases

- Good: matching Claude and Codex copies collapse into one repository record
  with two installation entries; a drifted copy changes aggregate drift but
  not task ownership.
- Base: `--installed off` inventories only the selected repository skills.
- Bad: walking `$HOME`, mapping by a skill-name prefix, editing an installed
  copy, or merging different same-named unowned skills.

### 6. Tests Required

- Assert manifest-derived roots without a home walk, explicit opt-out and root
  overrides, multi-platform deduplication, drift routing, and unowned-name
  separation.
- Assert shared-reference content and membership change snapshot identity and
  that missing or symlinked sources fail closed.
- Assert the Python 3.9 floor, controlled fallback, honest test-text reference
  classification, unowned reviewability without changeability, and stable
  snapshots when generated bytecode appears.
- Assert legacy stdout and bounded artifacts have identical snapshots and
  counts, large inventories remain complete without entering the envelope,
  persistence is opt-in, valid prior artifacts can be replaced, unsafe paths
  and arbitrary content are preserved, and interrupted or raced writes leave
  no temporary residue.
- Preserve tests proving reviewed content is never executed, symlinks are not
  followed, pair comparison remains bounded, and SE/SD canonical roles remain
  stable.
- Run the focused analyzer suite, skill contract tests, `make generate`, and
  `make check` with a temporary bytecode cache outside the shipped skill tree.

### 7. Wrong vs Correct

#### Wrong

```text
~/.codex/skills/se-example/SKILL.md differs, so edit that installed file and
open one task for every host copy named se-example.
```

#### Correct

```text
Map each bounded installed copy through verified package evidence, review the
canonical repository source once, retain per-copy drift, and route one task to
the verified owner repository.
```

---

## Scenario: Observed Session Evidence In Skill Reviews

### 1. Scope / Trigger

- Trigger: changing how `se-review-skills` discovers, classifies, reports, or
  acts on conversations that used a reviewed skill.
- Why: session indexes contain incidental mentions, private data, nested
  transcripts, incomplete outcomes, and old skill versions. Without a separate
  evidence gate, an execution error can be misreported as a current source
  defect or leak raw conversation content into a task.

### 2. Signatures

```text
sessions=auto|off       default auto
session=<id>            repeatable, inside the verified project boundary
```

Automatic review inspects the available current conversation, then bounded
project-scoped history. It stops at three distinct confirmed sessions per skill
and twenty distinct sessions total, allocated round-robin across skills. One
session consumes one total slot and one slot for each reviewed skill it
demonstrably invoked; repeated invocations of the same skill stay in one
minimized skill/session evidence record.

### 3. Contracts

- Confirm invocation through explicit user or platform activation, or an
  assistant declaration corroborated by distinctive workflow behavior. Paths,
  diffs, maps, copied prompts, test output, and nested transcripts are
  mention-only candidates.
- Keep session discovery and causal judgment inline with the parent. Use only
  an already available project-aware reader and never scan global history, raw
  home directories, provider caches, or unrelated projects.
- Minimize evidence to a redacted session locator and relevant turn range,
  invocation evidence, skill provenance, request, expected contract, behavior,
  outcome, causal class, and confidence. Never persist raw dialogue, secrets,
  personal data, host paths, or full tool output.
- Record provenance as `current-canonical`, `installed-drift`,
  `historical-version`, or `unknown`. Historical or unknown evidence can show
  recurrence risk but cannot alone prove a current source defect.
- Classify mistakes as `skill-contract`, `execution-deviation`,
  `tool-or-environment`, `user-intent-change`, or `indeterminate`. A selectable
  finding also requires an observed consequence, causal explanation, current
  canonical locator, allowed template remedy, and falsifiable validation.
- Compare a successful or neutral invocation when available. Structure a remedy
  as core workflow, safety gate, conditional reference, deterministic helper,
  host overlay, evaluation, or recovery path. Every gotcha names trigger,
  failure, prevention, recovery, and regression method.
- Session evidence is read-only and never grants task or edit authority. Before
  `task=` or `apply=`, recompute the source snapshot and revalidate the project
  boundary, invocation, provenance, causality, locator, and redaction.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Session reader is unavailable or incompletely indexed | Continue static review and report the coverage limit. |
| Search result only mentions the skill | Reject it as an invocation and do not spend the confirmed-session budget. |
| Explicit session is outside the verified project | Reject it without global fallback. |
| Activation, outcome, or version was lost to compaction | Classify as `indeterminate`; do not create a finding. |
| Clear skill contract was ignored | Classify `execution-deviation`; prefer evaluation unless recurrence implicates structure. |
| Tool or permission failure caused the outcome | Change the skill only when its fallback or recovery contract is deficient. |
| User changed intent after invocation | Preserve chronology as `user-intent-change`; do not blame the skill. |
| Selected session evidence is stale before mutation | Reject the selector and require a fresh review. |

### 5. Good/Base/Bad Cases

- Good: verify a user activation, compare the relevant current skill rule to a
  redacted mistake and a successful control, classify the cause, point to the
  current template, and propose a testable recovery gotcha.
- Base: no safe history reader exists, so complete the static skill review and
  disclose zero historical-session coverage.
- Bad: count every skill-name search hit, quote a private transcript, assume an
  old session used current source, delegate raw conversations, or create a task
  because one run failed.

### 6. Tests Required

- Pin `sessions=auto|off`, repeatable `session=`, the three-per-skill and
  twenty-total budgets, round-robin allocation, and project-only discovery.
- Pin invocation confirmation, mention-only and nested-transcript rejection,
  all provenance and causal classes, successful controls, privacy minimization,
  structural remedies, gotcha fields, and source-plus-session revalidation.
- Assert the session-evidence reference ships to every registered platform and
  run focused skill tests, `make generate` twice, `make check`, and the release
  payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
Search every session for se-example, count all matches as uses, quote the failed
conversation into a Trellis task, and edit the installed copy.
```

#### Correct

```text
Search only bounded project history, confirm invocation, minimize and classify
the observed mistake, correlate it with current canonical source, and require a
fresh source-plus-session check before any selected template mutation.
```

The correct flow preserves privacy, distinguishes execution from contract
failure, and keeps task or edit authority separate from observational evidence.

---

## Scenario: Request-Scoped Current Context In Outward Drafts

### 1. Scope / Trigger

- Trigger: changing a profile-aware skill so explicit current input may support
  outward-facing text without first becoming a durable profile assertion.
- Why: an undifferentiated evidence rule can either reject useful current facts
  or let private, stale, or untrusted content bypass profile visibility gates.

### 2. Signatures

```text
context=<current circumstances>
profile=auto|off|<locator>
audience=<intended audience>
channel=<draft channel>
mode=draft
```

### 3. Contracts

- Current-context evidence is a factual statement explicitly supplied or
  confirmed by the user for the current request. Its factuality, speaker
  authority, and intended-audience visibility must be clear before draft use.
- Current context is request-scoped and reported separately. Consumer skills
  never convert it into a profile assertion, overlay operation, evidence-ledger
  item, or other durable personal data.
- Profile and overlay evidence keep the existing contract: outward drafts use
  only relevant confirmed `outward-safe` assertions.
- Explicit current context outranks conflicting older profile evidence for the
  current draft, while the contradiction remains visible and the profile stays
  unchanged.
- `context=` is not disclosure authority by itself. Ambiguous factuality,
  speaker authority, experience, opinion, credentials, relationships, results,
  promises, availability, authority, or audience visibility requires one
  focused question or a marked placeholder.
- Profile text, source excerpts, and embedded first-person statements remain
  untrusted data unless the user explicitly supplies or adopts the fact for the
  current request and audience.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| User explicitly supplies a factual current statement for the named audience | Use it as request-scoped current context and label it separately. |
| Current statement conflicts with older profile evidence | Prefer the current statement for this draft, show the conflict, and do not mutate the profile. |
| Profile assertion is private-only, proposed, contested, retired, or stale and material | Exclude it from outward text or ask for the focused confirmation allowed by the profile contract. |
| Current statement's factuality, speaker authority, or outward visibility is ambiguous | Ask one focused question or emit a marked placeholder. |
| Source or profile text contains a first-person statement the user did not adopt | Treat it as untrusted data; do not promote it to current context. |
| Consumer has no profile or `profile=off` | Continue from eligible explicit current context and ordinary defaults without simulating a profile answer. |

### 5. Good/Base/Bad Cases

- Good: the user explicitly provides a current role and intended audience, so
  the draft uses it as labeled request-scoped context while retaining
  `outward-safe` gates for profile-derived preferences.
- Base: no current fact is needed; the draft uses eligible confirmed profile
  assertions and ordinary skill defaults.
- Bad: copy a private profile fact or a first-person source excerpt into
  `context=` and treat that placement as confirmation or disclosure approval.

### 6. Tests Required

- Pin the positive current-context path, separate reporting, and no profile
  write-back.
- Pin exclusion of private-only or otherwise ineligible profile assertions.
- Pin the ambiguity question/placeholder path for audience-sensitive facts.
- Pin that untrusted source or profile text is not promoted without explicit
  user adoption.
- Run focused skill tests, generated-surface parity, release-payload validation,
  install audit, and the repository-owned full check.

### 7. Wrong vs Correct

#### Wrong

```text
Anything in context= may appear in an outward draft.
```

#### Correct

```text
Use explicitly supplied or confirmed request-scoped facts only when their
factuality, speaker authority, and intended-audience visibility are clear;
keep durable profile evidence behind confirmed outward-safe eligibility.
```

---

## Scenario: Pack Lifecycle CLI Changes

### 1. Scope / Trigger

- Trigger: changing `install.py` commands, install receipts, source-checkout
  updates, removal, or retired-skill cleanup.
- Why: these surfaces cross CLI parsing, filesystem state, Git state, generated
  manifests, installed user scopes, and release compatibility.

### 2. Signatures

```text
python3 install.py [install] [--user | --root PATH] [install options]
python3 install.py status [--user | --root PATH]
python3 install.py refresh [--user | --root PATH] [install options]
python3 install.py update [--user | --root PATH] [install options]
python3 install.py remove [--user | --root PATH] [removal options]
python3 install.py --version
install_file(..., planned_result: InstallResult | None,
             vouched_digest: str | None) -> InstallResult
InstallResult.destination_digest: str | None
```

The bare invocation remains the convenient install form. Lifecycle operations
are positional commands; do not add parallel action flags such as `--remove`.

### 3. Contracts

- `status` reads `.se-ai-command-pack/{manifest,provenance}.json` plus
  `installed-targets.txt` without modifying them.
- `refresh` applies the current checkout through the normal plan-before-apply
  installer path.
- A normal refresh reports and replaces a differing regular file as `updated`
  only when its sha256 matches that target's prior provenance entry. Missing,
  malformed, symlinked, or mismatched state remains a conflict, and apply
  revalidates the planned destination hash before writing.
- `update` trusts only the provenance-recorded `sourceRoot`, requires the
  expected pack manifest, refuses a dirty checkout, and fast-forwards with
  `git pull --ff-only`.
- Because `sourceRoot` comes from an integrity-unprotected plain-JSON receipt
  and drives `git` plus re-execution of its `install.py`, `update` refuses an
  unverified source before any `git` or exec: the recorded path must be a git
  repository (current-user-owned where the platform exposes an effective-uid
  check), and must either equal the running checkout (`installer.registry.ROOT`)
  or be explicitly confirmed via `--confirm-source` (or an interactive yes). The
  same-checkout / explicit-confirmation rule is the cross-platform guarantee;
  the ownership check is supplementary defense-in-depth on POSIX.
- On POSIX the trust checks and the later git/exec use are pinned to one
  directory file descriptor opened before the checks (`SourceHandle`,
  three-tier capability ladder in `_fd_pinning_tier`): children run with
  `pass_fds=(fd,)` plus a `preexec_fn` `fchdir` callable and relative argv,
  so swapping the recorded path after validation cannot redirect them.
  `preexec_fn` is safe here only because `install.py update` is a
  single-threaded CLI — do not reuse the pinned-child helper from threaded
  code. A symlinked `.git` or `install.py` is refused (never followed), and
  a `.git` worktree/submodule pointer file is accepted only after a one-hop
  `gitdir:` target validation (exists + is a directory + current-user-owned, bounded read,
  no `commondir` recursion). The residual window is entries *inside* the
  pinned, owned checkout; the external-path window is closed on tier 1.
- After pulling, `update` launches a fresh Python process, runs a dry-run, and
  applies only when that plan succeeds. This prevents old imported modules
  from being mixed with newly pulled files.
- `remove` and retired-target cleanup delete only hash-vouched or
  template-identical files unless the user explicitly passes `--force`.
- Retiring a skill requires removing it from `SKILLS`, deleting its
  canonical template, regenerating `manifest.json`, and registering every
  previously shipped target in `RETIRED_TARGETS`.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Install root is missing | Exit nonzero with `install root not found`. |
| Status receipts are absent or invalid | Report not installed and return 1. |
| Recorded source checkout is missing or is the wrong pack | Exit before Git or filesystem writes. |
| Recorded source is not a git repository, or (on POSIX) not owned by the current user | Refuse before any Git or exec. |
| `.git` or `install.py` is a symlink, or a `.git` file's `gitdir` target is missing/non-directory/foreign-owned | Refuse before any Git or exec; the opened directory fd is closed on every refusal. |
| Recorded source differs from the running checkout and is not confirmed | Refuse before any Git or exec (or prompt when interactive); `--confirm-source` authorizes a relocated checkout. |
| Source checkout is dirty | Exit before fetch, pull, or refresh. |
| Fast-forward pull fails | Exit with the Git failure; never merge or rebase. |
| Refreshed dry-run fails | Do not run the applying refresh. |
| Current payload differs and destination matches prior provenance | Report `updated`; refresh atomically without `--force` or backup. |
| Destination differs from its prior provenance or provenance is untrusted | Report a conflict; write no selected payload or receipts. |
| Destination changes after a vouched preflight | Reclassify against the prior hash and preserve concurrent drift. |
| Retired target is hash-vouched | Remove it during normal refresh. |
| Retired target drifted | Preserve and report it unless `--force` is explicit. |

### 5. Good/Base/Bad Cases

- Good: `python3 install.py update --user` fast-forwards a clean recorded
  checkout, previews the new payload, and reapplies from a fresh process.
- Good: a prior-version Claude or Codex skill still matches its receipt, so a
  normal refresh upgrades it as `updated` without treating it as user drift.
- Base: `python3 install.py --user` remains an idempotent install/refresh.
- Bad: implementing lifecycle behavior in a skill prompt, accepting both a
  positional command and an action flag, continuing in the pre-pull Python
  process, or deleting retired files without provenance vouching.

### 6. Tests Required

- CLI tests assert each positional command dispatches correctly and obsolete
  action flags are rejected.
- Status tests assert installed version, source checkout, platform grouping,
  and the not-installed return code.
- Update tests assert dirty-checkout refusal, `--ff-only`, dry-run-before-apply,
  and two fresh-process invocations for planning and application.
- Update source-trust tests assert that an unverified `sourceRoot` is refused
  with zero `git` and zero exec calls — including the principal case of a
  current-user-owned git checkout that differs from the running checkout and is
  refused by the confirmation gate (not merely the `.git` gate) — while the
  same-checkout path proceeds, `--confirm-source` and an interactive yes
  authorize a relocated checkout, a `.git`-file worktree is accepted, and the
  ownership check is skipped where `os.geteuid` is unavailable. CLI tests assert
  `--confirm-source` forwards and defaults to false.
- Retirement tests inject a prior provenance hash and assert normal refresh
  removes the vouched old target while existing drift-preservation tests stay
  green.
- Refresh tests inject prior-version Claude and Codex payload hashes, assert
  dry-run and apply classify them as `updated`, and pin user drift, untrusted
  provenance, preservation-policy precedence, and preflight-race behavior.
- Documentation contract tests inspect only the contract-bearing README and
  operator-guide sections, require prior-provenance authorization plus
  preservation precedence and `preserved` status, and avoid pinning whole
  paragraphs or generated repository-map output.
- Run `make check` to cover unit tests, Ruff, mypy, generated manifest parity,
  and the release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
python3 install.py --remove
```

This duplicates the positional command model and creates a second parser path.

#### Correct

```text
python3 install.py remove --user --dry-run
python3 install.py remove --user
```

One command surface owns removal, with an explicit preview before application.

For normal refresh ownership, comparing only against the current payload is
wrong because pristine bytes from an earlier release would look user-modified.
Use the prior receipt and carry the observed destination digest through the
plan:

```text
installed sha256 == prior provenance -> updated + apply-time digest recheck
installed sha256 != prior provenance -> conflict + no writes
```

## Scenario: SD Status Pack-Freshness Signal

### 1. Scope / Trigger

- Trigger: reading an `sd-status` report in this consumer repository and
  needing to know whether the installed SD command pack is current, or
  interpreting the `versions.packState` field anywhere.
- Why: local-mode `sd-status` cannot resolve a target pack version, so an
  installed pack arbitrarily far behind its source reports no freshness
  signal at all — no anomaly, no follow-up, no recommendation. An operator
  who reads `packState: "installed"` as "current" is misled by silence.

### 2. Disposition: local-only guidance (upstream approval not sought)

Both `scripts/sd-ai-command-pack-status.py` and
`scripts/sd_ai_command_pack_fleet_lib.py` are vendored with
`install: "always"` (`.sd-ai-command-pack/manifest.json`), so a local edit is
overwritten by the next pack refresh. A behavior change is therefore an
upstream pull request against `sd-ai-command-pack`, which needs explicit
per-PR approval that the autonomous run-level authority excludes. This
section is the local-only disposition: it records what the collector cannot
say and how an operator checks by hand. It is also the interim record an
upstream proposal would require to land first, so choosing local-only now
does not foreclose an upstream route later (the vendored-artifact upstream
route is tracked as its own task).

### 3. The load-bearing code

All citations below are pinned to installed pack `0.64.3`
(`sd-ai-command-pack-status.py` at 2631 lines) and were re-located by symbol
in the currently installed collector on 2026-08-09. Both files are
`install: "always"`, so on any other pack version re-locate by the named
symbol, not the line number.

- **Name-gated source lookup** — `collect_versions`, `:393-398`: the only
  target source local mode consults is the repository's own root
  `manifest.json`, and only when its `name` equals `sd-ai-command-pack`.
  In any consumer repository (this one's manifest is named
  `se-ai-command-pack`) the gate never opens and `sourcePack` stays `None`.
- **Omitted argument at the local call site** — `main`, `:2607-2619`: the
  local-mode `collect_local(` call passes no `target_pack_version`; the
  parameter defaults to `None` (`collect_local`, `:1926`). Only the fleet
  lane supplies a target (`collect_fleet`, `:2443`).
- **The drift gate both surfaces share** — `collect_follow_ups`,
  `:1769-1774`, and `next_steps`, `:1834-1837`: the refresh recommendation
  and the numbered next step both fire only on
  `versions.packState == "different"`. With no target, the state ladder
  (`collect_versions`, `:399-407`) stops at `"installed"` and neither
  surface can fire. The human `Delivery` line (`render_local`, `:2148-2150`)
  likewise prints a target suffix only when a target resolved.

### 4. What `packState: "installed"` means

**Unknown, not current.** `"installed"` is the neutral rung reached when no
target version resolved; it is emitted whether or not drift exists. Only
`"current"` and `"different"` are freshness verdicts, and local mode in a
consumer repository can produce neither. The top-line `SD status:
healthy|attention` verdict carries no pack-freshness claim in either
direction — `render_local` (`:2095-2100`) computes it from anomalies,
working-tree state, and sync state only. A repository with no resolvable
target still exits zero: the absence of a target is not an error, and the
report it gives instead is exactly `packState: "installed"` with
`targetPack: null` — read that pair as "target unknown, freshness not
checked".

### 5. Operator procedure: checking drift by hand

Learning a version must not fetch, install, refresh the pack, or create the
fleet profile; the procedure below only reads files that already exist.

1. Installed version: `.sd-ai-command-pack/provenance.json` →
   `packVersion` (this also appears as `versions.sdAiCommandPack` in the
   report).
2. Target version, first source — the machine fleet profile: resolve the
   path the way `fleet_profile_path` does
   (`sd_ai_command_pack_fleet_lib.py`, `:119-131`): `$XDG_CONFIG_HOME`
   first, `~/.config` as fallback, then
   `<base>/sd-ai-command-pack/config.json`. Read its `packSource`, then
   that checkout's `manifest.json` → `version`.
3. Compare. Installed strictly behind target means the pack is stale;
   `sd-status` will not have said so.

Target sources considered, with accept/reject reasons:

- **Machine fleet profile** (accepted, lookup position 1): written by
  `install.py TARGET --configure-fleet`, read through the documented
  `fleet_profile_path` resolution, purely local. Absent on machines that
  never ran `--configure-fleet` — in that case there is no resolvable
  target and freshness is simply unknown (see section 4); do not create the
  profile to answer the question.
- **Sibling source checkout by bare path convention** (rejected): guessing
  `../sd-ai-command-pack` without a profile recording it is an unrecorded
  convention, wrong whenever the checkout lives elsewhere. When the profile
  exists its `packSource` reaches the same checkout through a recorded
  path, which is why the profile is the accepted route to it.
- **GitHub release list** (rejected): network-dependent, so it must degrade
  under `--no-network` rather than fail or silently report `current` — a
  by-hand check that could not reach the network must report "could not
  check", never "current". It is also unproven as a source:
  `gh release list --repo platypeeps/sd-ai-command-pack` returned no
  releases when checked on 2026-08-07 and again on 2026-08-09.

### 6. Recorded reproduction of the defect shape

2026-08-09, this repository: installed pack `0.64.3`
(`provenance.json`), fleet profile resolved via `$XDG_CONFIG_HOME` to a
`packSource` naming the local `sd-ai-command-pack` checkout at version
`0.64.32` — installed strictly behind. `sd-status --no-network --json`
exited `0` and reported:

```json
{"sdAiCommandPack": "0.64.3", "packState": "installed",
 "sourcePack": null, "targetPack": null}
```

with no anomaly, follow-up, or recommendation naming pack freshness. The
invariant is that shape — installed strictly behind a resolvable source
with the freshness fields silent — not the version pair (the source
checkout advances on its own; it was `0.64.24` when the defect was first
observed on 2026-08-07) and not the top-line verdict (see section 4).

## Scenario: Repomix Repository Map Refresh

### 1. Scope / Trigger

- Trigger: adding or changing the on-demand repository map, its Repomix
  configuration, or its refresh command. The map is gitignored and never
  committed (policy A-025); it is generated locally on demand.

### 2. Signatures

```text
make repomix
bash .github/scripts/update-repomix
```

### 3. Contracts

- `repomix.config.json` owns the input exclusions and writes compressed,
  parsable Markdown to `docs/repomix-map.md`.
- Git change-count sorting is disabled so identical repository contents
  generate byte-stable file ordering on every regeneration.
- `.github/scripts/update-repomix` runs the pinned Repomix version through `npx`
  without adding Node dependencies to this Python project.
- The refresh script exports `NPM_CONFIG_IGNORE_SCRIPTS=true` **before** the
  `npx` invocation it constrains: `npx --yes` fetches and installs a package
  tree unattended, so any lifecycle script that tree declares would otherwise
  run un-reviewed on a maintainer machine. npm reads its configuration from the
  environment at invocation time, so an export placed after `exec npx` would
  never apply.
- The generated map excludes itself, local knowledge copies and receipts,
  Trellis task/session state, and copied agent-platform surfaces.
- `docs/repomix-map.md` is gitignored and generated on demand; it is never
  committed, so no committed-but-stale (silent-drift) state can exist.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| `npx` is unavailable | Exit nonzero with an actionable requirement message. |
| Repomix installation or generation fails | Propagate the nonzero exit; do not report a refreshed map. |
| Repomix detects suspicious content | Treat the generation as failed and inspect before use. |
| Configuration changes | Regenerate on demand with `make repomix`; the map is gitignored and never committed. |
| Identical inputs generate a different map | Treat the map as nondeterministic and investigate before relying on it. |

### 5. Good/Base/Bad Cases

- Good: `make repomix` uses the pinned version and replaces the local
  generated map.
- Base: rerunning the command without source changes produces no map diff.
- Bad: running an unpinned global or latest Repomix version and relying on an
  output whose behavior cannot be reproduced from the repository.

### 6. Tests Required

- `tests/test_repomix.py` asserts that the refresh script exports
  `NPM_CONFIG_IGNORE_SCRIPTS=true` and that the export precedes `exec npx` —
  ordering is the load-bearing half, and a test that only greps for the string
  would pass on a script where the setting never takes effect.
- `tests/test_repomix.py` asserts the required copied/runtime exclusion set and,
  when the on-demand map is present locally, verifies it omits those files while
  retaining representative repo-owned source, tests, templates, and specs. The
  map-content check skips cleanly when the gitignored map is absent (CI / fresh
  clones).
- Run `make repomix` and require a successful Repomix security scan.
- Run `git diff --check` and verify `docs/repomix-map.md` is the configured
  output and does not include itself.
- Run `make check` so repository-map tooling changes do not regress the Python
  pack, generated surfaces, or release gate.

### 7. Wrong vs Correct

#### Wrong

```text
npx repomix@latest
```

#### Correct

```text
make repomix
```

The repository-owned command pins the tool and applies the curated exclusions.

## Scenario: Hash-Locked Dev Dependencies

### 1. Scope / Trigger

- Trigger: changing a dev dependency pin, the lock, or anything that installs
  them (`Makefile` `setup`, the three installing CI jobs, Dependabot scope).

### 2. Signatures

```text
make lock          # regenerate requirements-dev.lock (needs uv + network)
make lock-check    # offline consistency gate, also wired into `make check`
```

### 3. Contracts

- `requirements-dev.txt` is an **input file**; nothing installs from it.
  `make lock` compiles it into `requirements-dev.lock` with
  `uv pip compile --universal --python-version 3.10 --generate-hashes
  --no-header --only-binary :all:`, and the lock is the only install source for
  CI and `make setup`.
- Installs use `--require-hashes --only-binary :all:`. Both flags are required:
  `--require-hashes` alone accepts a *hashed source distribution*, whose build
  hooks then execute — the hash proves provenance, not that nothing runs.
- `make setup` builds the venv with `python -m venv --clear`. Without `--clear`
  a package that dropped out of the lock survives in the reused environment and
  the gate runs against a superset of the locked set.
- `.github/scripts/check-dev-requirements-lock.py` is stdlib-only and offline,
  so it can run *before* the install it protects. It reports `input-unpinned`,
  `unpinned`, `unhashed`, `pin-missing`, and `pin-mismatch`; exit 0 pass,
  1 findings, 2 usage/environment error.
- What the checker provably does **not** catch: it cannot prove the lock is a
  faithful regeneration of its input. A transitive dependency silently held at
  an older version, or a lock hand-edited in a way that stays internally
  consistent, passes. That needs a resolver and a network; only `make lock`
  followed by an empty diff proves regeneration.
- A *missing* entry is not part of that gap. `--require-hashes` rejects any
  dependency pip resolves that the file does not pin, so deleting an entry
  fails the install with that requirement named rather than passing quietly —
  verified by installing a lock with `mypy-extensions` removed, which exits 1
  on `mypy_extensions>=1.0.0 ... These do not:`. The undetectable case is
  stale-but-consistent, not absent.
- Entry detection must not require `==`. A rule keyed on the pin operator skips
  a loosened requirement instead of reporting it — silently passing the exact
  desync the gate exists to catch.
- Indentation alone must not mark a line as continuation text either: pip strips
  each line before parsing, so `    ruff>=0.16` installs exactly like the
  unindented form. Only the shapes the compiler emits below an entry —
  `--hash=`/option continuations and `# via` comments — are continuations.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Dependabot bumps `requirements-dev.txt` without a regenerated lock | `lock-check` fails with `pin-mismatch`; the PR is incomplete until `make lock` is committed alongside it. |
| A lock entry loses its `--hash=` lines | `unhashed` finding, exit 1. |
| A lock or input entry is loosened from `==` to a range | `unpinned` / `input-unpinned` finding, exit 1 — never a skip. |
| The lock is missing or declares no requirements | Exit 2 with a `make lock` recovery hint, distinct from a findings failure. |
| A dependency has no wheel for a supported interpreter | `--only-binary :all:` fails the compile; resolve it deliberately rather than relaxing the flag. |

### 5. Good/Base/Bad Cases

- Good: a pin change lands as `requirements-dev.txt` + `requirements-dev.lock`
  in one commit, and `make lock-check` passes offline.
- Base: no dependency change, so `lock-check` is a no-op inside `make check`.
- Bad: installing from `requirements-dev.txt`, or dropping `--only-binary` and
  trusting `--require-hashes` to prevent source builds.

### 6. Tests Required

- `tests/test_dev_requirements_lock.py` covers the live repository state, every
  finding class, PEP 503 name normalization across the input/lock spellings,
  and the exit-2 paths. Negative cases build disposable fixture directories and
  pass `--repo` at them; no test mutates the repository's own requirements
  files.
- The same module locks the wiring: the `Makefile` install line must keep
  `--require-hashes --only-binary :all: -r requirements-dev.lock` and `--clear`.
  A checker nothing calls verifies nothing.

### 7. Wrong vs Correct

#### Wrong

```text
python -m pip install -r requirements-dev.txt
```

#### Correct

```text
python -m pip install --require-hashes --only-binary :all: -r requirements-dev.lock
```

## Scenario: Vendored OpenCode npm Manifest

### 1. Scope / Trigger

- Trigger: any proposal to remove, prune, or Dependabot-manage
  `.opencode/package.json` or its declared npm dependency.

### 2. Local-only record (four fields)

1. **Owning pack** — upstream Trellis (`mindfold-ai/Trellis`, the upstream
   already identified at this file's Vendored-Artifact Ownership section).
2. **File** — `.opencode/package.json`. Registry A member
   (`.trellis/.template-hashes.json`, the machine-local Trellis hash file);
   absent from Registry B (`.sd-ai-command-pack/manifest.json`);
   `templateReceipted` in `.github/trellis-provenance.json`.
3. **Behaviour** — the manifest declares `@opencode-ai/plugin: ^1.14.39`, but
   no `.opencode` JavaScript imports it: every import in `.opencode/lib/*.js`
   and `.opencode/plugins/*.js` resolves to a node builtin or a sibling module.
   So a caret range is resolved and installed for a package nothing uses, and
   `.gitignore:70` ignores `.opencode/node_modules/`, meaning those installs
   land inside the checkout.
4. **Upstream pull request** — mindfold-ai/Trellis#565 proposes dropping the
   unused dependency (the vendored template manifest becomes `{}`), citing the
   import evidence above. The explicit per-PR approval it required was
   recorded in task `08-10-upstream-relay-opencode-plugin-dep` on 2026-08-20
   before the PR was opened, following the relay pattern precedented by
   platypeeps/sd-ai-command-pack#397, #398, #399.

### 3. Contracts

- Do **not** edit or delete `.opencode/package.json` locally. A local removal
  is reverted by the next Trellis refresh, silently — the class of failure
  already recorded under Vendored Pack Lifecycle.
- Do not add an `npm` Dependabot ecosystem block for it: Dependabot would open
  PRs against a file this repository cannot own.
- Guidance that claims the manifest is "unused and slated for removal" is
  wrong and must be corrected wherever it is living guidance; archived task
  artifacts keep their original wording as historical record.

### 4. Good/Base/Bad Cases

- Good: the defect is recorded here and in the task disposition, and the
  removal is routed upstream when per-PR approval is obtained.
- Base: the manifest stays as vendored, with the unused dependency documented.
- Bad: deleting the dependency locally and reporting the audit finding fixed —
  the fix has an expiry date set by the next refresh.

## Scenario: Repository-Owned PR Full Check

### 1. Scope / Trigger

- Trigger: configuring or changing the repository-owned project check selected
  by the deterministic `sd-review-pr` local gate.

### 2. Signatures

```text
package.json scripts.check = "make check"
package.json scripts.check:full =
  "npm run check && bash ~/.agents/bin/sd-ai-command-pack-full-check.sh"
bash ~/.agents/bin/sd-ai-command-pack-review-full-check.sh
bash ~/.agents/bin/sd-ai-command-pack-toolchain.sh doctor
```

### 3. Contracts

- The package `check` script is the sole package-level owner of `make check`.
- `check:full` runs the project check first and the shared pack full-check
  second, joined by `&&` so either failure remains blocking.
- The review selector invokes `check:full` with Prism and Gito disabled; the
  shared gate continues to own all other pack-wide checks.
- Root package metadata stays private and dependency-free. It exists only to
  expose scripts and must not produce a package lockfile.
- `check:full` must not call the review selector, `sd-review-pr`, or a platform
  adapter because those paths recurse into selection.
- Toolchain doctor reports `package:check` as a candidate but does not execute
  it; execution belongs to the review selector.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| `check:full` is missing or invalid | The review selector uses its documented fallback. |
| The configured package runner is unavailable | Exit `127` with an actionable error. |
| `make check` fails | Stop before the shared pack full-check. |
| The shared pack full-check fails | Propagate its nonzero exit. |
| The wrapper contains a forbidden recursive command | Reject it with exit `2`. |

### 5. Good/Base/Bad Cases

- Good: `check:full` composes the canonical project check and shared pack gate.
- Base: contributors continue to run `make check` directly.
- Bad: `check:full` calls the review helper, skips the shared gate, declares
  dependencies, or duplicates the Make target in multiple package scripts.

### 6. Tests Required

- Parse `package.json` and assert the exact private, dependency-free script
  contract and absence of supported package lockfiles.
- Run the review selector with a stub package runner and assert it requests
  `run check:full` with Prism and Gito disabled.
- Run the focused configuration test, `npm run check`, toolchain doctor,
  `make repomix`, the Obsidian KB refresh, `npm run check:full`, and
  `git diff --check`.

### 7. Wrong vs Correct

#### Wrong

```json
{
  "scripts": {
    "check:full": "bash ~/.agents/bin/sd-ai-command-pack-review-full-check.sh"
  }
}
```

#### Correct

```json
{
  "private": true,
  "scripts": {
    "check": "make check",
    "check:full": "npm run check && bash ~/.agents/bin/sd-ai-command-pack-full-check.sh"
  }
}
```

The correct wrapper preserves the repository's canonical check and the shared
pack gate without creating a recursive review path.

## Scenario: Audit Ledger Status Reconciliation

### 1. Scope / Trigger

- Trigger: rewriting `status:` on findings in `.trellis/audit/ledger.md`,
  whether during an `sd-audit-repo` run or a standalone reconciliation.
- Why: nothing in the merge path writes a finding's status back when the PR
  that fixes it lands. On 2026-08-15 all 44 findings still read `open` while
  35 were demonstrably fixed, which makes the ledger's open set useless as a
  backlog — a consumer cannot tell a live defect from one fixed six merges ago.

### 2. Contracts

- Status vocabulary is closed: `open`, `fixed`, `regressed`, per
  `.claude/skills/sd-audit-repo/SKILL.md:246`. There is no status for "real,
  but the remaining fix is upstream" — that belongs in `notes:` naming the
  blocked Trellis task that owns it.
- `notes:` is the human-editable field and may already hold text. Append;
  never overwrite. Preserve unknown lines within an entry.
- `evidence:` keeps its original `file:line` references even after the code
  moves. It records what was first observed; the current location goes in
  `notes:`. Rewriting it destroys the record the re-check is falsified against.
- `last-seen:` means "last seen present". Do not advance it on a `fixed`
  finding — that asserts the defect was observed at this HEAD.

### 3. Validation & Error Matrix

- status outside the closed vocabulary -> reject
- `fixed` with no re-check assertion -> reject; an unasserted `fixed` is
  indistinguishable from a guess
- ledger committed together with `.trellis/tasks/**` -> the bookkeeping
  validator admits neither commit; per `SKILL.md:253-259` the mix cannot be
  journaled or finalized and cannot be undone once published. Commit the
  ledger alone, task artifacts alone.

### 4. Common Mistake: proving a file moved, not that the defect is gone

**Symptom**: a finding is marked `fixed` because the path in its evidence no
longer exists.

**Cause**: `not exists(<path>)` is cheap and looks decisive. It is only valid
when *deletion is the fix* — A-026's unreferenced dead wrapper qualifies.

**Fix**: assert the inverted evidence at the construct's current home.

#### Wrong

```python
# A-034: "npx --yes with unlocked transitives and install scripts enabled"
"A-034": lambda: (not exists("scripts/update_repomix"), "the script is gone"),
# Passes. The script moved to .github/scripts/update-repomix and still
# runs `npx --yes` against unlocked transitives.
```

#### Correct

```python
# A-018 relocated too, but the assertion tests the property the finding named.
"A-018": lambda: (
    "os.getuid()" in read("~/.agents/bin/sd_ai_command_pack_lib.py"),
    "cache root is UID-qualified",
),
```

**Prevention**: when evidence points at a path that no longer exists, find
where the construct went before choosing a status. Relocation alone is
`open`.

### 5. Common Mistake: re-verifying one side of a two-sided finding

**Symptom**: a finding whose claim is a *mismatch* between two things stays
`open` across repeated passes, each pass confirming the half that never
changed.

**Cause**: many findings do not assert "X is wrong" but "X disagrees with Y" --
behaviour against a documented promise, a value against its schema, an
implementation against its own docstring. Re-reading X and finding it unchanged
feels like a re-check and produces a confident `still open`. It establishes
nothing: either side moving resolves the finding, and the side that moves is
usually the cheaper one, which is the documentation.

A-008 is the worked case. It claimed `--platform` promised platform-only
install while `installer/fileops.py:145` selects `ALWAYS_INSTALL` /
`IF_NOT_EXISTS` rows ahead of the platform filter. Two reconciliations
(2026-08-15, 2026-08-16) re-read the selection order, found it unchanged, and
recorded `still open`. Both were wrong: `06f9fa5` had amended the help text on
2026-08-05 -- the second remedy the finding itself proposed -- and pinned the
result in `tests/test_install_core.py:258`, a test that names A-008. The
finding sat wrongly open for three weeks, and the third pass nearly reordered
live installer code to fix a contradiction that no longer existed.

#### Wrong

```python
# Confirms the selection order. The finding was never about the order alone.
"A-008": lambda: (
    "ALWAYS_INSTALL" in read("installer/fileops.py").split("platform_filter")[0],
    "rows are still selected before the platform filter",
),
```

#### Correct

```python
# Both sides, and the finding survives only while they still disagree.
"A-008": lambda: (
    selects_before_filter("installer/fileops.py")
    and "installed regardless of this filter" not in read("install.py"),
    "selection order still contradicts the documented --platform contract",
),
```

**Prevention**: read the finding's title as a sentence and count its nouns. If
it names two things, the re-check asserts both, and a passing re-check must
state which side it observed moving. A finding that cites a promise is closed
by the promise changing just as surely as by the code changing -- and when a
test already pins the agreement, the question is settled, not open.

### 6. Tests Required

A reconciliation ships a re-check script that reads the ledger to discover
which findings claim `fixed`, rather than accepting that list as input.
Assertion points:

- every `fixed` finding has a registered assertion — an unregistered one fails
- each assertion re-runs that finding's inverted evidence and reports what it
  observed
- an empty `fixed` set prints a distinct vacuous-pass line, so a run before the
  ledger is written cannot read as a real pass

## Shared State Sentinel Contracts

### 1. Scope / Trigger

- Trigger: changing a shared state schema or any skill-specific argument that
  creates, replaces, or resumes that state.
- Why: shared references describe portable behavior, but each consuming skill
  owns a strict argument surface that must not silently acquire another
  consumer's aliases.

### 2. Contracts

- Shared state references describe first-state behavior in caller-neutral
  terms and enumerate each consumer's explicit sentinel separately.
- Caller-specific sentinels are not interchangeable argument names. For the
  monitor-state schema, `se-monitor` accepts `baseline=new` and `se-watchlist`
  accepts `checkpoint=new`; each skill rejects the other name through its
  unknown-argument boundary.
- Sentinel wording must not alter the shared schema version, recovery rules,
  pending-item behavior, or the rule that first-state mode is not a
  zero-change delta.

### 3. Tests Required

- Pin every accepted skill-specific sentinel in its owning skill and in the
  shared reference.
- Pin cross-rejection so a shared-reference edit cannot accidentally imply
  aliasing between consumer argument surfaces.
- Run the neighboring state recovery, pending-item, first-state, generated
  surface, and release-payload checks.

### 4. Wrong vs Correct

- Wrong: a shared reference says that `baseline=new` starts state for every
  consumer, implying that watchlist accepts `baseline=`.
- Correct: the shared reference names caller-neutral first-state behavior,
  maps each consumer to its own sentinel, and preserves strict cross-rejection.

---

## Runtime Profile And Claude Overlay Contract

### 1. Scope / Trigger

- Trigger: changing a skill's invocation, context, model profile, effort, or a
  platform's verified runtime-metadata support.
- Why: one portable recommendation crosses registry validation, generated
  entrypoints, manifest source selection, installation hashes, and review-source
  reconciliation.

### 2. Signatures

```text
RuntimeProfile(invocation, context, model, effort)
RUNTIME_PROFILE_ASSIGNMENTS
SKILL_RUNTIME_PROFILES
render_claude_skill(name, canonical_text, profile) -> str
generated/skills/claude/<skill>/SKILL.md
make generate
```

### 3. Contracts

- Every `SKILL_NAMES` entry has exactly one portable profile. Grouped
  assignments are validated before their ordered per-skill map is derived.
- Canonical `SKILL.md` frontmatter stays limited to `name` and `description`;
  its body is the only authored instruction source. The generated Claude body
  equals the canonical body verbatim, with exactly one deliberate exception: a
  `fresh-session` profile appends an advisory note (see below). Canonical bodies
  are never modified.
- Claude generation maps only verified invocation controls, `context: fork`,
  `model`, and `effort`. Allowed model values are `inherit`, `haiku`, `sonnet`,
  and `opus`.
- `fresh-session` never becomes `context: fork`; generation omits the context
  key while retaining supported invocation, model, and effort fields. Because
  Claude frontmatter has no independent-session field, `render_claude_skill`
  instead appends an advisory in-body note (marker
  `<!-- generated: runtime-profile fresh-session -->`, constant
  `FRESH_SESSION_NOTE`) stating the independent-run intent, so the intent is not
  silently dropped. An unsupported host primitive on any portable axis must get
  an honest encoding (in-body note or documented degradation), never a
  misleading frontmatter field and never a silent omission.
- Only Claude `SKILL.md` manifest rows use generated sources. Claude resources
  and every Codex/shared-agent payload continue to use canonical templates.
- The skill-review inventory compares installed bytes with the generated source
  but reports and reviews the authored canonical template.
- `generated/**` is a release payload and is excluded from the repository map
  because it duplicates canonical bodies.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Missing, unknown, or duplicate skill assignment | Raise `RuntimeError` during registry validation. |
| Unknown portable invocation, context, model, or effort | Fail generation before writing outputs. |
| Claude adapter produces an unsupported key, model alias, or effort | Fail generation before writing outputs. |
| Canonical body differs from the generated body (beyond a `fresh-session` overlay's appended advisory note) | Generator parity test fails. |
| A non-`fresh-session` overlay carries the fresh-session marker, or the marker-bearing overlay set is not exactly the fresh-session skills | Generator marker-set test fails. |
| A `fresh-session` overlay's advisory note is misreported as host-enforced isolation | `contextIsolation` must stay `inline-or-host-default` (keyed off frontmatter `context == "fork"` only). |
| Generated entrypoint is missing, changed, stale, or symlinked | Check mode exits nonzero with the affected path. |
| A later coordinated write fails | Restore prior generated and catalog files; remove newly created directories. |
| Installed Claude bytes match generated bytes | Report `canonical-match` while retaining the authored review path. |
| Generated payload changes without a version bump | Release gate exits nonzero. |

### 5. Good/Base/Bad Cases

- Good: change one registry profile, run `make generate`, and receive a Claude
  frontmatter-only change while every canonical body and portable target stays
  unchanged.
- Base: rerun generation with unchanged profiles and receive no diff.
- Bad: add `model` to a canonical skill, hand-edit a generated Claude file,
  map `fresh-session` to `fork`, or review the generated copy as authored code.

### 6. Tests Required

- Pin exact registry coverage plus missing, unknown, duplicate, and invalid
  value failures.
- Pin each Claude translation branch, frontmatter order, canonical-body
  preservation, generated drift, stale-output cleanup, and coordinated rollback.
- Pin the `fresh-session` in-body note: the marker-bearing overlay set equals
  exactly the fresh-session skills, the canonical body is preserved as a prefix,
  and `contextIsolation` stays `inline-or-host-default` (the note is advisory).
- Pin platform-specific manifest sources and installed bytes, including
  Codex/shared-agent portable frontmatter.
- Pin generated installed-byte drift against the authored canonical review path.
- Run `make generate` twice, `make check`, `make repomix`, and
  `git diff --check`.

### 7. Wrong vs Correct

#### Wrong

```yaml
# templates/skills/se-research/SKILL.md
name: se-research
description: Use when deep research is requested.
context: fork
model: opus
```

#### Correct

```text
templates/skills/se-research/SKILL.md
  -> portable name/description plus authored body
installer/registry.py
  -> RuntimeProfile("both", "forked", "deep", "high")
generated/skills/claude/se-research/SKILL.md
  -> context: fork, model: opus, effort: high plus the canonical body
```
---

## Scenario: Frontmatter Grammar Authority And Shipped Subset

### 1. Scope / Trigger

- Trigger: changing how skill frontmatter is parsed, emitted, or validated on
  either side - `_frontmatter` in the shipped `skill_review.py`, or
  `parse_frontmatter` / `validate_skill` / the `yaml.safe_dump` emitter in
  `.github/scripts/generate-skill-surfaces.py`.
- Why: two parsers read the same bytes and only one of them may depend on
  PyYAML, so their agreement is a contract rather than a coincidence.

### 2. Signatures

```text
.github/scripts/generate-skill-surfaces.py   # the authority
  parse_frontmatter(text, label) -> tuple[dict, str]          # yaml.safe_load
  validate_skill(name) -> tuple[list[str], dict[str, str] | None]
  _unrenderable_character(value) -> str | None
  render_claude_skill(...) -> yaml.safe_dump(..., width=10000)

templates/skills/se-review-skills/scripts/skill_review.py     # the subset
  _frontmatter(text, label) -> tuple[dict[str, str], str, tuple[str, ...]]
  raises ReviewError("<label>:<line>: unsupported frontmatter construct: <name>")
```

### 3. Contracts

- The generator is authoritative. The shipped parser is a strict **rejecting**
  subset: for every document it accepts it returns what `yaml.safe_load`
  returns, and every construct outside the subset raises instead of being
  reinterpreted or silently skipped. Over-rejection is correct; disagreement
  never is.
- The subset's value domain is exactly `str`, `bool`, and `None`, represented
  as the text itself, `"true"` / `"false"`, and `""`. Nothing else may be
  accepted, because nothing else has a faithful text representation.
- Keys and values consult the same resolution predicate but not identically. A
  value YAML resolves to a boolean stays inside the subset - its text is what
  the mapping would carry anyway. A **key** does not: `true: v` gives PyYAML
  the mapping key `True`, not `"true"`, so the mapping itself diverges. Only
  the value path exempts `true` / `false`.
- YAML 1.1 resolution is wider than intuition. `yes` / `no` / `on` / `off` /
  `True` are booleans, `~` / `null` is None, `010` is 8, `0x1f` is 31, `1.0` is
  a float, and `2026-08-10` is a `datetime.date`. Confirm the resolver
  empirically before widening or narrowing the guard; never from memory.
- `<<` needs its own rule. PyYAML tags it as a merge key and raises
  `ConstructorError`, which no resolver-free parser can infer from the token.
- Indicator tests are on the **first character**, never a substring. A
  substring test rejects `disable-model-invocation`, which 14 generated files
  carry, and `a#b`, which PyYAML accepts.
- Trim with `strip(" ")`, never bare `strip()`. Python counts U+00A0 as
  whitespace and YAML does not, so `strip()` silently drops a character the
  authority keeps.
- Any Unicode category `Cc` character other than the line break is refused
  anywhere in the block. NUL makes PyYAML's reader raise `special characters
  are not allowed` while a naive line parser accepts it.
- The authority owes a reciprocal obligation: `validate_skill` refuses a
  description containing a `Cc` character, U+2028, or U+2029, because
  `yaml.safe_dump` escapes or folds those into output the subset must reject.
  Without it the generator can emit an overlay its own review tool cannot read.
  `validate_agent` deliberately does not carry the guard - `_safe_pack_skill_source`
  refuses any basename but `SKILL.md`, so agent overlays are unreachable by
  this parser and their list-valued `tools` is legitimate.
- The emitter's `width=10000` is load-bearing. A narrower width folds a long
  description onto a continuation line, which the subset rejects as an indented
  line.

### 4. Validation & Error Matrix

- indented line -> `indented line`
- no colon / `name:value` -> `line without a mapping colon` /
  `mapping colon without a following space`
- `tools: [Read]`, `{a: b}`, `|`, `>`, `&a`, `*a`, bare `-` or `?`, `@ % , #`
  or a backtick opening a value -> `value opening with a YAML indicator`
- `k: a: b`, `k: v:` -> `colon in a plain scalar`
- `k: v # c` -> `comment in a plain scalar`
- `yes`, `~`, `010`, `1.0`, `2026-08-10` as a value ->
  `value that YAML resolves to a non-string`
- `true:`, `010:`, `2026-08-10:`, `<<:` -> `key that YAML resolves to a non-string`
- quoted, anchored, or sequence-opened key -> `key opening with a YAML indicator`
- empty key, repeated key -> `empty key`, `duplicate key`
- `'a`, `"a` -> `unterminated quoted scalar`; `'a' junk` ->
  `content after a closing quote`
- `"a\tb"` -> `escape sequence in a double-quoted scalar`
- any `Cc` character -> `control character 0x.. in the block`

### 5. Good/Base/Bad Cases

- Good: `description: Use when it's time` - plain scalar, apostrophe intact.
- Base: `description: 'Use when alpha: omega'` - quoted because the value
  carries a colon; both parsers return the same text.
- Bad: `tools: [Read]` in a `SKILL.md` - a flow sequence the subset refuses by
  construct name and line, rather than dropping the line as it once did.

### 6. Tests Required

`tests/test_frontmatter_conformance.py`, six groups:

1. Corpus regression over `**/SKILL.md` enumerated from `git ls-files -z`, with
   vacuity guards (>=150 documents, >=1 boolean, >=1 double-quoted). It passes
   before and after any correct change - a regression guard, never a bite proof.
2. Agreement table for documents inside the subset where a naive parser
   diverges.
3. Rejection table, one case per bullet above, asserting construct and line.
4. Generator reciprocity in three halves: render every overlay and agree (a);
   must-reject for `Cc` / U+2028 / U+2029 (b); must-accept and round-trip for an
   apostrophe, a colon-space, and a `#` (c). Half (c) is what keeps a validator
   that refuses everything from passing half (b).
5. Installed-root fixture through `_discover_installed` / `build_inventory` -
   no tracked enumeration can reach an operator's installed skills.
6. Product fuzz against PyYAML: 13 key shapes x 36 value shapes plus a
   control-character sweep. Baseline `cases=468 accepted=72`. A run accepting
   materially more or fewer means the parser drifted from this contract;
   reconcile against the contract before editing the baseline.

Each group must be shown to bite by a probe that is reverted afterwards.

### 7. Wrong vs Correct

#### Wrong

```python
# Silently reinterprets, and silently skips what it cannot model.
if value.startswith(("'", '"')):
    values[key] = ast.literal_eval(value)   # Python escapes, not YAML's
else:
    continue                                # the line just disappears
```

#### Correct

```python
# Refuses what it cannot represent, naming the construct and the line.
if value[0] in {"'", '"'}:
    values[key] = _unquote_scalar(value, label, line_number)
elif value[0] in _YAML_INDICATORS:
    raise _frontmatter_error(label, line_number, "value opening with a YAML indicator")
```
