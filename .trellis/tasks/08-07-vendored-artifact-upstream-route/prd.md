# Vendored-artifact defects have no recorded route to upstream

## Goal

Record once — the ownership lookup, the upstream route, and the local-only
fallback — so a run that finds a defect in an installed file can determine what
it is allowed to do without re-deriving the answer from registries each time.

## Problem

Seven active tasks hit the same wall and each wrote its own version of it. The
first six reached it independently, before this consolidation task existed; the
seventh was written after it and still needed its own constraint section,
because the shared guidance this task proposes does not exist yet:

| Task | Its constraint heading |
| --- | --- |
| `08-06-finalization-ordering-trap` | the stages are not owned by this repository |
| `08-06-prism-rules-lane-divergence` | the adapter is not owned by this repository |
| `08-06-sd-review-local-rebuttal-gap` | all three surfaces are vendored |
| `08-06-watch-coordinator-infra-classification` | the coordinator is not owned by this repository |
| `08-06-task-create-base-branch-default` | the file is vendored |
| `08-06-task-json-trailing-newline` | the file is vendored |
| `08-07-status-collector-pack-drift` | the collector is vendored |

Seven headings, six phrasings, one fact — two tasks reached the identical
wording independently. Each task spent its own investigation
establishing ownership, and each arrived at the same two-option ending —
document locally, or propose upstream — with no shared statement of what either
option actually requires.

### There are three registries, and which one applies is not obvious

Ownership is decided by a different registry depending on where the file came
from:

| Registry | Governs | Notable behaviour |
| --- | --- | --- |
| `.sd-ai-command-pack/manifest.json` | files installed from sd-ai-command-pack | entry kinds: `install: "always"`, `install: "if-not-exists"`, and `kind: "managed-block"` with an `anchor` |
| `.sd-ai-command-pack/provenance.json` | per-file hashes for the same pack | detects local drift against the installed version |
| `.trellis/.template-hashes.json` | files installed from upstream Trellis | 148 entries, including 28 under `.trellis/scripts/` |

A run holding a file path has no single lookup that answers "who owns this".
Getting it wrong in either direction is costly: treating a repo-owned file as
vendored abandons a fix that was always allowed, and treating a vendored file as
repo-owned produces an edit the next pack refresh silently reverts.

Two behaviours in particular are not obvious from the file alone:

- **`install: "if-not-exists"` means repo-owned after first install.** This is
  how `.prism/rules.json` is classified, and it is why
  `08-06-prism-rules-lane-divergence` concluded the PR #156 rule was
  *undelivered* rather than clobbered. That distinction changed the task's
  entire remedy.
- **A file can be dual-owned.** `.github/copilot-instructions.md` is recorded as
  a whole-file hash by Trellis while the sd-pack legitimately appends its own
  managed block, so the Trellis hash reports permanent drift that is not drift.
  A run comparing hashes will see a false positive with no way to know it is
  expected.

### The boundary is real, not merely undocumented

`sd-work-backlog`'s run-level authority explicitly excludes "an upstream Trellis
pull request without explicit approval for that PR". So the block is genuine.
What is missing is what happens next: whether the local-only fallback is a
lesser outcome or a legitimate terminal one, what a run should write down so the
upstream proposal survives the session, and how a later reader learns the
proposal was never made.

All seven tasks are still in planning, so none has yet *chosen* a disposition.
What converged is the framing: every one independently reduced the problem to
the same two options — document locally, or propose upstream — and read the
authority boundary the same way, that an upstream pull request is approval-gated
and local documentation is available without it. Seven independent derivations
of one framing is evidence the rule exists; it just is not written anywhere.

The seventh is the sharpest evidence: it was authored on 2026-08-07 with this
consolidation task already filed, and still had to restate the whole constraint
from scratch, because a filed task is not recorded guidance.

## Requirements

- Record the ownership lookup as a procedure: given a repository-relative path,
  which registry to consult in which order, and what each possible result means
  for editability. It must resolve `install: "always"`,
  `install: "if-not-exists"`, `kind: "managed-block"`, a `.template-hashes.json`
  entry, and "in no registry" — including which of those are repo-owned.
