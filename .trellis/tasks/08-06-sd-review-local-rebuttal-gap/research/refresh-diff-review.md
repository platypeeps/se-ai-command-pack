# Research: sd-ai-command-pack refresh diff review (0.64.3 → 0.64.32)

- **Query**: Refresh-diff unit review required by the task PRD — name behavioral
  changes to the sd-check gate, the local provider set, severity mapping, remote
  disposition handling, and thread resolution; summarize the `--local-disposition`
  rebuttal control; list every changed file.
- **Scope**: internal (working-tree diff vs `HEAD`, cross-checked against the
  pinned upstream worktree)
- **Date**: 2026-08-09

## Inputs

| Input | Value |
|---|---|
| Installed version at `HEAD` | `0.64.3` (`.sd-ai-command-pack/manifest.json`) |
| Refreshed version in working tree | `0.64.32` |
| Pinned upstream source | `/private/tmp/claude-501/-Users-sven-repos-platypeeps-se-ai-command-pack/41ff720a-de03-4afb-aae6-41e543204d3d/scratchpad/sd-pack-v0.64.32` (tag `v0.64.32`) |
| Changelog range read | `CHANGELOG.md` headings `0.64.4` … `0.64.32` (lines 3–632) |
| Changed files | 41 total: **36 pack payload/manifest files** + 5 `.trellis/` files |

**File-count note.** The task brief says 34 payload files. The actual
non-`.trellis/` change set is **36**. The two likely uncounted are
`.sd-ai-command-pack/manifest.json` and `.sd-ai-command-pack/provenance.json`
(manifest/provenance rather than payload). Full list in **Files changed** below.

**Payload fidelity.** Every changed payload file except one was compared
byte-for-byte against `<upstream>/templates/<path>` with `cmp`. All 20 scripts,
all 6 `.agents/skills/` files, `docs/SD_AI_COMMAND_PACK.md`, and
`.claude/sd-ai-command-pack/planning-adversarial-review.md` are **identical** to
the upstream templates. The 6 `.claude/skills/` files have no `templates/`
counterpart (they are generated adapters) but are byte-identical to their
`.agents/skills/` twins. So the refresh is a clean upstream import with no
in-flight local edits — which is exactly why the finding below matters.

---

## ⚠ Blocking-class finding: the refresh reverts local commit `bc01bc2`

This is the single most consequential thing in the diff and it is **not** in the
upstream changelog, because it is a downstream-only patch.

`git log 3d2341b..HEAD -- scripts/ .claude/skills/ .agents/skills/ docs/SD_AI_COMMAND_PACK.md`
shows exactly one local commit that patches a pack payload script since the
0.64.3 refresh:

```
bc01bc2 fix(review): recompute deterministic sd-check every run, don't serve stale cache
```

That commit added `_resolve_check()` to `scripts/sd-ai-command-pack-review.py`.
The refresh removes it and restores upstream's memoized form:

```diff
-def _resolve_check(repo: Path, state: dict[str, Any], state_path: Path) -> dict[str, Any]:
-    # Always recompute the deterministic sd-check. ... Memoizing the report
-    # would serve a stale pass/fail after those inputs change at an unchanged
-    # head, which false-blocks review.
-    check = _run_check(repo)
...
-    check = _resolve_check(repo, state, state_path)
+    if state.get("check") is None:
+        check = _run_check(repo)
+        _advance(state_path, state, "check", check=check)
+    check = state["check"]
```

Confirmed upstream-side: `templates/scripts/sd-ai-command-pack-review.py:1827`
in the v0.64.32 worktree is `if state.get("check") is None:` — upstream never
adopted the fix, so the refresh is a genuine revert, not a merge artifact.

**Verified consequence.** `python3 -m pytest tests/test_review_coordinator.py -q`
against the refreshed working tree:

```
E       AttributeError: module 'sd_review_coordinator' has no attribute '_resolve_check'
...
5 failed in 0.04s
```

All five locally-authored regression tests (including the AC1 test that was
proven to fail pre-fix) now fail on import-time attribute lookup.

**Partial upstream overlap.** Upstream fixed the two *live inputs* the local
patch named, but at their source rather than at the memoization layer:

- `knowledge.obsidian-kb` determinism → 0.64.22 advisory downgrade (see below).
- `pack.review-scope` stale PR body → 0.64.4 finding #6 makes
  `sd-ai-command-pack-review-scope.sh` ignore a CLOSED/MERGED same-branch PR.

The memoization itself is unchanged upstream, so any other live-input drift at
an unchanged head is still served from cache. Whether that residual is
acceptable is a decision for the task, not a finding of this review.

**Local relevance of the KB half is real, not hypothetical**: `.obsidian-kb` in
this repo is an absolute external symlink
(`.obsidian-kb -> /Users/sven/Documents/sdelmas-llm-wiki/raw/se-ai-command-pack`),
so the 0.64.22 advisory downgrade does apply here.

