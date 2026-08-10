# Implementation plan — skill_review internals

Design: [`design.md`](design.md). Requirements and acceptance criteria:
[`prd.md`](prd.md).

One branch, one PR. D1 and D2 are independent, so they land as two commits and
either can be reverted alone.

## Preconditions

- [ ] On `main`, clean tree, synced with `origin`.
- [ ] `task.py start` has run (this plan is written before it, per the complex-task gate).
- [ ] Feature branch created and recorded with `task.py set-branch`.

## Step 1 — Collapse the containment predicates (D1)

- [ ] Delete `_is_within` (`skill_review.py:1648`).
- [ ] Rewrite its three call sites — `:1793`, `:1807`, `:1810` — to `_is_relative_to`,
      preserving the `candidate == root or not ...` guard at `:1793` verbatim.
- [ ] Grep the whole repo for the dead name.

Validation:

```bash
grep -rn "_is_within" . --exclude-dir=.git --exclude-dir=.venv   # expect: only .trellis/tasks/** prose
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -m unittest discover -s tests -p test_skill_review.py 2>&1 | tail -3
```

Failure condition: any hit outside `.trellis/tasks/`, or any test regression.

## Step 2 — Rewrite `_frontmatter` as a strict rejecting subset (D2, D3, D4)

- [ ] Add a module-level comment on `_frontmatter` naming
      `generate-skill-surfaces.py` as the authoritative grammar, this parser as a
      strict rejecting subset of it, and the conformance test as the binding.
- [ ] Replace the quoted-value branch: drop `ast.literal_eval`. Single-quoted →
      replace `''` with `'`. Double-quoted → strip delimiters, but reject if the
      value contains a backslash. Reject an unterminated quote or trailing
      content after the closing quote.
- [ ] Add the scalar resolution guard, applied to **keys and values alike**:
      accept `true`/`false` (yielding `"true"`/`"false"`) and empty (yielding
      `""`); reject every other spelling YAML would resolve to a non-string — the
      boolean and null spellings and anything numeric- or date-looking.
      Conservative over-rejection is correct here; a strict subset may refuse
      more than YAML but never disagree. Keys matter as much as values:
      `true: v`, `010: v`, `2026-08-10: v` give PyYAML `True`, `8`, and a `date`.
- [ ] Require a space or end-of-line after the mapping colon. `name:value` is a
      plain scalar to YAML, not a mapping entry, and the authority reports
      `frontmatter must be a YAML mapping` for it.
- [ ] Add the structural rejections from D3 — indented line; an unquoted value
      whose **first character** is any of `-?:,[]{}#&*!|>%@` or a backtick
      (first character, not a two-character form: `k: -` alone is a
      `ScannerError`); ` #` or **any** `:` in an unquoted value, including a
      trailing one; missing `:`; an empty key, a quoted key, a key whose **first
      character** is an indicator, or the merge key `<<`; duplicate key — each
      raising `ReviewError` in the D4 format with a 1-based line number.
- [ ] **The key check is on the opening character only.** A substring test would
      reject `disable-model-invocation` — 14 live generated files — and `a#b: v`,
      which PyYAML accepts. `<<` needs its own rule: PyYAML tags it as a merge
      key and raises `ConstructorError`, which no resolver-free parser can infer.
- [ ] Add the generator-side guard (D2 reciprocal obligation): `validate_skill`
      refuses a description containing a Unicode category `Cc` control character,
      U+2028, or U+2029. Without it a legitimate tab in a description renders an
      overlay the shipped parser refuses — measured, `description: "Use when
      alpha\tomega"`. Define the guard by category, not by an ad-hoc character
      list; U+2029 folds to a real continuation line exactly as U+2028 does.
- [ ] Trim with `strip(" ")`, **never bare `strip()`**. Python counts U+00A0 as
      whitespace and YAML does not, so `description: <NBSP>text` silently loses a
      character today. This is the one place the rewrite fixes a bug the current
      parser already has rather than closing a future one.
- [ ] Reject any Unicode category `Cc` character other than the line break,
      anywhere in the block — subsumes the tab rule and closes NUL, which makes
      PyYAML's reader raise `special characters are not allowed` while a line
      parser accepts it silently.
- [ ] Delete the two silent `continue` paths that the rejections replace.
- [ ] Keep the return signature `tuple[dict[str, str], str, tuple[str, ...]]`
      and the surrounding module's style.
- [ ] Update the operator-facing caveat at `:1635` — `coverage.limits[0]`,
      currently "Metadata parsing is intentionally limited to top-level scalar
      fields." — to state that out-of-subset constructs are rejected rather than
      reinterpreted. Same commit: it is payload and it feeds `snapshotId`.

