# Roll out dispatch protocols to remaining fan-out skills — Design

## Overview

Replicate the validated pilot `## Sub-agent dispatch` section
(07-25-dispatch-pilot, shipped on `templates/skills/se-research/SKILL.md` and
`se-fact-check/SKILL.md`) across five more high-fan-out skills: **se-digest,
se-feedback, se-scan, se-video-notes, se-red-team**. Prose-only change per
skill: a non-required section inserted **between `## Workflow` and
`## Safety rules`**. No `## Final report` contract changes, no generator
changes, no registry/profile changes.

Doctrine anchor: `templates/skills/se-review-skills/references/runtime-routing.md`
"Subagent decomposition" (lines 67-86). Model section: `sd-audit-repo`'s
`## Dispatch protocol`, as the pilot recorded.

## Pattern to replicate (se-fact-check shape)

All five targets are **single-fan-out-phase** (one worker per unit, then
orchestrator synthesis), so they follow the **se-fact-check** structure, NOT
se-research's multi-phase "within a phase, never across phases" guard. Each
`## Sub-agent dispatch` section has six elements:

1. **Strategy / inline-fallback opening.** Verbatim first sentence:
   `On sub-agent dispatch platforms, run the units below in parallel; on inline
   platforms, work through them sequentially in one context.` Then the pilot's
   layered-strategy clause, naming **this skill's own quality invariant** (see
   per-skill table) instead of se-fact-check's "verdict ladder":
   "Dispatch is an execution strategy layered over the Workflow above — it never
   changes the scope, the `<invariant>`, or the `## Final report` contract."
2. **One-worker-per-`<unit>` bullet.** States the unit and that the orchestrator
   does the pre-fan-out inventory/ID assignment and post-fan-out synthesis.
3. **Orchestrator-owns bullet.** Parent assigns unit IDs, deduplicates and
   reconciles worker output, and writes the single final report; workers never
   assign IDs and never write the report (runtime-routing.md:80-81).