---

## Named behavioral changes to the five required surfaces

### (a) The deterministic sd-check gate — **CHANGED (three items)**

**a1. External-symlinked Obsidian KB: failing row moved from blocking to advisory.**
Confirmed as reported in the brief.

> `## 0.64.22 - 2026-08-06`
> "Downgrade `sd-check`'s `knowledge.obsidian-kb` freshness row to advisory when
> `.obsidian-kb` is an absolute symlink to a vault outside the repository. That
> vault is gitignored, never shipped, and mutates independently of repo HEAD, so
> `update-spec-kb.py --check` fails non-deterministically against it … Observed on
> `platypeeps/anomaly-metric-creator` #316 and #325."
>
> "The downgrade is narrow. A new `_is_external_symlink(kb_root, repo)` helper is
> true only when `kb_root` is a symlink whose `resolve(strict=False)` target lands
> outside the repository tree. Only a *failing* row for such a path becomes a
> non-blocking `skipped` … `skipped` is absent from `AGGREGATE_PRECEDENCE`, so it
> never contributes to the blocking verdict. A passing row stays `passed`."

In the diff (`scripts/sd-ai-command-pack-check.py`), `_is_external_symlink` is
added near the `_result_row` helpers, and the `knowledge.obsidian-kb` row builder
becomes:

```python
if _is_external_symlink(kb_root, repo) and row.get("status") == "failed":
    return _result_row(
        "knowledge.obsidian-kb", "builtin", "skipped",
        diagnostic=("advisory: external-symlinked .obsidian-kb drift is "
                    "non-deterministic and never shipped; " + str(row.get("diagnostic", ""))),
        remediation=..., exit_code=..., command=..., duration_ms=...,
    )
return row
```

Original `diagnostic`, `remediation`, `exitCode`, `command`, and `durationMs` are
preserved on the downgraded row. In-repo symlinks and real tracked directories
keep blocking; a broken link resolves to its declared target (external →
advisory, in-repo → blocking).

**a2. Per-run worktree content-hash cache (performance, with one stated
granularity trade).**

> `## 0.64.18 - 2026-08-05`
> "Cut the per-check-row worktree re-hash in `sd-ai-command-pack-check.py`
> (A-101, R1/R2). … A per-run content-hash cache now keys each regular file's
> content digest by a cheap `(st_mode, st_size, st_mtime_ns)` signature … the run
> performs exactly two full content passes … **Run-level granularity trade:** the
> cheap signature cannot see a same-size, mtime-preserving rewrite that happens
> between rows, so a per-row snapshot can miss it and no longer attribute the
> mutation to a specific check row. The run's final snapshot runs against a fresh
> cache and re-hashes from scratch, so it still fails the run for all three
> mutation classes … only per-row attribution for that one case is traded away.
> Symlinks are always read fresh, so every retarget is still caught at every
> snapshot."

Diff: new `_WorktreeHashCache` class; `_hash_path`, `_tracked_worktree_digest`,
`_index_digest`, and `state_snapshot` gain an optional `cache` parameter;
`build_report` creates one `run_cache` for the whole run and deliberately passes
**no** cache to the authoritative `final = state_snapshot(repo)`.

**a3. `pack.review-scope` no longer trusts a CLOSED/MERGED same-branch PR body.**

> `## 0.64.4 - 2026-08-04`
> "Review scope resolution (finding #6): `sd-ai-command-pack-review-scope.sh` now
> requests and requires `state` from `gh pr view` and ignores a CLOSED PR whose
> head is the same branch, so a stale closed PR body can no longer redirect the
> review scope of a fresh open PR on that branch."

Diff adds `state` to the `gh pr view --json` field list, a new
`unknown:pr_closed` scope state, and a matching `check_pr_body_scope` branch that
behaves like "no open PR": `fail` when the gh mode is required, otherwise `warn`.

**Also relevant to the gate, though not in `check.py`:** the housekeeping merge
gate's KB refresh gained a read-only advisory skip.

> `## 0.64.4` — "Housekeeping merge gate (finding #7): a read-only Obsidian KB
> target no longer hard-blocks a merge. … an `EACCES`/`EROFS` refresh failure is
> recorded as an advisory skip with a fix command; every other refresh failure
> (corrupt vault, disk full, broken symlink) still blocks."

`sd-ai-command-pack-housekeeping.sh` now captures the helper's combined output,
re-prints it, and on `refresh_status == 2` matching
`errno 13|permission denied|errno 30|read-only file system|eacces|erofs` emits
`add_action kb_refresh_skipped` and returns 0 instead of `add_anomaly
kb_refresh_failed`.

### (b) The local provider set — **NONE FOUND**

Compared `HEAD` vs the refreshed
`scripts/sd-ai-command-pack-review-local.py` for every provider token. The
adapter allow-list is unchanged in both:

