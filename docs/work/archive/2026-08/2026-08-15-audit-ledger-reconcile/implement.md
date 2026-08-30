# Implementation plan — audit ledger reconciliation

Branch: `task/audit-ledger-reconcile` off `main`.

## 1. Complete the verification sweep

`research/ledger-drift-sample.md` covers 27 of 44. Finish the remaining 17 and
resolve the 4 flagged as needing judgment.

- [ ] Sweep A-004, A-005, A-006, A-007, A-010, A-012, A-017, A-027, A-028,
      A-029, A-030, A-033, A-034, A-037, A-041, A-042, A-043 against their
      recorded evidence.
- [ ] Settle the four judgment cases by reading, not grepping:
  - A-015 — `housekeeping.sh` no longer contains `hasNextPage`; read the
    replacement and decide whether an unbounded loop survives.
  - A-016 — `work-loop.py:717` still closes a descriptor `os.fdopen` owned at
    `:705`. Decide whether the wrapping `except OSError` addresses the finding
    or only masks its symptom. Bias to `open`.
  - A-018 — cache variables moved to `sd_ai_command_pack_lib.py:119`. Confirm
    whether they are UID-qualified there. Relocation alone is not `fixed`.
  - A-022 — confirm whether an `update` end-to-end test exists under any name.
- [ ] Resolve one tension the sample surfaced: task
      `08-10-upstream-relay-opencode-plugin-dep` states A-032's "local
      disposition is complete and merged in PR #197", but
      `.opencode/package.json:3` still declares the floating dependency. Either
      the task's claim is wrong or the finding's local half was never the
      package file. Settle it before assigning A-032 a status; do not copy the
      task's claim into the ledger unverified.
- [ ] Append every result to `research/ledger-drift-sample.md` in the existing
      table shape.

Validation: the research file accounts for all 44 IDs exactly once.

```bash
grep -oE 'A-0[0-9]{2}' .trellis/tasks/08-15-audit-ledger-reconcile/research/ledger-drift-sample.md \
  | sort -u | wc -l    # expect 44
```

## 2. Write the re-check script

- [ ] Author `scripts/recheck.py` under this task directory.
- [ ] It parses `.trellis/audit/ledger.md`, collects every ID whose status is
      `fixed`, and runs that ID's assertion.
- [ ] A `fixed` ID with no registered assertion is a failure, not a skip.
- [ ] Exit 0 only when every `fixed` finding's assertion holds.

Review gate: run it before step 3. At that point no finding is `fixed`, so it
checks nothing and exits 0 — a vacuous pass. Confirm the output says so
explicitly (`0 findings marked fixed; nothing to verify`) rather than printing
the same success line a real pass would. A vacuous pass that looks like a real
one is the failure mode that would let step 4 certify nothing.

## 3. Rewrite the ledger

- [ ] For each of the 44 entries set `status:` per the decision rule in
      `design.md`, and add or extend `notes:` with a dated verification line.
- [ ] Touch no other field. `last-seen` stays as-is.
- [ ] Preserve any pre-existing `notes:` text rather than overwriting it.

Validation — structural, before semantic review:

```bash
# every entry still has all its required fields
python3 - <<'EOF'
import re
t = open('.trellis/audit/ledger.md').read()
for b in re.split(r'\n(?=## A-)', t)[1:]:
    i = re.match(r'## (A-\d+)', b).group(1)
    for f in ('status','severity','dimension','first-seen','last-seen','evidence','why','fix','notes'):
        assert re.search(rf'^- {f}:', b, re.M), f'{i} missing {f}'
    s = re.search(r'^- status: (\S+)$', b, re.M).group(1)
    assert s in {'open','fixed','regressed'}, f'{i} bad status {s}'
print('ok')
EOF

# nothing but status/notes changed.
# Matches any added/removed line that is not a `- status:`/`- notes:` bullet
# and not a continuation of one (continuations are indented, not `- `-prefixed).
git diff -U0 .trellis/audit/ledger.md \
  | grep -E '^[-+]' | grep -vE '^(\+\+\+|---)' \
  | grep -vE '^[-+]- (status|notes):' \
  | grep -vE '^[-+][[:space:]]+[^-[:space:]]'
# expect no output
```

## 4. Run the acceptance check

- [ ] `python3 .trellis/tasks/08-15-audit-ledger-reconcile/scripts/recheck.py`
      exits 0 with zero contradictions.
- [ ] `make check` passes.

Rollback point: if step 4 contradicts a `fixed` status, revert that entry to
`open` with a note explaining the contradiction. Do not weaken the assertion to
make it pass — that inverts the purpose of the check.

## 5. Commit in two parts

Order matters: the ledger commit must not contain task paths.

- [ ] Commit 1 — `git add .trellis/audit/ledger.md` only.
      `chore(audit): reconcile ledger statuses against HEAD`
- [ ] Verify: `git show --stat HEAD` lists exactly one file.
- [ ] Commit 2 — `git add .trellis/tasks/08-15-audit-ledger-reconcile` only.
      `chore(trellis): record audit ledger reconciliation`
- [ ] Verify: `git show --stat HEAD` contains no `.trellis/audit/` path.

## 6. Ship

- [ ] `sd-ship until=merge`.
- [ ] The PR body needs a tooling/generated scope heading: the diff is entirely
      `.trellis/**`, and the journal files added at finalization trigger
      `pack.review-scope` late (this is finding A-010's neighbour, tracked as
      task `08-10-review-scope-late-arrival`). Author the heading up front
      rather than absorbing the failure on the successor-head re-entry.

## Follow-ups to record, not to do here

- The status write-back gap that caused this drift. If the sweep shows most
  `fixed` findings were fixed by a task that never touched the ledger, file a
  task for closing that loop in the merge path.
- Every finding confirmed still-present becomes candidate work for the next
  `sd-work-backlog` run. Record the list in the task record so the loop can see
  it without re-deriving.
