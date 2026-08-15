# Design — audit ledger reconciliation

## Boundaries

Two files change, in two commits:

| Commit | Path | Why separate |
|--------|------|--------------|
| 1 | `.trellis/audit/ledger.md` | `sd-audit-repo` owns this file and forbids mixing it with `.trellis/tasks/**` |
| 2 | `.trellis/tasks/08-15-audit-ledger-reconcile/**` | planning artifacts, research, re-check script |

Nothing under `installer/`, `templates/`, `scripts/`, `.github/`, or `docs/`
is touched. This task changes no behavior; if a shipped file needs an edit, the
finding stays `open` and the fix is separate work.

## Schema conformance

The entry shape is fixed by `.claude/skills/sd-audit-repo/SKILL.md:223-238`:

```
## A-NNN — <title>
- status: open|fixed|regressed
- severity: P2 · effort: M · confidence: Plausible
- dimension: security
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - path:line — note
- why: <=2 lines
- fix: <=2 lines
- notes: <optional, human-editable>
```

Reconciliation writes exactly two fields per entry and leaves the rest byte-identical:

- `status:` — set to `fixed` or left `open`.
- `notes:` — appended to, or added if absent.

`severity`, `effort`, `confidence`, `dimension`, `first-seen`, `evidence`,
`why`, and `fix` are historical record and are not rewritten. In particular
`evidence` keeps its original `file:line` references even where the line has
since moved; the `notes:` line carries the current location. Rewriting evidence
in place would destroy the record of what was originally observed and make the
re-check script unfalsifiable against the original claim.

### `last-seen`

Left unchanged. It means "last seen present", so touching it on a `fixed`
finding would assert the defect was observed at this HEAD, which is the
opposite of the finding. On a still-`open` finding, advancing it would be
defensible, but doing so for some entries and not others produces a field with
two meanings. Uniform non-modification keeps it readable.

## Status decision rule

For each finding, run its recorded evidence against HEAD:

```
cited construct absent / inverted / relocated with the defect gone
    -> fixed
cited construct still present and still defective
    -> open, notes name the current file:line
still real, but the only remaining fix is in another repository
    -> open, notes name the blocked Trellis task that owns it
cannot be settled by a mechanical check
    -> open, notes state what a human must read to settle it
```

`regressed` is available but is expected to go unused: it applies to a finding
previously marked `fixed` that reappeared, and no finding is currently `fixed`.
If the sweep does find a construct that a merged task claims to have removed,
that entry becomes `regressed` rather than `open`, and the discrepancy is
reported rather than quietly normalized.

### Why archived tasks are not evidence

The archive contains a near one-to-one counterpart for most findings, which
makes "matching archived task therefore fixed" tempting and wrong. Tasks are
archived as won't-do as well as done — `08-14-dependabot-lock-automation` is a
merged won't-do in this very repo. The archive is used only to *locate* the
change that plausibly fixed a finding; the status comes from the tree.

## The re-check script

`scripts/recheck.py`, under this task directory. Not repo tooling, not wired
into `make check` — it is the acceptance evidence for this task, and it is
expected to be run by hand and to rot as the tree moves on.

Shape: a table of `(finding_id, assertion)` where each assertion is a small
predicate over the working tree returning pass/fail plus an observed value.

```python
CHECKS = {
    "A-020": lambda: ("--fail-under" in read("Makefile"), "coverage floor in Makefile"),
    "A-026": lambda: (not exists("scripts/se-ai-command-pack-skill-review.py"), "wrapper deleted"),
    ...
}
```

Exit non-zero listing every finding marked `fixed` in the ledger whose
assertion does not hold. The script reads the ledger to discover which findings
claim `fixed`, so a status the sweep sets without a matching assertion is
itself a failure — that is the property that makes the check falsifiable rather
than a restatement of what was just written.

Findings left `open` get no assertion. Asserting a defect is still present is
a weaker and more brittle claim, and an `open` status is the conservative
default that needs no defence.

## Tradeoffs

**Mechanical checks over reading each finding in full.** A grep can confirm a
construct is gone without confirming the *concern* is addressed — A-018's
variables moved to another file, and "moved" is not "UID-qualified". Mitigation:
relocation alone never yields `fixed`; the sweep must observe the defect gone
at the new location, or the finding stays `open` with a note. Four findings are
already flagged this way in `research/ledger-drift-sample.md`.

**Per-finding assertions are hand-written.** One predicate per `fixed` finding
— on the current sample roughly 20-30 of the 44, since `open` findings get no
assertion — is real surface with no reuse. The alternative — a generic "does this evidence line
still resolve" checker — is worse: most evidence is prose about a construct,
not a machine-checkable fact, so a generic checker would silently pass on
findings it cannot actually evaluate.

## Compatibility and rollback

The ledger is read by humans and by `sd-audit-repo`'s next run, which reconciles
against existing IDs. Setting statuses to `fixed` is exactly what that run
expects to find; a subsequent audit that re-detects a `fixed` finding marks it
`regressed`, which is the designed path.

Rollback is `git revert` of the ledger commit alone. Because the two commits are
disjoint, reverting the bookkeeping does not disturb the task record of why it
was done.