- `if adapter not in {"prism", "gito", "argv"}:` (HEAD line 387, new line 398)
- default plan entries `"id": "prism"` / `"id": "gito"` — unchanged
- `if provider.identifier in {"prism", "gito"}` — unchanged
- `_prism_payload` / `_gito_payload` dispatch — unchanged
- `MAX_PROVIDERS = 16` — unchanged

Every hit shifts by exactly the +11 lines the new module preamble adds. No
provider added, removed, or renamed; the Codex-CLI lane remains a caller-supplied
`argv` provider rather than a built-in adapter. No changelog entry between
0.64.4 and 0.64.32 touches the provider set.

### (c) Severity mapping — **NONE FOUND**

`FINDING_SEVERITY_RANK = {"unspecified": 0, "low": 1, "medium": 2, "high": 3}` is
untouched (it appears only as an unchanged context line in the diff). The Prism
integer→name map `{1: "low", 2: "medium", 3: "high"}`, the `None → "unspecified"`
branch, the casefold-then-validate string branch, the 40-char bounding of raw
severity strings, and the max-severity merge
(`if FINDING_SEVERITY_RANK.get(severity, 0) > FINDING_SEVERITY_RANK.get(str(row["severity"]), 0)`)
are all present at identical relative positions in both versions (HEAD lines
1535–1816, new lines 1546–1827 — a uniform +11 shift). No changelog entry in
range mentions severity.

### (d) Remote disposition handling — **NONE FOUND**

In `scripts/sd-ai-command-pack-review.py` the diff's hunks do not touch
`_parse_remote_dispositions`, the `"remoteDispositions": {}` state seed, the
`supplied_dispositions` / `stored_dispositions` merge, `_advance(...,
remoteDispositions=merged_dispositions)`, or the terminal-bucket accounting
(`elif disposition in {"rebutted", "resolved"}`). Every remote-disposition symbol
appears in both versions at a uniform +10/+26 line shift with identical text. The
one remote-adjacent change is *additive and separate*: a new
`_parse_local_dispositions` sits immediately above `_parse_remote_dispositions`
and deliberately mirrors its grammar.

`scripts/sd-ai-command-pack-pr-eligibility.py` gains merge-state diagnosis that
touches `mergeStateStatus` classification, not review dispositions:

> `## 0.64.4` — "Merge-eligibility (finding #2): … now classifies a PR that GitHub
> reports as `BLOCKED` but `MERGEABLE`. A non-clean merge state is given an
> actionable diagnostic — `merge_blocked_conflicts`, `merge_blocked_out_of_date`,
> `merge_blocked_conversation`, `merge_blocked_review`, or
> `merge_state_not_clean` — instead of a blanket skip, while the state stays
> `blocked` and such a PR is still never reported merge-eligible."

The new `classify_non_clean_merge_state` docstring states the contract inline:
"ADDITIVE-ONLY: this never changes the verdict. Every caller still returns
`status="blocked"` and never reaches `gh pr merge`". The `gh pr view --json`
field list gains `mergeable`, parsed advisory-only (`None` when absent).

### (e) Thread resolution — **NONE FOUND in `sd-review`; one collection change elsewhere**

In `scripts/sd-ai-command-pack-review.py`, thread resolution is byte-for-byte
unchanged, only line-shifted by +9:

- the GraphQL `reviewThreads(first:100 …) { nodes { id isResolved isOutdated … } }`
  query string (HEAD 1315 → new 1324) is character-identical
- `"resolved": bool(row.get("isResolved"))` (HEAD 1393 → new 1402)
- the unresolved predicate `if not row["resolved"] and not row["outdated"] and row["comments"]`
  (HEAD 1519 → new 1528)
- `_nested_thread_comments`, `_collect_review_threads`, the 1000-row caps, and the
  `unresolved` counting/reporting block — all unchanged

The only thread-related behavioral change in the refresh is in a **different**
tool, `sd-review-learnings`, and it is collection batching rather than resolution:

> `## 0.64.11 - 2026-08-04`
> "Batch `sd-review-learnings` review-thread collection into aliased GraphQL
> queries (up to `GITHUB_REVIEW_THREAD_BATCH_SIZE = 20` PRs per request) instead
> of one `gh` subprocess per PR … a whole-batch failure … or a per-alias `null`
> (partial failure) falls back to the pre-batch single-PR query for the affected
> PRs — one PR never drops the rest. Per-PR truncation and input ordering are
> preserved; identical learnings output on a fixed PR window."

`scripts/sd-ai-command-pack-pr-eligibility.py` also gains a `collect_threads`
region (+112 lines) feeding `merge_blocked_conversation`; it reads thread state
for merge diagnosis and does not resolve threads.

---

## The rebuttal control itself: `--local-disposition`

