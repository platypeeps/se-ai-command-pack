# Repo-own tooling home and vendored-path documentation

## Goal

Contributors can tell editable repo-own source from installed vendored product at a glance, and no dead entry points linger to drift.

## Requirements

- Give repo-own tooling one documented home (e.g. tools/, or explicitly documented .github/scripts) — today 17 of 19 scripts/ files are SD-pack installs and repo-own build scripts sit in .github beside installed prompts. [A-004]
  - *Count re-measured 2026-08-10: the filing's "17 of 19" is stale. `git ls-files scripts/` returns 28 tracked files and both pack receipts list 26, so it is **26 of 28**, with the same two repo-own files. After D-2 and D-3 it becomes 26 of 26.*
- Add a CONTRIBUTING section listing the vendored do-not-edit path families (scripts/sd-ai-command-pack-*, .github/prompts/sd-*.prompt.md, platform command/skill dirs, .trellis-owned files) and where their sources live. [A-004]
- Resolve the dead wrapper scripts/se-ai-command-pack-skill-review.py: delete it, or document + test it as the supported repo-root invocation (coordinate with 07-25-audit-lint-shipped-payload, which conditionally includes it in the lint scope). [A-026]

## Decisions (planning convergence, 2026-08-10)

Recorded here because the PRD left the home and the wrapper disposition open,
and because planning turned up one constraint and one defect the filing did not
know about. Each is backed by evidence in the checkout, cited inline.

### D-1 — `.github/scripts/` is the documented repo-own tooling home

The PRD offers `tools/` or "explicitly documented `.github/scripts`". Choose the
second: six repo-own build scripts already live there, the `Makefile` already
calls four of them across five call sites (`:29`, `:32`, `:64`, `:65`, `:69` —
`generate-skill-surfaces.py` is invoked twice), and `.github/workflows/tests.yml`
calls six (`:62`, `:84`, `:85`, `:101`, `:146`, `:156`). A `tools/` directory
would move files that two callers already reference at a settled location and
buy nothing the documentation does not.

Derived from `.sd-ai-command-pack/installed-targets.txt` (210 entries), not from
naming: `.github/scripts/**` is installed by neither registry, and
`.github/prompts/**` is wholly vendored. No directory holds both kinds.

### D-2 — Move the Repomix refresh script into the documented home

From `update_repomix` under `scripts/` to `.github/scripts/update-repomix`.

This decision was **reversed during adversarial review**. The first draft kept
the file in place, claiming three vendored contracts pinned the path and made a
move unavailable. Two of those three claims did not survive verification, and
the record is kept here because the corrected reasoning is the decision.

| Claimed blocker | Verified outcome |
| --- | --- |
| `sd-ai-command-pack-review-scope.sh:146` hardcodes the path in `is_repository_map_scope_path()` | **Real but benign.** `is_pack_target_path()` greps `installed-targets.txt`, and `.github/scripts/**` is absent from it, so the moved file is an ordinary authored file. The effect is that editing it no longer *requires* a `pack.review-scope` heading — a relaxation for authored code, not a breakage. |
| `docs/SD_AI_COMMAND_PACK.md:1042` documents `sd-update-spec` discovery via executable `scripts/` entries | **Disproven.** The documented order checks exact Makefile targets *first*, and `Makefile:34` defines `repomix:`. Discovery succeeds regardless of where the script lives. |
| `.github/copilot-instructions.md:45` lists `scripts/update_repomix*` as a pack path | **Real, and already wrong today.** `installed-targets.txt` does not install this file; the repository owns and edits it (`07-25-audit-dependency-hygiene` added `NPM_CONFIG_IGNORE_SCRIPTS`). The move turns a wrong vendored claim into a stale one. |

With no genuine blocker, the third acceptance criterion is met as written rather
than reinterpreted, and `scripts/` becomes **100% vendored with no exception** —
a rule a contributor can apply without remembering a carve-out, which is the
stated goal. The rename to `update-repomix` matches the hyphenation of its six
siblings in the documented home.