Validation:

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -m unittest discover -s tests -p test_skill_review.py 2>&1 | tail -3
```

Failure condition: any pre-existing `test_skill_review` case changes verdict.
That would mean the subset is narrower than the shipped fixtures, not just
narrower than YAML.

Confirm PyYAML's resolver empirically rather than from memory before writing the
guard — `yaml.safe_load("k: yes")` must return `True` and `yaml.safe_load("k:
2026-08-10")` a `datetime.date`, since the whole guard rests on YAML 1.1
resolution being wider than intuition suggests.

## Step 3 — Conformance test (D5)

- [ ] New `tests/test_frontmatter_conformance.py` with the six groups from D5.
- [ ] Group 6 ports the planning fuzz prototype. Baseline to reproduce:
      `cases=468 accepted=72 rejected=396`, `DIVERGENCES=0`,
      `CONTROL-CHAR DIVERGENCES=0`. A run that accepts materially more or fewer
      than 72 means the implementation drifted from D3, not that the fuzz is
      wrong — reconcile against the design before changing the test. The key
      shapes must include `disable-model-invocation`, `a#b`, and `<<`; the value
      shapes must include bare `-`, `?`, and `:`.
- [ ] Group 1 enumerates `**/SKILL.md` from `git ls-files -z` — never a literal
      path list, and **not** the wider manifest `.md` set. `_safe_pack_skill_source:614`
      refuses any basename but `SKILL.md`, so agent overlays are unreachable, and
      binding them here would fail the test on a legitimate `tools: [Read]`.
- [ ] Group 5 builds a temporary installed root with `external/SKILL.md` and runs
      the real installed-discovery path (`_discover_installed:1029` →
      `build_inventory:1588`). Tracked enumeration cannot see an operator's
      installed skills; this fixture is the only coverage they get.
- [ ] Group 1 skips nothing silently: a document with no frontmatter is counted
      and reported, not dropped.
- [ ] Group 1 guards against vacuity: assert `>= 150` documents, `>= 1` boolean
      value, and `>= 1` double-quoted value in the enumerated corpus (today: 180,
      14, 29).

**Group 1 passes before the change.** The corpus exercises none of the
divergences — measured, `mismatches: 0` against the current parser over all 180
documents — so it is a regression guard, not evidence the fix works. Do not
report it as a bite proof.

Validation — the test must **bite**, proven by three probes, each reverted:

```bash
bash scripts/sd-ai-command-pack-toolchain.sh run-python -- -m unittest discover -s tests -p test_frontmatter_conformance.py 2>&1 | tail -3
```

- [ ] Probe A: temporarily restore `ast.literal_eval` in the quoted branch →
      **group 2** fails on the `'a: b''s'` case. Group 1 stays green, and that
      asymmetry is the point.
- [ ] Probe B: change the generator's `width=10000` to `width=40` and render one
      overlay in memory → group 4 fails, because the wrapped continuation line
      is now a rejected indented line rather than a silently dropped one.
- [ ] Probe C: add `tools: [Read]` to one canonical `SKILL.md` → group 1 fails
      with the flow-sequence construct name, proving the rejection reaches real
      files and not only synthetic fixtures.
- [ ] Probe D: revert the `validate_skill` control-character guard → group 4b
      fails on the tab description, which is the hole the first draft of this
      plan shipped. Then restore the guard but **omit only U+2029**, keeping `Cc`
      and U+2028 → 4b must still fail, isolating U+2029. Reverting the whole
      guard does not isolate it, since the tab case fails first.
- [ ] Probe E: widen the guard to reject the **apostrophe** → group 4c fails.
      "Reject every non-ASCII character" would not work: `'`, `:`, and `#` are
      code points 39, 58, and 35, so 4c would stay green and prove nothing.
- [ ] Probe F: switch one `strip(" ")` back to bare `strip()` → group 6 fails on
      the NBSP case. That bug is live in the current parser and invisible to
      every other group.

A probe that does not produce the expected failure means the test is not
covering what it claims; fix the test before proceeding.

## Step 4 — Release discipline (D6)

- [ ] `manifest.json` version `0.68.3` → `0.69.0`.
- [ ] `CHANGELOG.md`: one `## 0.69.0 - <today>` entry naming both changes and
      listing the newly rejected constructs. The bullet **leads with
      `**Breaking:**`** per `CONTRIBUTING.md:137` — input a consumer's `SKILL.md`
      could previously carry is now refused. The release gate validates only the
      heading, so nothing catches a missing marker; it is on this step.
- [ ] `make generate` to refresh derived surfaces that carry the version
      (`generated/references/skill-catalog.md` holds `Bundled pack version`).

Validation:

```bash
make release-check
```

Expected: the payload gate reports the `0.68.3 -> 0.69.0` bump accepted rather
than `no payload change`.

## Step 5 — Full gate

```bash
make check
```

Expected, all in one run: `unittest` green with the new module counted, coverage
at or above the 80 floor, ruff and mypy clean, release payload gate accepting
`0.69.0`, `shell-syntax` unchanged, `trellis-provenance check: ok`.

Failure condition: any non-zero exit. `make check` alone is not sufficient
evidence for this task — the PR #206 incident showed a local gate can be green
because it reads machine-local state — so Step 3's enumerate-from-tracked-tree
shape and CI's own run are the real proof.

## Step 6 — Ship

- [ ] `sd-ship until=merge` under the work-loop context.
- [ ] Confirm CI lanes green at the pushed head before the merge gate: the
      conformance test shells out to `git ls-files`, and a fresh-clone or
      shallow-checkout difference would surface only there.

## Review gates

1. After Step 2, before Step 3: the rejection set matches D3 exactly — no
   construct added on impulse, none quietly dropped.
2. After Step 3: all six probes ran and were reverted; the tree is clean.
3. Before Step 6: `git status` clean, no `git add -N` residue
   (`git rm --cached --force` if any appears — `git reset` does not clear it).

## Rollback points

- After Step 1: revert the single commit; nothing else depends on it.
- After Step 2: revert commits 2–3 together; the version bump in Step 4 is the
  only thing that would need re-deciding, and it is a separate commit.
- After merge: `git revert` of the merge; no migration, no persisted state.