> `## 0.64.26 - 2026-08-07`
> "Give verified-false local review findings a rebuttal channel. `sd-review`
> instructs the caller to verify every finding and to rebut rather than comply
> when one is wrong, but only the remote stage could act on that:
> `--remote-disposition <id>=rebutted` had no local counterpart. A local provider
> false positive therefore held `remoteGate: actionable-local-findings` shut with
> no way past it short of editing the file the provider misread.
> `--local-disposition <stable-id>=rebutted` closes that, with the same grammar
> and the same single accepted value. A rebutted finding stays in the receipt as
> `rebutted` under `disposition.localDispositions`, so the judgement remains
> auditable; the gate now blocks on findings left outstanding rather than on the
> provider's aggregate outcome, while a provider reporting findings but listing
> none still blocks. An id matching no finding at that head is an error rather
> than a silent no-op, because stale ids copied from an earlier head are the way
> this would otherwise go wrong. Observed on PR #353 …"

### How it lands in the installed scripts

**Grammar / validation** — duplicated deliberately in both
`sd-ai-command-pack-review.py` (coordinator, raises `ReviewError`) and
`sd-ai-command-pack-review-local.py` (stage, raises `ReviewInputError`), with
identical rules:

```python
LOCAL_DISPOSITION_VALUES = frozenset({"rebutted"})

identifier, separator, disposition = value.rpartition("=")
if (not separator or not identifier or len(identifier) > 240
        or any(ord(character) < 32 for character in identifier)
        or disposition not in LOCAL_DISPOSITION_VALUES):
    raise ...("local dispositions must use <stable-id>=rebutted")
if identifier in dispositions:
    raise ...("local disposition ids must be unique")
```

`rpartition("=")` means the stable id may itself contain `=`; only the final `=`
splits. Ids are capped at 240 chars and must contain no control characters.

**CLI surface** — `parser.add_argument("--local-disposition", action="append",
default=[])` is added to both scripts. The coordinator re-serializes each
validated pair into the stage invocation:

```python
for identifier, disposition in _parse_local_dispositions(args.local_disposition).items():
    command.extend(("--local-disposition", f"{identifier}={disposition}"))
```

So the coordinator validates once and the stage validates again on receipt.

**Application** — `_apply_local_dispositions(findings, dispositions)` in the
stage indexes findings by `str(item.get("id"))`, and refuses unknown ids rather
than ignoring them:

```python
unknown = sorted(set(dispositions) - set(known))
if unknown:
    raise ReviewInputError(
        "local disposition ids match no finding at this head: " + ", ".join(unknown[:8]))
```

Matched findings get `item["disposition"] = "rebutted"`; the applied map is
recorded at `receipt["disposition"]["localDispositions"]`. Provider evidence is
never mutated or deleted.

**Gate recomputation** — `_remote_gate` gains a keyword-only
`findings_present: bool = True` and inverts what it keys on:

```diff
-    if outstanding or outcome == "findings":
+    if outstanding or (outcome == "findings" and not findings_present):
         return {"state": "blocked", "reason": "actionable-local-findings"}
```

So the gate now blocks on the *count of findings left outstanding*, not the
provider's aggregate `outcome`. The `not findings_present` clause preserves the
old behavior for the degenerate case a provider reports `findings` while listing
none — evidence nobody can inspect or rebut still blocks.

**Receipt reuse path** — `_redispose_receipt(receipt, dispositions,
local_policy)` lets a rebuttal apply to an already-stored receipt without
re-running any provider: it re-applies the dispositions, recomputes
`disposition["outstanding"]`, merges into `disposition["localDispositions"]`,
recomputes `receipt["remoteGate"]`, and the caller re-persists via
`_atomic_json`. It raises `ReviewInputError` if the stored receipt has no
`findings` list or no `disposition` block. Rebuttals apply to one attempt at one
head; a later head requires its own.

**Operator guidance** shipped in `.agents/skills/sd-review/SKILL.md` (and its
`.claude/skills/` mirror):

> "A local provider finding you have verified false takes the matching
> `--local-disposition '<stable-id>=rebutted'` pair. The bar is the same as the
> remote one and it is high: rebut only after checking the cited path and line in
> the checkout and finding the claim untrue there — a finding that is merely
> low-severity, inconvenient, or hard to fix is outstanding, not rebutted. … Two
> provider misreads are common enough to name … fenced code blocks quoted inside
> a Markdown document read as if they were the diff's own source, and a cited
> defect that is simply not present at the cited line."

The skill's header count changes from "Two coordinator-only evidence flags" to
"Three".

---

## Other notable behavioral changes in the refresh

Recorded so nothing passes silently. Grouped by whether they can change an
observable result.

### Payload verdict-key vocabulary — dual-emit, breaking in 0.66.0