Accepted, recorded cost: two vendored files
(`sd-ai-command-pack-review-scope.sh:146`, `.github/copilot-instructions.md:45`)
keep references to the old path. Both are Registry B installs that this
repository cannot correct without an upstream pull request, so they are recorded
as a follow-up relay rather than silently tolerated. Neither reference causes a
failure: the first becomes a dead `case` arm, the second a stale line in a file
reviewers are already told not to read line by line.

**Provenance consequence of the move.** `PLATFORM_DIRS` in
`.github/scripts/check-trellis-provenance.py:37` includes `.github`, so every
tracked file under it must be covered or the gate reports `uncovered:`. Landing
the script at `.github/scripts/update-repomix` therefore requires curating it
into `repoOwn` in `.github/trellis-provenance.json` — the same list D-4 fixes,
and the same step `07-25-audit-dependency-hygiene` recorded when it added a new
`.github/scripts` file. `scripts/` is not a platform directory, so deleting the
D-3 wrapper needs no provenance change.

**Implementation trap to avoid.** The script derives its repository root as
`"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` (`:4`). At
`.github/scripts/` that resolves to `.github/`, not the repository root. The
move must change `/..` to `/../..` or the `cd "$repo_root"` before `exec npx`
runs Repomix against the wrong directory.

### D-3 — Delete the wrapper

The removed wrapper — `se-ai-command-pack-skill-review.py`, formerly under
`scripts/` — was an 18-line `runpy` forwarder to
`templates/skills/se-review-skills/scripts/skill_review.py`. A repo-wide grep
excluding `.git` returns **no executable reference**: every hit is a
`.build/` review receipt, the generated `docs/repomix-map.md`, the audit
ledger/report, an archived task, or this task's own artifacts. No `Makefile`
target, workflow step, test, or script imports it.

