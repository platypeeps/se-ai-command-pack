# write_json omits the trailing newline on every task.json

## Goal

Make every `task.json` Trellis writes end with a newline, so hand edits produce
a one-line diff instead of a two-line diff plus a spurious no-newline marker.

## Problem

`common/io.py:37` builds the payload and writes it verbatim:

```python
payload = json.dumps(data, indent=2, ensure_ascii=False)
...
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(payload)
```

`json.dumps` does not append a newline and nothing adds one, so every file
written through `write_json` ends mid-line. The surrounding function is
otherwise careful — the write is atomic through `mkstemp` plus `os.replace`,
with a docstring explaining why — which is what makes the omission read as an
oversight rather than a decision.

### The same repository already does it the other way

`.trellis/scripts/common/active_task.py:428` defines its own writer:

```python
path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
```

Identical `json.dumps` call, identical arguments, `+ "\n"` appended. Two writers
in the same script family disagree, so this is an internal inconsistency in
Trellis, not a convention either way.

### Blast radius

`write_json` has fifteen call sites across `task.py` and `task_store.py` —
create, start, set-base-branch, set-scope, and every parent/child link mutation.
Every one produces a newline-less file.

Measured across the active task tree: **15 of 19** `task.json` files have no
trailing newline. The four that do are the ones previously corrected by hand.
`.trellis/.template-hashes.json` is also affected.

Nothing in the repository enforces the convention: there is no `.gitattributes`
and no `.editorconfig` `insert_final_newline` rule, so no check catches it.

### Why it costs anything

The file is machine-written but hand-edited. Correcting one field with an editor
that adds a final newline turns a one-line change into:

```
-  "base_branch": "task/07-28-enhance-skills-workflow"
-}
\ No newline at end of file
+  "base_branch": "main"
+}
```

The `}` line and the marker are pure noise in review, and they appear on exactly
the files a reviewer is most likely to be reading closely. It also means the
same logical file has two possible byte representations depending on who wrote
it last, so a later `task.py` command silently reverts an editor's newline and
produces a second no-op-looking diff.

## Constraint: the file is vendored

`.trellis/scripts/common/io.py` is tracked in `.trellis/.template-hashes.json`
and is upstream-Trellis, not repo-owned. Changing it is an **upstream** pull
request needing its own approval, which the autonomous run-level authority
explicitly excludes. Only this repository's `.trellis/spec/` guidance is
editable locally.

## Requirements

- Decide and record a disposition:
  - **Upstream (preferred).** Propose appending `"\n"` in
    `io.py:write_json`, matching `active_task.py:428`. The change is one
    character of behaviour; the proposal's substance is the consistency
    argument and the migration answer below.
  - **Local-only.** If upstream is not pursued, document in
    `.trellis/spec/backend/quality-guidelines.md` that `task.json` is written
    without a trailing newline, that a hand edit should not add one, and that a
    no-newline marker in a `task.json` diff is expected rather than a defect.
- State what happens to the 15 existing files. A code change fixes only files
  written after it lands; a bulk rewrite would touch 15 tasks in one commit for
  cosmetic reasons. Pick one and say why — do not leave it implied.
- Do not change `write_json`'s atomicity, its `mkstemp`/`os.replace` sequence,
  its error handling, or its return contract. The newline is the whole change.
- Do not introduce a repository-level `.gitattributes` or `.editorconfig` rule
  as a workaround. That would mask the inconsistency at the diff layer while
  leaving the two writers disagreeing.

## Acceptance Criteria

- [ ] The disposition is recorded with its reasoning, including whether upstream
      approval was sought.
- [ ] The record cites both writers by file and line — `io.py:37` and
      `active_task.py:428` — so the inconsistency is verifiable without
      re-deriving it.
- [ ] The migration answer for the existing 15 files is stated explicitly, with
      its reason.
- [ ] If the upstream route is chosen, the proposal confirms the atomic-write
      behaviour is unchanged.
- [ ] Whichever route is chosen, a reader hitting a `\ No newline at end of
      file` marker on a `task.json` can determine from the guidance alone
      whether it is expected.

## Out of scope

- The `base_branch` default defect in the same script family. That is
  `08-06-task-create-base-branch-default`; the two share a file tree and nothing
  else.
- Any other formatting property of `task.json` — key order, indent width,
  `ensure_ascii`.
- Trailing newlines in non-JSON Trellis artifacts, or in generated files outside
  `.trellis/`.

## Notes

- Measured 2026-08-06: 15 of 19 active `task.json` lack the trailing newline;
  the 4 exceptions were hand-corrected earlier. `.trellis/.template-hashes.json`
  is affected too but is regenerated, so it does not motivate the fix.
- Surfaced while correcting `base_branch` on two tasks, where a 2-line change
  rendered as a 4-line diff. The two defects were found together but are
  independent — same file tree, unrelated causes.
- Seventh instance of the vendored-artifact pattern. That pattern now clearly
  warrants its own task rather than a note repeated in each PRD.
- Lightweight; PRD-only.