> `## 0.64.17 - 2026-08-05` — "Unify the `outcome`/`status` vocabulary across
> emitted payload envelopes (A-077). One rule now holds at the top level of every
> emitted document: the `outcome` key carries a verdict and `status` is reserved
> for an embedded sd-status document. … the housekeeping result's embedded enum
> `outcome.status` is renamed to `outcome.verdict` … The review-local stage report
> converges its top-level verdict from `status` onto `outcome`. Both renames ship
> additively: the old keys are still emitted for one release and are recorded in
> `DEPRECATED_PAYLOAD_KEYS` with `removed_version 0.66.0`."

Concretely: `sd-ai-command-pack-review-local.py` now emits both `outcome` and a
`status` alias in `_report`, `_invalid_report`, and `_cancelled_report`, and
prints `report['outcome']`. `sd-ai-command-pack-review.py` reads
`local.get("outcome", local.get("status"))`. `housekeeping-result.py`
`classify_outcome` returns both `verdict` and `status`. Any downstream consumer
reading `outcome.status` / review-local `status` must migrate before 0.66.0.

### Work-loop lifecycle fix

> `## 0.64.28 - 2026-08-08` — "Let `stop` retire a paused work-loop run. `pause`
> releases the ownership lock by design, but `stop` reached `require_lock` through
> `mutate_state` and demanded one back, so a paused run could not be stopped at all
> … The same defect blocked `reconcile`, which is worse: `references/run-recovery.md`
> routes a stopped or red run *to* `reconcile`, so the documented recovery path
> could not be walked at all. … `stop` runs `release_lock` unconditionally after
> its mutation, so every status it can set — `paused`, `stopped`, and `completed` —
> ends lockless".

Diff: `LOCK_RELEASING_STATUSES` added, `mutate_state` gains
`released_lock_statuses`.

### Session recorder derives commits when `--commit` is omitted

> `## 0.64.27 - 2026-08-07` — "recording a session without `--commit` wrote
> `add_session.py`'s '(No commits - planning session)' placeholder, and the
> final-bundle validator then rejected that same session with
> `journal_commit_missing`. … Omitting `--commit` now derives the unrecorded work
> commits on HEAD — stopping at the first commit a journal already cites, and
> skipping commits confined to `.trellis/workspace` … It declines, preserving the
> previous behavior, whenever the answer is not obvious".

> `## 0.64.29 - 2026-08-08` — "Teach the record-session wrapper … to insert the
> Testing / Next Steps journal sections when absent: Trellis >=0.6.14 omits
> sections scaffolded empty by <=0.6.7."

### `sd-review-learnings` narrowing refusal (behavior gate)

> `## 0.64.27` — "the managed block is rendered wholesale from whatever GitHub
> scope the run requested, so `--github-pr N` … renders a block holding only that
> PR's clusters. … An update that would delete clusters already recorded in the
> snapshot is now refused, naming them, with `--allow-narrowing` to accept the
> deletion deliberately. Scan and `--dry-run` are unaffected".

> `## 0.64.12 - 2026-08-04` — unsafe planning changed-path evidence now routes
> through `_print_early_failure` under the `sd-review-learnings:planning` phase
> "instead of an uncaught `ValueError` traceback".

### PR-eligibility slug derivation actually happens now

> `## 0.64.27` — "the probe never derived a repository slug. It reported
> `github_repository_unavailable` with the diagnostic 'could not derive GitHub
> repo from origin' — claiming an attempt that never happened — on every
> repository with an SSH remote … The probe now derives from `git remote get-url`
> with a parser held to byte-for-byte parity with that shell twin".

### New review-preflight rule: root-task `base_branch`

> `## 0.64.30 - 2026-08-08` — "a changed active task record with no parent must
> target the repository default branch or carry a recorded
> `meta.base_branch_exemption` reason. The default branch resolves from the new
> `SD_AI_COMMAND_PACK_DEFAULT_BRANCH` variable …, then from the `origin/HEAD`
> symbolic ref, and the rule skips itself when neither source resolves."

**This is a new way for the preflight to fail.** Any active root task in this
repo whose `base_branch` names a feature branch will now be flagged unless
`origin/HEAD` and `SD_AI_COMMAND_PACK_DEFAULT_BRANCH` both fail to resolve.

### Gito local-review scope widened (twice)

> `## 0.64.21 - 2026-08-06` — "The exclusion is now the copied/generated boundary
> rather than the whole directory … now reviewable: active `.trellis/tasks/**`
> artifacts and `.trellis/spec/**`. Consequence to expect: task- and spec-only
> changes now cost a local provider round they previously skipped, and Gito may
> raise findings on PRD, design, implementation-plan, and spec prose it never saw
> before. `.gito/config.toml` installs `if-not-exists`, so an existing consumer
> keeps its current file; apply the same narrowing by hand to opt in."

> `## 0.64.24 - 2026-08-06` — "Stop excluding `.trellis/workspace/**` from the
> Gito local-review scope. … Every finalization PR therefore reached Gito with
> nothing in scope, which exits 0 without a structured report and surfaces as
> `local provider failure blocks remote routing`".