Both tasks that met it deferred the decision here on purpose —
`08-08-installer-dead-code-trim/prd.md:52` ("owned by 07-25-audit-repo-tooling-ownership")
and `07-25-audit-lint-shipped-payload/design.md:39` ("its keep-vs-delete
disposition is owned by a separate task"). Keeping it would mean writing tests
and widening the lint scope for a second path to a script that is already
directly invocable, so deletion is the smaller and more honest resolution.

Consequence for the coordinating task: `07-25-audit-lint-shipped-payload`
excluded the wrapper from its lint gate pending "only if it is kept". It is not
kept, so that follow-up pointer closes with no work.

### D-4 — Fix the `check-dev-requirements-lock.py` misclassification

Discovered during planning, and included because the documentation in D-1 would
otherwise be false. `.github/trellis-provenance.json` classifies
`.github/scripts/check-dev-requirements-lock.py` under `files` (hash-pinned)
while its five siblings sit under `repoOwn` (hand-curated, editable). The
consequence is real and was reproduced against the checkout — appending a
comment and running the gate:

```
drifted: .github/scripts/check-dev-requirements-lock.py
trellis-provenance check: 1 finding(s)
```

The tree was restored and the gate returns
`ok (55 hashed, 353 tracked platform files covered)`.

So one file in the directory this task documents as "repo-own and editable" is
not editable without a provenance re-absorb. It was absorbed via `--accept` when
`07-25-audit-dependency-hygiene` added it, rather than curated into `repoOwn`.
The misclassified entry sits at `.github/trellis-provenance.json:57`, inside
`files`; its five siblings are at `:63`-`:67`, inside the `repoOwn` block that
opens at `:60` (`:61` and `:62` are `PULL_REQUEST_TEMPLATE.md` and
`dependabot.yml`). Moving it to `repoOwn` matches those siblings and is safe
**because the path is absent from the live Trellis registry today**, not because
the checker enforces that absence. Stating it precisely, since the first draft
got this backwards: `run_check` *subtracts* `repoOwn` from the registry
comparison (`check-trellis-provenance.py:228`), so `repoOwn` membership would
suppress a
future ownership collision rather than surface it. That is an argument for
keeping the list short and evidence-backed, which a repository CI script
appearing in no registry satisfies.

## Adversarial review ledger (round 1, 2026-08-10)

Host lane and Codex lane (`gpt-5.6-sol`, read-only, PRD-only scope) run in
parallel. Codex reviewed the pre-reversal draft, so C-1 and C-2 were found
independently by both lanes — the agreement is why D-2 was reversed rather than
defended.

| ID | Concern | Blocking | Disposition |
| --- | --- | --- | --- |
| C-1 | D-2's "three vendored contracts pin the path, move not available" premise is false: only the review-scope predicate hardcodes it, Makefile-target discovery precedes `scripts/` discovery, and copilot-instructions is guidance rather than an executable dependency. | yes | **addressed** — D-2 reversed to a move; the verified per-claim table replaces the assertion. Found by host lane and Codex #1 independently. |
| C-2 | D-2 weakened the "one documented home" requirement by redefining `scripts/` as an exception, so criterion 3 was satisfied only under a reinterpretation. | yes | **addressed** — the reversal removes the exception entirely; `scripts/` becomes 100% vendored and criterion 3 is met as written. Codex #2. |
| C-3 | D-4 misstated the checker: `run_check` subtracts `repoOwn` from the registry comparison (`:228`) rather than cross-checking it, so `repoOwn` can *suppress* a future collision. | no | **addressed** — D-4 now rests on verified current registry absence and says so explicitly. Codex #3. |
| C-4 | The `scripts/` test is an ownership/location invariant, not liveness; a dead file shipped by the pack would pass, so "makes criterion 2 durable" was overclaimed. | yes | **addressed** — reworded to scope the claim, liveness assigned to the reference grep, and a third assertion added that the wrapper path is absent outright. Codex #4. |
| C-5 | Validation did not prove criterion 4: `make check` shows the current bytes are clean, not that an edit to any `.github/scripts/**` file survives. | yes | **addressed** — assert every tracked `.github/scripts/**` path is in `repoOwn` and absent from `files`, since `files` membership is what makes a path drift-sensitive (`:206`). Codex #5. |
| C-6 | Criterion 1's validation was one-way: it catches an omitted vendored family but not an overbroad one that captures repo-own files. | yes | **addressed** — reverse check added, expanding each family against the tracked tree and asserting no intersection with repo-own paths. Codex #6. |
| C-7 | The filing's "17 of 19" inventory count is stale. | no | **addressed** — re-measured to 26 of 28 and annotated in Requirements rather than silently rewritten. Codex #7. |

### Round 2 (remediation)

Both lanes reran against the rewritten PRD. Round 2 falsified the round-1 claim
that nothing remained unresolved, which is recorded rather than quietly amended.

| ID | Concern | Blocking | Disposition |
| --- | --- | --- | --- |
| C-8 | C-6's own remedy was unsatisfiable: the forward check requires a vendored family to cover every installed target, while the reverse check read Trellis `repoOwn` as proof of repo-ownership — and `.github/PULL_REQUEST_TEMPLATE.md` is both. The two checks could never pass together, so criterion 1 still lacked a valid proof and the round-1 "none unresolved" line was false. | yes | **addressed** — repo-own oracle redefined as absence from all three receipts, verified against the checkout; the D-4 ordering dependency this exposes is now stated. Codex R2 #1. |
| C-9 | Citation and count drift introduced by the round-1 rewrite: `Makefile` calls four distinct `.github/scripts` files across five sites (not five files); `update-repomix` would have six siblings (not five); `repoOwn` script entries are `:63`-`:67` (not `:62`-`:66`); ledger C-3 still cited `:226`; the lint statement starts at `design.md:39` (not `:38`). | no | **addressed** — all five corrected against `sed -n` output from the checkout. Host lane independently caught the `:228` and `:57`/`:60` errors before Codex reported them. Codex R2 #2. |
| C-10 | D-2's grep postcondition was overstated: after the move the pattern also matches this PRD, which quotes the old path. | no | **addressed** — postcondition reworded to name the expected matches. Codex R2 #3. |

Codex R2 affirmed as sound: the reversed D-2 and its complete reference
enumeration, the provenance consequence, criterion 4's assertion, and the
measured counts (28 tracked `scripts/` files, 26 in each receipt, 210 installed
targets, six workflow-called repo-own scripts, an 18-line wrapper).

### Round 3 (final permitted round)

| ID | Concern | Blocking | Disposition |
| --- | --- | --- | --- |
| C-11 | The round-2 oracle was satisfiable but **unsound**. It missed Registry A entirely — 148 tracked files keyed only in `.trellis/.template-hashes.json`, including `.trellis/scripts/**` — and misclassified the two `install: "if-not-exists"` targets (`.gito/config.toml`, `.prism/rules.json`), which the spec ranks repo-owned after first install because refresh preserves them. The zero/zero result therefore did not prove criterion 1. | yes | **addressed** — the home-grown oracle is discarded for the repository's own two-registry lookup at `quality-guidelines.md:772-850`. Re-run over the tracked tree it yields 406 do-not-edit / 1002 repo-own and reproduces every documented example, including the dual-owned managed-block case. Codex R3 #1. |

Codex R3 affirmed: all round-2 citation corrections accurate, and D-4's ordering
dependency holds (`oracle_before=false`, `oracle_after_D4=true`).

Verification of the C-11 fix was run in-lane rather than by opening a fourth
automatic round, which the contract forbids: the spec's procedure reproduces the
four known classifications, and `scripts/` after D-2 and D-3 measures
`{'vendored-B': 26}` with zero repo-own entries — the exceptionless invariant
D-2 promises, proven rather than asserted.

No concern is parked or unresolved after round 3, the lanes agree, and the round
limit is respected, so implementation is unblocked. Every change landed in
`prd.md`, the only planning artifact this task has.

The three rounds carry one lesson worth generalizing beyond this task: every
oracle written from scratch here was wrong, and the correct one was already
specified in `quality-guidelines.md`. That belongs in the review-learnings pass
at ship time.

## Acceptance Criteria

- [x] CONTRIBUTING distinguishes editable source from vendored installs with concrete path families. — new section "Repo-own source vs vendored installs" lists nine do-not-edit families per registry with their upstream source, plus the four exceptions (`check.json`, the two seeded targets, the dual-owned managed block, `.gitignore`), all derived from the registries.
- [x] The wrapper is deleted or wired + tested — no unreferenced entry point remains. — deleted; `grep` leaves only archived tasks, audit records, and the test that asserts its absence. `test_dead_wrapper_stays_deleted` fails if it returns (verified by restoring it: 3 failures).
- [x] Makefile references repo-own scripts at their documented home. — `Makefile:35` now calls `.github/scripts/update-repomix`; every `.github/scripts` call site resolves and `make check` is green. `shell-syntax` was extended to cover the relocated script, which the `scripts/*.sh` glob could no longer reach (falsified: a broken script yields `Error 1`).
- [x] `.github/scripts/**` is uniformly editable: the provenance gate passes after an edit to any file in it, with no `drifted:` finding. (Added by D-4.) — probed all three representative files after the fix, each `rc=0`; the same probe produced `drifted:` before. `test_every_file_is_curated_repo_own_and_not_hash_pinned` pins it.

## Validation

- `grep -rn "se-ai-command-pack-skill-review" --exclude-dir=.git .` returns no
  executable reference after deletion — only generated maps, audit records, and
  task artifacts.
- A new `tests/test_repo_tooling_ownership.py` asserts every tracked file under
  `scripts/` is vouched by the pack — no exceptions, once D-2 lands. Stated
  precisely, because the first draft overclaimed it: this is an **ownership and
  location** invariant, not a liveness one. It cannot detect a dead entry point
  that the pack itself ships, and it deliberately fails any future repo-own
  helper placed under `scripts/`, which is the policy D-1 sets. The liveness half
  of criterion 2 is proven by the reference grep below, not by this test. The
  test reads the tracked set from `git ls-files scripts/` so untracked local
  scratch files cannot fail it. Assertions:
  1. every tracked `scripts/` path classifies as pack-vendored under the spec's
     ownership lookup — the manifest entry is the ownership decider, with
     `provenance.json` used only as the content receipt beside it; and
  2. the `scripts/` subsets of `provenance.json` and `installed-targets.txt` are
     identical, so the two receipts cannot drift apart unnoticed; and
  3. the deleted wrapper path is absent outright, so the
     specific dead wrapper this task removes cannot return by being added to a
     receipt.

  Measured today: both receipts list the same 26 `scripts/` paths, and the only
  tracked files absent from both are the two this task removes or moves
  (`se-ai-command-pack-skill-review.py`, `update_repomix`). Asserting against
  `installed-targets.txt` alone would have been the weaker check — it proves a
  path was named, not that its content came from the pack.
- The same test proves criterion 4 deterministically, which `make check` alone
  does not: a passing baseline shows the current bytes are consistent, not that
  an *edit* would survive. Assert instead that every tracked `.github/scripts/**`
  path is in `repoOwn` and in no other classification — `files` membership is
  exactly what makes a path drift-sensitive: `run_check` walks
  `manifest["files"]` at `check-trellis-provenance.py:206` and appends the
  `drifted:` finding at `:218`, so excluding a path from `files` is the property
  that makes the directory uniformly editable. The reproduced `drifted:` finding in
  D-4 is the falsifying case this assertion would have caught.
- Criterion 1 needs a reverse check, not only forward coverage. Forward: zero
  installed targets uncovered by a documented family. Reverse: no documented
  do-not-edit family matches a path that is actually repo-own. Without it, an
  overbroad family reads as correct while telling contributors not to edit files
  they own; `.github/copilot-instructions.md:45` is a live example of exactly
  that error.

  **Do not invent the oracle — the repository already specifies it.**
  `.trellis/spec/backend/quality-guidelines.md:772-850` defines a two-registry
  ownership lookup with five outcomes, and this task's checks must simply *be*
  that procedure. Two home-grown oracles were tried and both were wrong, which
  is why this is stated as a rule rather than a preference:

  - Trellis `repoOwn` as the oracle is unsatisfiable. That list means "not
    Trellis-owned", not "not vendored", so the forward check (a family must
    cover every installed target) and the reverse check would contradict on
    `.github/PULL_REQUEST_TEMPLATE.md`, verified as `sd-installed=True` and
    `trellis-repoOwn=True` simultaneously.
  - "Absent from the three receipts" is satisfiable but **unsound**. It misses
    Registry A entirely — 148 tracked files including `.trellis/scripts/**` are
    keyed in `.trellis/.template-hashes.json`, not in any of the three — and it
    misclassifies the two `install: "if-not-exists"` targets, which the spec
    ranks as repo-owned after first install because refresh preserves them
    (`installer/fileops.py:300`).

  The spec's procedure, run over the tracked tree, classifies 1408 files as
  406 do-not-edit and 1002 repo-own and reproduces every documented example:
  `.gito/config.toml` and `.prism/rules.json` as `repo-own (seeded)`,
  `.github/copilot-instructions.md` as dual-owned managed-block, and
  `.sd-ai-command-pack/check.json` as repo-own. Membership and editability come
  from the manifest entry; `provenance.json` is drift evidence, not an ownership
  decider (`:807`).

  Ordering dependency worth stating: `.github/scripts/check-dev-requirements-lock.py`
  classifies as not-repo-own today purely because of the D-4 misclassification,
  and becomes correctly repo-own once D-4 lands. D-4 is a prerequisite of this
  check, not an independent extra.

  **Satisfiability was proven, not assumed.** Both checks were run against the
  checkout, giving `FORWARD uncovered: 0`, `REVERSE repo-own captured: 0`,
  `BOTH PASS: True`. A first attempt with hand-guessed families failed in both
  directions, which is the useful result: it mis-shaped
  `.opencode/commands/sd-*.md` as `sd/**` and missed that `.gitignore` is an
  installed target. The family list in CONTRIBUTING must be derived from the
  registries and then run through this check, never written from memory.

  That first run also surfaced a concrete finding the section must encode:
  **`.sd-ai-command-pack/check.json` is repo-own**, while the three files beside
  it (`installed-targets.txt`, `manifest.json`, `provenance.json`) are installs.
  A blanket `.sd-ai-command-pack/**` do-not-edit family is therefore exactly the
  overbroad error C-6 predicted — it would tell contributors not to edit the
  sd-check registration file they own and do edit. It is the only repo-own file
  inside an otherwise-vendored directory in the whole tree, so it is the one
  exception the section has to name explicitly.
