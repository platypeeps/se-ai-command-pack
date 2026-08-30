# Roll out dispatch protocols to remaining fan-out skills — Implementation

Ordered checklist. Prose-only skill-body edits + regeneration + version/changelog.
Validation command for the whole task: `make check` (exit 0).

## Step 0 — Re-verify insertion points (cheap, prevents mis-edit)

For each of the five skills, open `templates/skills/<skill>/SKILL.md` and
confirm by content (not fixed line number) the `## Workflow` section end and the
`## Safety rules` heading. A-006 already landed so no rename rebase is expected,
but confirm the last Workflow step number cited in `design.md` still matches.

## Step 1 — Add `## Sub-agent dispatch` to each canonical body

Insert between `## Workflow` and `## Safety rules`, using the six-element
se-fact-check shape from `design.md`. Order the four mechanical skills first,
then se-red-team (the divergence case) last.

1. **se-digest** — unit: per input document/thread; invariant: "the synthesis
   discipline"; orchestrator keeps the agreement/conflict map (step 4) and
   web-gap-fill (step 6).
2. **se-feedback** — unit: per supplied review/source; invariant: "the
   disposition discipline"; orchestrator keeps dedup (step 5) and
   disagreement/minority preservation (step 7); workers never assign feedback
   IDs or set dispositions.
3. **se-scan** — unit: per player/vendor profile; invariant: "the same-criteria
   discipline"; state the shared `criteria=` axis set is an orchestrator-enforced
   global gate, not a per-worker quota.
4. **se-video-notes** — unit: per video, **scoped to `mode=compare`** (single
   mode has nothing to fan out); invariant: "the coverage-fidelity bar";
   coverage/timestamp-fidelity rules are global gates each worker honors;
   compare-frame synthesis (step 12) stays orchestrator-owned.
5. **se-red-team** — unit: per adversarial lane; invariant: "the classification
   discipline". Apply the **R2 fresh-session divergence** from `design.md`:
   per-lane workers receive artifact + shared evidence/assertion ledger + their
   lane only, NEVER the parent's steelman verdict / suspected defects / expected
   findings / conclusion; the no-recursion guard is phrased for an independent
   session (not a returning fork). Keep steelman (step 2), evidence ledger
   (step 3), lane selection (step 4), counterargument (step 9), and
   minimization/handoff orchestrator-owned.

Neutrality: no brand words in any added prose (capability phrasing only).

## Step 2 — Version bump FIRST (before generate)

Hand-edit `manifest.json` version `0.66.11 -> 0.66.12` (the help/skill catalog
embeds this; bump before `make generate` or the drift gate rejects a stale
catalog).

## Step 3 — Changelog

Prepend a dated `## 0.66.12 - 2026-08-05` entry to `CHANGELOG.md` describing the
dispatch rollout to the five skills and noting the se-red-team fresh-session
divergence.

## Step 4 — Regenerate

`make generate`. Then confirm `git diff --name-only` lists **exactly**: the five
`templates/skills/*/SKILL.md`, the five `generated/skills/claude/*/SKILL.md`, the
regenerated help catalog + `templates/skills/_shared/references/skill-catalog.md`,
`manifest.json`, `CHANGELOG.md`, and the task planning files. No stray file, no
manual `generated/**` edit.

## Step 5 — Full gate

`make check` → exit 0. This runs the unit tests, ruff lint, the
`generate-skill-surfaces.py --check` drift gate (proves committed overlays match
byte-for-byte and the neutrality lint finds zero banned phrases across the five
edited bodies), and `check-release-payload.py`.

## Step 6 — Pattern-conformance note (PRD acceptance item)

Record a short note in the task (e.g. `research/pattern-conformance.md` or the
journal) stating: the four mechanical skills matched the se-fact-check pilot
shape verbatim in structure; the single recorded divergence is se-red-team's
fresh-session isolation (workers isolated from parent conclusions + independent-
session no-recursion wording), justified by R2 + runtime-routing.md:83-86.

## Step 7 — Mark acceptance criteria + finalize

Check the three prd.md acceptance criteria, then hand to the ship flow
(sd-ship until=merge under the work-loop) for finish-work archival + gated merge.

## Validation gates (summary)

- Per-edit: neutrality (no brand words), correct insertion (between Workflow and
  Safety rules), unit boundaries per `design.md`.
- Whole task: `make check` exit 0; `git diff --name-only` scope check.
- Human gate: pattern-conformance note (no automated dispatch-presence test).

## Rollback

Prose-only; revert the five body edits + regeneration + version/changelog in one
commit range. No data or schema migration.