**Caveat:** `.gito/config.toml` is `if-not-exists` and is **not** in this
refresh's change set, so neither widening takes effect here automatically. This
is the direct cause of the false-positive class that motivated
`--local-disposition` (a provider reading quoted Markdown fences as source).

### State-root consolidation — operator action on Windows / custom root

> `## 0.64.20 - 2026-08-06` — "`SD_AI_COMMAND_PACK_STATE_HOME` now moves *every*
> private state surface, not only the work-loop ledger. `fleet-timing` and
> `fleet-controller` previously ignored it. … **Operator action — one-time state
> move.** … On POSIX with `SD_AI_COMMAND_PACK_STATE_HOME` unset, nothing moves".

Not applicable here unless the variable is set or the host is Windows.

### Secret redaction widened

> `## 0.64.15 - 2026-08-05` — "the lib's `_ENVIRONMENT_SECRET_RE` missed
> fine-grained GitHub PATs (`github_pat_…` — `gh[pousr]_` excludes the `i`), Slack
> tokens, `sk-` keys, PEM private-key blocks, and most `key: value` shapes, so
> those leaked verbatim into agent-visible `environment_blocked` diagnostics."
> Both consumers now derive from one `_SECRET_SHAPES` table; the lib substitutes
> (fail-open), fleet-timing rejects (fail-closed).

### `sd-status` gains a worktree inventory (additive)

> `## 0.64.32 - 2026-08-09` — "an additive `git.worktrees` JSON block … plus a
> `git.branchesHeldElsewhere` list … Read-only throughout … `--json` stays schema
> version 2 (additive keys)."

> `## 0.64.29` — "Adopt `task.py current --json` in the status collector … with a
> prose-path fallback for consumer repositories still on Trellis <=0.6.7 that
> reject the flag."

### `sd-fix-ci` per-job dispatch protocol (skill prose)

> `## 0.64.7 - 2026-08-04` — "CI triage now fans out one read-only sub-agent per
> failing job … Workers return a typed `real-code | flake | infra |
> stale-baseline` classification … Fan-out is bounded to waves of at most six
> concurrent workers".

The SKILL.md now forbids the whole-run `gh run view <run-id> --log-failed` in
favor of per-job `gh run view -j <job-id> --log-failed`.

### Planning adversarial review: `< /dev/null` now required

> `## 0.64.23 - 2026-08-06` — "Require `< /dev/null` on the `codex exec`
> invocation … In a background Bash task stdin is not a TTY, so `codex exec`
> treats it as piped input, prints `Reading additional input from stdin...`, and
> blocks indefinitely … reporting such a run as `Codex: failed` records an absent
> second opinion as an attempted one."

**Directly relevant to this repo**, whose
`.claude/rules/sd-planning-adversarial-review.md` delegates to
`.claude/sd-ai-command-pack/planning-adversarial-review.md` — the file this
refresh updates.

### Behavior-preserving consolidations (no observable change claimed)

- `0.64.19` — git subprocess invocation consolidated into `run_git_minimal` /
  `run_git_cached` (`review-local`, `surface-check`, `install-audit`,
  `work-loop`, `fleet-controller`, `fleet-publish`). In `review-local.py` the
  `git check-ignore` call passes `stderr=None` specifically to preserve the
  pre-migration inherited-stderr behavior.
- `0.64.16` — one `atomic_write_text` / `default_text_file_mode` owner in the
  lib; `record-session` and `update-spec-kb` drop their 31-line copies for the
  hardened 67-line writer (cross-device guard, parent-dir fsync, `revalidate`).
- `0.64.18` (second item) — `pr-body-scope` `ScopeRule` partitions patterns into
  a literal `frozenset` + glob tuple and caches its hash; "Classification output
  is byte-identical."
- `0.64.10` — `.claude/hooks/*` classified as copied/generated in the `.mjs`
  preflight to match the shell classifier.
- `0.64.6` — redundant `nearestAnchorFailure === null` guard removed;
  "Behavior-preserving."
- `0.64.5` / `0.64.4` finding #11 — sibling-loader `ENOTDIR` now reports
  `missing` rather than `non_regular`; "Fail-closed refusal is unchanged; only
  the diagnostic reason/message differs."
- `0.64.31` — git-caused `*_unavailable` preflight findings enriched with
  command, exit status, and bounded stderr; "Diagnostics only: reason codes,
  receipt schema, statuses, and dispositions are unchanged."
- `0.64.13` — `sd-status fleet` collection parallelized in a bounded
  `ThreadPoolExecutor`; input ordering and per-row content unchanged, but a
  raising consumer is now isolated to a degraded `unavailable` row instead of
  aborting the run.
- `0.64.8`, `0.64.9`, `0.64.14` — manifest `agent` artifact kind (pack ships zero
  agent bodies, manifest byte-identical), `fleet-refresh.operator-policy`
  structured question registration, and audit-scope documentation. Docs/plumbing.

