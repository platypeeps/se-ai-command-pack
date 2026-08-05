# Research: Target skills for dispatch rollout (5 skills)

- **Query**: For each of se-digest, se-feedback, se-scan, se-video-notes, se-red-team — fan-out unit, per-unit result contract, insertion point, skill-specific wrinkle.
- **Scope**: internal
- **Date**: 2026-08-05

## Structural model to use

All five are **single-fan-out-phase** skills (one worker per unit, then orchestrator synthesis), so they follow the **se-fact-check** shape, NOT se-research's multi-phase "within a phase, never across phases" guard. Each dispatch section states: strategy/inline-fallback line, one-worker-per-<unit> bullet, orchestrator-owns bullet, worker input contract bullet, no-recursion bullet, active-task-prefix bullet (see `pilot-pattern.md`). Insert `## Sub-agent dispatch` between `## Workflow` and `## Safety rules` in every case.

Runtime profiles (`installer/registry.py:178-250`): se-digest, se-feedback, se-scan, se-video-notes = `BOUNDED_SYNTHESIS` (context `forked`); se-red-team = `INDEPENDENT_RED_TEAM` (context `fresh-session`, `user-only`, `installer/registry.py:171-173, 248`).

---

## se-digest — `templates/skills/se-digest/SKILL.md`

- **(a) Fan-out unit**: **per input document/thread**. Workflow steps 2-3 (SKILL.md:46-53) — "Read every input in full" and "Extract per-document claims and stance … with locators" — are mutually independent per input. Orchestrator-owned before/after: step 1 inventory (assigns document IDs), step 4 agreement/conflict map (inherently cross-document), steps 5-7 synthesis + delivery.
- **(b) Per-unit result contract** (worker returns, does not change final report): per-document claims + stance (what it asserts/recommends/assumes) with locators (page/section/timestamp) — i.e. the raw material for the "Per-document digests" bullet in `## Final report` (SKILL.md:76-77). Orchestrator keeps ownership of the "Conflict table" and "Synthesis" (SKILL.md:74-80).
- **(c) Insertion point**: after `## Workflow` step 7 (line 57 "7. Deliver the digest."), before `## Safety rules` (line 59). Final report at line 72 — unchanged.
- **(d) Wrinkle**: the agreement/conflict map (step 4) is cross-document by construction — it MUST stay orchestrator-owned (maps cleanly to "orchestrator deduplicates and reconciles"). Web-gap-fill (step 6) requires user approval and stays with the orchestrator, never a worker.

## se-feedback — `templates/skills/se-feedback/SKILL.md`

- **(a) Fan-out unit**: **per supplied review/source**. Workflow step 2 (read each source fully) + step 3 (normalize into atomic entries) (SKILL.md:52-59) are independent per source. Orchestrator-owned: step 1 inventory (source IDs), step 5 dedup (cross-source), steps 6-12 clustering/dispositions/ledger.
- **(b) Per-unit result contract**: atomic feedback entries for that source — exact wording/lossless excerpt, original locator, observation, requested change, stated rationale, affected outcome, audience, severity, ambiguity, source limitations (SKILL.md:56-59). Worker does NOT assign the stable feedback IDs, cluster, or set dispositions — those stay with the orchestrator (feedback IDs, theme map, disposition ledger; SKILL.md:79-94, 119-129).
- **(c) Insertion point**: after `## Workflow` step 12 (line 94), before `## Safety rules` (line 96). Final report at line 115 — unchanged.
- **(d) Wrinkle**: dedup (step 5, SKILL.md:63-66) and "preserve disagreement / minority audiences / isolated severe findings" (step 7, SKILL.md:72-74) are inherently cross-source — the dispatch section must state these stay orchestrator-owned so fan-out never erases contradictions or minority views (mirrors safety rule SKILL.md:108-109).

## se-scan — `templates/skills/se-scan/SKILL.md`

- **(a) Fan-out unit**: **per player/vendor profile**. Workflow step 4 (SKILL.md:51-53) — "Build one profile per player on the same criteria" — is independent per player. Orchestrator-owned before fan-out: steps 1-3 (define inclusion rule, enumerate candidates, apply inclusion + cut to `max=`, assign the player set/IDs). Orchestrator-owned after: step 5 comparison table + positioning read, step 6 deliver.
- **(b) Per-unit result contract**: one profile on the shared `criteria=` axes, momentum signals dated, unknowns marked `unknown`, sources >12 months marked stale (SKILL.md:51-53). Orchestrator assembles the comparison table and writes the positioning read (SKILL.md:54-57, 72-78).
- **(c) Insertion point**: after `## Workflow` step 6 (line 57 "6. Deliver the scan."), before `## Safety rules` (line 59). Final report at line 71 — unchanged.
- **(d) Wrinkle**: "same-criteria discipline" (SKILL.md:61-62) is a **global gate** — every worker profiles on the identical axis set; the dispatch section must state the orchestrator enforces the shared criteria across all workers (a per-worker quota/axis must not drift), analogous to se-research's `min_sources` global-gate note (`pilot-pattern.md` element 4).