4. **Worker input contract bullet.** Five mandatory elements: (a) smallest
   complete input, (b) explicit exclusions, (c) read-only authority boundary,
   (d) **expected artifact** (exact per-unit result shape), (e) **stop
   condition**. Concurrency capped to host/task budget (runtime-routing.md:77-79).
   Any skill with a global gate (se-scan same-criteria, se-video-notes
   coverage-fidelity) states it stays an orchestrator-enforced gate, never a
   per-worker quota (mirrors se-research's `min_sources` note).
5. **No-recursion guard bullet.** When already running as a dispatched
   sub-agent, run units inline rather than spawning another layer
   (runtime-routing.md:79). se-red-team adapts the wording to fresh-session
   (independent session, not a returning fork).
6. **Active-task prefix bullet.** Verbatim: open each dispatch prompt with
   `Active task: <task path from task.py current>` when a Trellis task is
   active; omit and hand the worker its unit input directly otherwise.

## Per-skill units, invariant, insertion point, result contract

| Skill | Fan-out unit | Named invariant | Insert after | Per-unit result (feeds final report, unchanged) |
|-------|--------------|-----------------|--------------|--------------------------------------------------|
| se-digest | per input document/thread | "the synthesis discipline" | Workflow step 7 | per-document claims + stance with locators → "Per-document digests" |
| se-feedback | per supplied review/source | "the disposition discipline" | Workflow step 12 | atomic feedback entries (wording, locator, requested change, rationale, severity…) → orchestrator assigns feedback IDs/clusters |
| se-scan | per player/vendor profile | "the same-criteria discipline" | Workflow step 6 | one profile on shared `criteria=` axes, dated signals, `unknown`/stale marks → comparison table |
| se-video-notes | per video (**`mode=compare` only**) | "the coverage-fidelity bar" | Workflow step 15 | per-video inventory + coverage class + timestamp ledger + chapter/claims ledgers → source-inventory/timestamps/claims bullets |
| se-red-team | per adversarial lane | "the classification discipline" | Workflow step 13 | one classified finding-register entry per lane → "Classified finding register" |

Orchestrator-owned cross-unit work that MUST NOT be fanned out (stated in each
section): se-digest agreement/conflict map (step 4) + web-gap-fill (step 6);
se-feedback dedup (step 5) + disagreement/minority preservation (step 7);
se-scan comparison table + positioning read; se-video-notes compare-frame
synthesis (step 12) + final audit; se-red-team steelman (step 2) + evidence
ledger (step 3) + lane selection (step 4) + counterargument (step 9) +
minimization/handoff.

## R2 — se-red-team fresh-session divergence (the one non-mechanical case)

se-red-team carries `INDEPENDENT_RED_TEAM` / `context: fresh-session`
(`installer/registry.py:171-173, 248`); its generated overlay already appends
the fresh-session advisory (`generated/skills/claude/se-red-team/SKILL.md`,
marker `<!-- generated: runtime-profile fresh-session -->`). The dispatch
section diverges from the pilot in two recorded ways:

1. **Workers must not inherit the parent's conclusions (R2).** Per-lane workers
   receive the artifact + the shared evidence/assertion ledger + their lane
   frame only — never the parent's steelman verdict, suspected defects, expected
   findings, intended fixes, or the reviewer's conclusion
   (runtime-routing.md:83-86; fresh-session definition runtime-routing.md:27-28).
   The steelman and evidence ledger are shared *inputs*; each lane judgment is
   formed independently from the artifact and evidence alone.
2. **No-recursion wording adapted to fresh-session** — the skill runs as an
   independent session, not a returning fork, so the guard says: when already
   running as an independent red-team session, run the lanes inline rather than
   spawning another layer.

This is the divergence the PRD requires to be recorded (R1: "Divergences from
the pilot pattern require a recorded reason"); it is captured here and will be
summarized in the pattern-conformance note before archive.

## Boundaries and non-goals

- Exactly five skills change. Every other skill body is byte-identical.
- **se-socratic-review is explicitly out of scope** (anti-parallel-by-design, R4).
- No `## Final report` contract change; dispatch references but never alters it.
- No generator, registry, profile, or manifest `files`-array change. Only the
  five canonical skill bodies + their regenerated overlays + version/changelog.
- Host BUILT-IN sub-agents only; prose must never name a specific SE worker
  agent or a host/product brand (R4 + neutrality lint).

## Validation

- **Neutrality lint**: no brand words (`BANNED_PHRASE_PATTERN`,
  generate-skill-surfaces.py:140-142). Use capability phrasing.
- **Section order**: `REQUIRED_SECTIONS` order-only check
  (generate-skill-surfaces.py:269-277) permits the interspersed non-required
  section; inserting between Workflow and Safety rules keeps order valid.
- **Drift gate**: hand-bump `manifest.json` version, prepend a dated
  `CHANGELOG.md` entry, `make generate` (regenerate 5 overlays + help catalog +
  skill-catalog), then `make check` (= test lint release-check; release-check =
  `--check` drift gate + `check-release-payload.py`) → exit 0.
- **Pattern-conformance note**: the PRD's human gate — a short note recorded in
  the task (what matched the pilot, what diverged and why) before archive. No
  automated dispatch-presence test exists.

## Risks and edge cases

- **Line-number drift**: research insertion lines assume the current tree.
  A-006 already landed, so no rename rebase is pending, but re-verify each
  insertion heading by content (find `## Workflow` … `## Safety rules`) before
  editing rather than trusting a fixed line number.
- **Version-ordering**: the help/skill catalog embeds the manifest version
  (regression seen in runtime-profile-gaps). Bump `manifest.json` **before** the
  final `make generate`, or `--check` rejects a stale catalog.
- **se-red-team overlay marker**: the fresh-session marker is appended at body
  end by the generator; after adding the dispatch section the overlay order is
  Workflow → Sub-agent dispatch → Safety rules → Final report → fresh-session
  marker. `make generate` re-appends it; the drift gate pins it. No manual edit
  of any `generated/**` file.
- **Over-broad edit**: touch only the five target bodies. Confirm `git diff
  --name-only` after `make generate` lists exactly the five templates + their
  five overlays + help catalog + skill-catalog + manifest + changelog.

## Affected files

- `templates/skills/{se-digest,se-feedback,se-scan,se-video-notes,se-red-team}/SKILL.md`
  — add `## Sub-agent dispatch`.
- `generated/skills/claude/{…same five…}/SKILL.md` — regenerated.
- `templates/skills/_shared/references/skill-catalog.md`, help catalog — regenerated.
- `manifest.json` (version bump), `CHANGELOG.md` (dated entry).
- Task: a pattern-conformance note before archive.