- The D-2 move updates every live reference, enumerated from the checkout rather
  than from the diff: `Makefile:35`, `tests/test_repomix.py:12`, and
  `.trellis/spec/backend/quality-guidelines.md:188`, `:2188`, `:2197`.
  `README.md:298` invokes `make repomix` and needs no change. Verified after the
  move by `grep -rn "scripts/update_repomix"` returning only the two vendored
  files, historical task records under `.trellis/tasks/archive/` and
  `.trellis/audit/`, and this PRD itself, which quotes the old path while
  explaining the move.
- `bash -n .github/scripts/update-repomix` plus a check that the relocated
  script's computed `repo_root` is the repository root, not `.github/`.
- Every path family named in the new CONTRIBUTING section is checked back
  against `installed-targets.txt` and `.github/trellis-provenance.json`, with
  zero installed targets left uncovered by a listed family.
- `make check` (test, lint, lock-check, release-check, shell-syntax,
  trellis-provenance) passes.
- The ownership test must answer identically with and without Registry A's
  receipt. The first implementation read `.trellis/.template-hashes.json`
  unconditionally and passed locally while erroring on every runner
  (`FAILED (errors=8, skipped=1)` at `564d252`) — the file is gitignored at
  `.gitignore:94`, so a checkout has one and CI never does. `make check` was
  green for the wrong reason: it ran against a file the gate cannot see. The
  spec already treats this as a known property — its lookup branches on
  `if [ -f .trellis/.template-hashes.json ]` at `quality-guidelines.md:798`
  and calls it "the machine-local Trellis hash file" at `:2366` — so the test
  violated a documented contract rather than finding a new one.

  Crashing was the lesser half. Made merely optional, the lookup would have
  inverted its verdict on the 32 paths the receipt alone covers, silently
  reclassifying vendored `.trellis/scripts/**` as repo-own on CI only. Those 32
  are bounded and contain no repo-authored path — exactly
  `.trellis/scripts/`, `.trellis/agents/`, `.trellis/config.yaml`, and
  `.trellis/workflow.md` — so they are named as a tracked substitute and the
  answer is identical in both environments. Verified in three conditions:
  receipt present `OK`, receipt hidden `OK (skipped=1)`, and the deleted
  wrapper restored under the hidden receipt still `FAILED (failures=3)`, so the
  substitute did not buy CI-stability by making the test vacuous. One assertion
  genuinely needs the receipt — that the named substitute still covers all of
  it, which is what catches a future vendored runtime file — and it skips when
  the receipt is absent rather than pretending to have run.