- Name the dual-ownership case explicitly, with `.github/copilot-instructions.md`
  as the worked example, so a run that sees its permanent hash drift can
  classify it as expected rather than investigating it again.
- State the disposition rule for a vendored defect: that local documentation is
  a legitimate terminal outcome and not a partial failure, that an upstream
  proposal requires explicit per-PR approval, and that a run must not edit a
  vendored file in place as a workaround.
- Specify what a task records when it takes the local-only route, so the
  unproposed upstream change stays discoverable: the owning pack, the file, the
  behaviour, and the fact that no upstream PR was opened.
- Do not weaken the authority boundary. This task documents the route; it does
  not grant, presume, or create a standing approval for upstream pull requests.
- Do not edit any vendored file as part of this task, whether it sits inside
  `.trellis/` or outside it. The deliverable is guidance recorded in
  `.trellis/spec/backend/quality-guidelines.md`, which is repo-owned and is the
  file the rest of this ordering cluster also writes.

## Acceptance Criteria

- [ ] A run holding an arbitrary repository-relative path can determine
      ownership from the recorded procedure alone, without opening the three
      registries to work out which applies.
- [ ] The procedure is verified against at least four real files with known and
      differing classifications — one `install: "always"`, one
      `install: "if-not-exists"`, one `.template-hashes.json` entry, and one
      repo-owned file in no registry — and each yields the correct answer.
- [ ] `.github/copilot-instructions.md` is classified as dual-owned with its
      drift named as expected.
- [ ] The disposition rule states that local-only is terminal, and that an
      upstream PR needs explicit approval.
- [ ] At least two of the seven existing tasks can have their bespoke constraint
      section replaced by a reference to the recorded guidance without losing
      information. Demonstrated, not asserted.
- [ ] The local-only record format names all four required fields — owning pack,
      file, behaviour, and the explicit statement that no upstream PR was opened
      — and a worked example shows each one filled in.
- [ ] No file outside `.trellis/` is modified, and no file inside `.trellis/`
      that appears in `.trellis/.template-hashes.json` is modified. Verified by
      checking each changed path against that registry, since the vendored files
      this task is about live inside `.trellis/`.

## Out of scope

- Fixing any of the seven underlying defects. Each keeps its own task.
- Opening an upstream pull request against `sd-ai-command-pack` or Trellis.
- Building a tool or check that computes ownership. If the procedure turns out
  to want automating, that is a separate task with its own justification.
- Changing `sd-work-backlog`'s authority contract, which is itself a vendored
  file.

## Notes

- The table above is the canonical membership list for the vendored-artifact
  pattern. This task consolidates those seven; it is not itself an eighth
  instance of the defect. Earlier drafts of two member PRDs each carried their
  own running ordinal and both arrived at "seventh" — those ordinals have been
  removed in favour of pointing here.
- Membership has one source of truth: the table. The count does not — "seven"
  also appears in this PRD's prose, in this task's `task.json` description and
  notes, and in its `implement.jsonl`, and every one of those is derived. Adding
  a member means appending the row **and** reconciling each derived copy in the
  same edit; a member task must not carry its own ordinal at all. This is the
  weakness of the arrangement, stated rather than hidden: the table is
  authoritative, but nothing enforces that the derived copies agree with it.
- The last row was added on 2026-08-07 and is the strongest argument that the
  pattern is worth writing down: the status collector cannot resolve a target
  pack version in a consumer repository (`collect_versions`,
  `sd-ai-command-pack-status.py:393-398`), so an installed pack behind the
  source checkout reports `packState: "installed"` and `SD status: healthy` with
  no anomaly. The collector is itself installed from the sd-pack, so the defect
  that hides vendored drift is vendored. It carries its own task,
  `08-07-status-collector-pack-drift`; this one still does not fix it.
- Planning depth: PRD-only. The deliverable is recorded guidance; the ownership
  procedure is a lookup, not a design.