## se-video-notes — `templates/skills/se-video-notes/SKILL.md`

- **(a) Fan-out unit**: **per video**. In `mode=compare` (>1 video), each video's steps 2-11 (inventory, coverage classification, full transcript read, timestamp ledger, chapter notes, claims/resources ledger; SKILL.md:63-107) are independent. Orchestrator-owned: step 12 compare-mode synthesis (common frame, agreements/conflicts; SKILL.md:111-115) and step 15 final audit (SKILL.md:124-128).
- **(b) Per-unit result contract**: per-video source inventory + coverage class (`complete-transcript|partial-transcript|metadata-only|unavailable`) + timestamp ledger + coverage-bounded chapter notes + claims/resources ledger with the video's stable IDs (SKILL.md:63-107). Feeds the "Source inventory and coverage", "Timestamped notes", and "Claims and verification queue" final-report bullets (SKILL.md:156-166) — unchanged.
- **(c) Insertion point**: after `## Workflow` step 15 (line 128), before `## Safety rules` (line 130). Final report at line 153 — unchanged.
- **(d) Wrinkle**: single-video (`mode=single`) has nothing to fan out — the dispatch section should scope fan-out to `mode=compare` (one worker per video). The coverage/timestamp-fidelity rules (never invent timestamps or coverage; SKILL.md:78-91) are global gates each worker must honor; the compare frame (step 12) stays orchestrator-owned so "coverage asymmetry" is reconciled centrally, not per worker.

## se-red-team — `templates/skills/se-red-team/SKILL.md`

- **(a) Fan-out unit**: **per adversarial lane**. Workflow step 4 (SKILL.md:60-64) selects relevant lanes; steps 5-8 (identify smallest failure, assign one finding class, record finding; SKILL.md:65-86) run per lane and are independent given the shared evidence ledger. PRD lenses (assumptions, incentives, security, privacy, misuse) are a subset of the step-4 lane list (hidden assumptions, contrary evidence, incentives/principal-agent, misuse/abuse, operational failure modes, dependency/concentration, security, privacy, counterargument, reversal). Orchestrator-owned **before** fan-out: step 1 confirm contract, step 2 steelman, step 3 evidence/assertion ledger (stable IDs), step 4 lane selection. Orchestrator-owned **after**: step 9 counterargument, steps 10-13 minimization/responses/handoff.
- **(b) Per-unit result contract**: for its lane, a classified finding register entry — ID (assigned by orchestrator), exactly one class (`demonstrated-defect|plausible-risk|speculative-case|value-disagreement`), locator, affected outcome, severity+rationale, evidence IDs, mechanism, uncertainty, consequence, scope, controls, sensitivity level, response options, residual concern, closure evidence (SKILL.md:69-86). Feeds "Classified finding register" (SKILL.md:137-138) — unchanged.
- **(c) Insertion point**: after `## Workflow` step 13 (line 106), before `## Safety rules` (line 108). Final report at line 127 — unchanged.
- **(d) Wrinkle — R2 fresh-session isolation (CRITICAL)**: se-red-team is `INDEPENDENT_RED_TEAM` / `fresh-session` (`installer/registry.py:171-173, 248`); its generated overlay already carries the fresh-session advisory (`generated/skills/claude/se-red-team/SKILL.md:155-156`, marker `<!-- generated: runtime-profile fresh-session -->`, appended by the generator — `generate-skill-surfaces.py:124-129`). Two composition points the dispatch prose must honor:
  1. **Workers must not inherit the parent's conclusions.** Per-lane workers receive the artifact + the evidence/assertion ledger + their lane frame only — NOT the parent's steelman verdict, suspected defects, expected findings, or the reviewer's conclusion. This directly follows runtime-routing.md:83-86 ("Do not pass suspected defects, expected findings, intended fixes, or the primary reviewer's conclusion unless the validation is explicitly testing that claim") and the fresh-session definition (runtime-routing.md:27-28; SKILL fresh-session note "do not inherit conclusions … Start from the artifact and its evidence alone").
  2. **No-recursion guard wording**: adapt the pilot's "already running as a dispatched sub-agent" phrasing to fresh-session (the skill runs as an independent session, not a returning fork). The steelman and evidence ledger are shared inputs to workers but the lane judgments must be formed independently.
- **Neutrality**: none of se-red-team's existing text trips `BANNED_PHRASE_PATTERN`; new dispatch prose must stay brand-free.

## Caveats

- se-red-team's frontmatter `description` (SKILL.md:3) differs from the tool listing's summary but is not load-bearing for dispatch.
- Exact insertion line numbers assume the current tree; if `07-25-audit-skill-arg-vocabulary` renames arguments first (PRD cross-coordination note), re-verify line numbers before editing.