---

## Files changed

36 pack files. `IDENTICAL` below means byte-identical to the pinned upstream
`templates/` copy (or, for `.claude/skills/`, to its `.agents/skills/` twin).

### `scripts/` (20)

| File | Δ | Character |
|---|---|---|
| `sd-ai-command-pack-check.py` | +123/−17 | **Behavioral** — external-symlink KB advisory downgrade (0.64.22) + per-run hash cache (0.64.18) |
| `sd-ai-command-pack-review-local.py` | +141/−19 | **Behavioral** — `--local-disposition`, `_remote_gate` keyed on outstanding count, `outcome`/`status` dual-emit, git-invocation migration |
| `sd-ai-command-pack-review.py` | +38/−23 | **Behavioral + regression** — adds `--local-disposition` passthrough and `outcome` fallback read; **removes local `_resolve_check`** (reverts `bc01bc2`) |
| `sd-ai-command-pack-review-scope.sh` | +35 | **Behavioral** — requires `state` from `gh pr view`, adds `unknown:pr_closed` (0.64.4 #6) |
| `sd-ai-command-pack-housekeeping.sh` | +21/−2 | **Behavioral** — EACCES/EROFS KB refresh becomes advisory skip (0.64.4 #7) |
| `sd-ai-command-pack-housekeeping-result.py` | +21/−2 | **Behavioral (payload key)** — `outcome.verdict` added, `outcome.status` kept as deprecated alias (0.64.17) |
| `sd-ai-command-pack-pr-eligibility.py` | +158 | **Behavioral** — `mergeable` field + `classify_non_clean_merge_state` (0.64.4 #2), real slug derivation (0.64.27); verdict explicitly unchanged |
| `sd-ai-command-pack-record-session.py` | +186 | **Behavioral** — derives commits when `--commit` omitted (0.64.27), inserts Testing/Next Steps sections (0.64.29), shared `atomic_write_text` |
| `sd-ai-command-pack-review-learnings.py` | +356 | **Behavioral** — batched aliased GraphQL thread collection (0.64.11), narrowing refusal + `--allow-narrowing` (0.64.27), planning-evidence failure routing (0.64.12), drops local `atomic_write_text` |
| `sd-ai-command-pack-review-preflight.mjs` | +231 | **Behavioral** — root-task `base_branch` rule (0.64.30), git-failure diagnostics enrichment (0.64.31), `.claude/hooks/*` classification (0.64.10), redundant-guard removal (0.64.6) |
| `sd-ai-command-pack-status.py` | +385 | **Behavioral (additive)** — `git.worktrees` + `branchesHeldElsewhere` and `==> Worktrees` rendering (0.64.32), `task.py current --json` adoption with fallback (0.64.29), parallel fleet collection (0.64.13), loader diagnostics |
| `sd-ai-command-pack-work-loop.py` | +142 | **Behavioral** — `stop`/`reconcile` on lock-released runs (0.64.28), shared state-root ladder (0.64.20), git-invocation migration |
| `sd_ai_command_pack_lib.py` | +539 | **Behavioral (shared)** — `declare_verdict_domain`/`VERDICT_CORE`/`DEPRECATED_PAYLOAD_KEYS` (0.64.17), `run_git_minimal`/`run_git_cached` (0.64.19), `resolve_state_root`/`ensure_private_directory` (0.64.20), hardened `atomic_write_text` (0.64.16), `_SECRET_SHAPES` redaction (0.64.15) |
| `sd-ai-command-pack-pr-body-scope.py` | +84 | Performance — `ScopeRule` literal/glob partition + cached hash; output byte-identical (0.64.18) |
| `sd-ai-command-pack-recovery-artifacts.py` | +99 | Mechanical/diagnostic — state-root wrappers raise `RecoveryError`, schema-version mismatch reports expected-vs-actual |
| `sd-ai-command-pack-surface-check.py` | +75 | Mechanical/diagnostic — git-invocation migration, `ENOTDIR` → `missing` loader reason |
| `sd-ai-command-pack-install-audit.py` | +14 | Mechanical — git-invocation migration, `SOURCE_ONLY_ALLOWED_PACK_FILES` entry |
| `sd-ai-command-pack-toolchain.sh` | +77 | **Behavioral (error path)** — data-driven `cache-env` key set (0.64.16), re-invokes `cache-env --json` on cache-setup failure and surfaces validated `recoveryAction` (0.64.15) |
| `sd-ai-command-pack-shell-lib.sh` | +24 | Mechanical — `prepare_tool_cache_env` derives keys from `cache-env` (0.64.16) |
| `sd-ai-command-pack-update-spec-kb.py` | +43 | Mechanical — drops local `atomic_write_text`/`default_text_file_mode` for the shared hardened writer (0.64.16) |

### `.agents/skills/` (6) — all IDENTICAL to upstream templates

| File | Δ | Character |
|---|---|---|
| `sd-review/SKILL.md` | +16/−1 | Doc (operator contract) — documents `--local-disposition`, its verification bar, and the two named provider misreads |
| `sd-fix-ci/SKILL.md` | +57/−9 | Doc (operator contract) — per-job dispatch protocol, per-job log fetching, read-only workers, wave bound of 6 |
| `sd-housekeeping/SKILL.md` | +4/−3 | Doc — `outcome.status` → `outcome.verdict` with deprecation note |
| `sd-status/SKILL.md` | +4 | Doc — worktree inventory reporting requirement |
| `sd-help/references/structured-questions.md` | +13 | Doc (generated) — adds `fleet-refresh.operator-policy` decision |
| `sd-help/references/command-catalog.md` | +1/−1 | Mechanical (generated) — bundled version `0.64.3` → `0.64.32` |

### `.claude/` (7)

| File | Δ | Character |
|---|---|---|
| `.claude/sd-ai-command-pack/planning-adversarial-review.md` | +25 | Doc (operator contract) — `< /dev/null` requirement, hang signature, `-o <file>` suggestion |
| `.claude/skills/sd-review/SKILL.md` | +16/−1 | Mirror of `.agents` twin (verified identical) |
| `.claude/skills/sd-fix-ci/SKILL.md` | +57/−9 | Mirror |
| `.claude/skills/sd-housekeeping/SKILL.md` | +4/−3 | Mirror |
| `.claude/skills/sd-status/SKILL.md` | +4 | Mirror |
| `.claude/skills/sd-help/references/structured-questions.md` | +13 | Mirror |
| `.claude/skills/sd-help/references/command-catalog.md` | +1/−1 | Mirror |

### Docs + manifests (3)

| File | Δ | Character |
|---|---|---|
| `docs/SD_AI_COMMAND_PACK.md` | +33/−4 | Doc — `--allow-narrowing`, pack-vouch ownership boundary, `outcome.verdict`, `SD_AI_COMMAND_PACK_DEFAULT_BRANCH` |
| `.sd-ai-command-pack/manifest.json` | +1/−1 | Mechanical — version `0.64.3` → `0.64.32` |
| `.sd-ai-command-pack/provenance.json` | +35/−35 | Mechanical — version + sha256 rows for the changed targets |

### Out of scope for this review (5 `.trellis/` files, not pack payload)

`.trellis/spec/backend/quality-guidelines.md`,
`.trellis/tasks/08-06-sd-review-local-rebuttal-gap/{check.jsonl,implement.jsonl,prd.md,task.json}`.

---

## Verification performed

| Check | Result |
|---|---|
| `cmp` every changed payload file vs `<upstream>/templates/<path>` | 20/20 scripts, 6/6 `.agents` skills, docs, and adversarial-review contract **IDENTICAL** |
| `cmp` each `.claude/skills/` file vs `.agents/skills/` twin | 6/6 **MIRROR-OK** |
| `git log 3d2341b..HEAD -- scripts/ .claude/skills/ .agents/skills/ docs/…` | 1 payload-patching local commit found: `bc01bc2` |
| `grep -n "_resolve_check" <upstream>/templates/scripts/…review.py` | no match — the revert is genuine |
| `python3 -m pytest tests/test_review_coordinator.py -q` | **5 failed** — `AttributeError: module 'sd_review_coordinator' has no attribute '_resolve_check'` |
| Provider / severity / remote-disposition / thread-resolution symbol comparison, `HEAD` vs refreshed | uniform line shift only; text identical at every site |
| `ls -la .obsidian-kb` | absolute external symlink → 0.64.22 advisory downgrade applies in this repo |

## Caveats / not found

- **Not verified**: whether the 0.64.30 root-task `base_branch` rule actually
  fires against this repo's current active tasks. It depends on `origin/HEAD`
  resolving and on each active root task's recorded `base_branch`; a full
  preflight run would settle it, and this review did not run one.
- **Not verified**: runtime behavior of `--local-disposition` end to end. The
  control was read from source and the changelog; no local review round was
  executed against a real provider finding.
- **Not verified**: whether the other repo test suites pass after the refresh.
  Only `tests/test_review_coordinator.py` was executed, chosen because the diff
  showed it targeted the reverted symbol.
- **`.gito/config.toml` is not in the change set.** The 0.64.21/0.64.24 scope
  widenings install `if-not-exists` and therefore do not apply to this repo
  automatically. Whether that matters depends on whether this repo wants the
  `.trellis/tasks/**` + `.trellis/spec/**` review surface.
- **File count differs from the brief** (36 payload/manifest files vs the stated
  34); see the note at the top.
- No decision or recommendation is offered here on how to handle the `bc01bc2`
  revert — this document only establishes that it happens, that it is genuine
  against upstream, and that it breaks five local tests.