## Notes

- Audit findings: A-004 (P3/M), A-026 (P3/S) — .trellis/audit/report-2026-07-25.md.
- Evidence: scripts/se-ai-command-pack-skill-review.py:1, :9; Makefile:14; CONTRIBUTING.md:1.
- Planning depth: PRD-only. Documentation plus removal of dead entry points.
- No shipped-payload path (`templates/**`, `generated/**`, `installer/**`,
  `install.py`, `manifest.json`) is touched, so the release gate requires no
  version bump. `make release-check` confirms this before review.
- Follow-up (D-2 cost): two vendored Registry B files keep stale references to
  the pre-move `update_repomix` path — `scripts/sd-ai-command-pack-review-scope.sh:146`
  and `.github/copilot-instructions.md:45`. Correcting them is an upstream pull
  request against platypeeps/sd-ai-command-pack requiring explicit per-PR
  approval, so this task records the relay instead of attempting the edit.
- `docs/repomix-map.md` is gitignored and untracked (`.gitignore:30`, policy
  A-025, asserted at `tests/test_repomix.py:104`), so deleting the wrapper
  requires no repository-map regeneration and no map-freshness gate runs in CI.
- The two registries overlap in ways the CONTRIBUTING section must state rather
  than smooth over: `.github/copilot-instructions.md` and `.gitignore` are
  written by **both** vendors, and `.github/PULL_REQUEST_TEMPLATE.md` is listed
  as Trellis `repoOwn` while also being an SD-pack installed target — Trellis's
  `repoOwn` means "not Trellis's", not "not vendored".
