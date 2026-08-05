# Research: Pilot dispatch-section pattern (se-research, se-fact-check)

- **Query**: Extract the exact dispatch-section template validated in 07-25-dispatch-pilot, plus its recorded rationale and invariants.
- **Scope**: internal
- **Date**: 2026-08-05

## Section identity

- Heading is **`## Sub-agent dispatch`** (not "Dispatch protocol").
- Placement: a **non-required** section inserted **between `## Workflow` and `## Safety rules`**.
  - se-research: `templates/skills/se-research/SKILL.md:71` (section starts at 71, after Workflow ends at 69).
  - se-fact-check: `templates/skills/se-fact-check/SKILL.md:83` (after Workflow ends at 81).
- Modeled on `sd-audit-repo`'s `## Dispatch protocol` per archived design (`design.md:1-8, 30-32`).

## Verbatim structural elements

### 1. Strategy / inline-fallback opening paragraph (capability-first, host-neutral)

se-research (`SKILL.md:73-76`):
> On sub-agent dispatch platforms, run the units below in parallel; on inline
> platforms, work through them sequentially in one context. Dispatch is an
> execution strategy layered over the Workflow above — it never changes the
> scope, the verification bar, or the `## Final report` contract.

se-fact-check (`SKILL.md:85-88`) — identical wording except the middle clause:
> ... it never changes the scope, the **verdict ladder**, or the `## Final report` contract.

**Difference**: each skill names its own quality invariant ("the verification bar" vs "the verdict ladder"). The first sentence ("On sub-agent dispatch platforms, run the units below in parallel; on inline platforms, work through them sequentially in one context.") is verbatim identical and is the R1 strategy line the pilot design pins (`design.md:50-51`).

### 2. Unit-decomposition bullet (skill-specific)

se-research (`SKILL.md:78-84`) — **multi-phase**, because its phases are data-dependent:
> **Parallelize within a phase, never across phases.** The Workflow phases are
> data-dependent: sweep lanes (step 3) feed claim verification (step 4), which
> feeds the disconfirmation pass (step 5). Fan out one worker per search lane in
> step 3; then, once those results are in, one worker per claim verification in
> step 4; then one worker per disconfirmation query in step 5. Never reorder or
> overlap steps 3, 4, and 5 — dispatch only fans out the independent units
> inside a single phase.

se-fact-check (`SKILL.md:90-94`) — **single-phase**:
> **One worker per atomic claim.** After the inventory splits the material into
> atomic claims (steps 2-3), the per-claim evidence work (steps 5-6) is mutually
> independent, so every claim worker runs concurrently in one phase. Inventory,
> claim splitting, and locator assignment stay with the orchestrator and run
> before any fan-out.

**Difference (the key one for rollout)**: se-research has a genuine cross-phase data dependency and therefore adds the "within a phase, never across phases" guard. se-fact-check is single-fan-out-phase and simply states "one worker per atomic claim … run before any fan-out". All five rollout targets are single-fan-out-phase (see `target-skills.md`), so **se-fact-check is the closer structural model** for the rollout.

### 3. Orchestrator-owned IDs / dedup / verification / report bullet

se-research (`SKILL.md:85-88`):
> **The orchestrator owns synthesis.** The parent context assigns unit IDs,
> deduplicates and reconciles worker output, runs the disconfirmation judgment,
> and writes the single final report. Workers never assign IDs and never write
> the report.

se-fact-check (`SKILL.md:95-98`):
> **The orchestrator owns the ledger.** The parent context assigns claim IDs,
> deduplicates evidence, reconciles conflicting verdicts, and writes the single
> verdict ledger. Workers never assign claim IDs and never write the final
> report.

Both trace to runtime-routing.md:80-81 ("The parent verifies evidence, deduplicates overlaps, resolves conflicts, and owns the final report").

### 4. Worker input contract bullet (expected artifact + stop condition)

se-fact-check (`SKILL.md:99-107`):
> **Worker input contract.** Each worker receives the smallest complete input
> for its claim (the claim ID, exact original wording, locator, and as-of date),
> explicit exclusions (do not re-inventory or re-split), an authority boundary
> (read-only: never edit the artifact, publish a correction, or contact a
> source), an **expected artifact** (the single verdict record for its claim —
> one verdict, decisive evidence with dates and locators, and any minimal
> corrected wording), and a **stop condition** (the claim is done when exactly
> one verdict is assigned with its evidence recorded). Cap concurrency to the
> host and task budget.

se-research (`SKILL.md:89-100`) is the same shape but adds a global-gate note: "The `min_sources` minimum stays a global gate the orchestrator enforces across all lanes, never a per-worker quota, so no unit lowers the verification bar." The five mandatory elements per worker are: (a) smallest complete input, (b) explicit exclusions, (c) authority boundary (read-only), (d) **expected artifact** (exact result shape), (e) **stop condition**. Concurrency capped to host/task budget. Maps to runtime-routing.md:77-79.

### 5. No-recursion guard bullet

se-research (`SKILL.md:101-104`) and se-fact-check (`SKILL.md:108-111`) — verbatim identical:
> **No recursion when already dispatched.** This skill may itself be running as
> a dispatched sub-agent. When it is already running as a dispatched sub-agent,
> run the units inline in its own context rather than dispatching further — do
> not spawn another layer.

Rationale (design.md:72-78): both pilot skills carry the `forked` runtime profile (DEEP_ANALYSIS), so the skill may already be an isolated sub-agent; recursive spawning is prohibited. Prose guard only, no registry change. Maps to runtime-routing.md:79 ("prohibit recursive spawning").

### 6. Active task prefix bullet

se-research (`SKILL.md:105-109`) and se-fact-check (`SKILL.md:112-116`) — verbatim identical except the trailing noun ("its unit input" vs "its claim input"):
> **Active task prefix.** When a Trellis task is active, open each dispatch
> prompt with `Active task: <task path from task.py current>` before the
> role-specific instructions, so platforms that do not hook-inject context still
> receive it. When no Trellis task is active, omit the prefix and hand the worker
> its unit input directly.

## Recorded rationale & invariants (from archived design.md)

Source: `.trellis/tasks/archive/2026-08/07-25-dispatch-pilot/design.md`.

- **Doctrine anchor** (design.md:1-8): `runtime-routing.md` "Subagent decomposition" (lines 67-86); model section is `sd-audit-repo`'s `## Dispatch protocol`.
- **Scope invariant** (design.md:11-13): "Prose-only change … No new required section. No final-report contract change." Dispatch is non-required and interspersed.
- **Section-order invariant** (design.md:29-36): `REQUIRED_SECTIONS` validation checks only relative order of the five required headings and permits interspersed non-required sections (`generate-skill-surfaces.py:255-263`, now :270-277). No generator change needed; When→Arguments→Workflow→Safety→Final report order preserved.
- **Neutrality invariant** (design.md:46-48, 92): must not match `BANNED_PHRASE_PATTERN` (`Claude|Cowork|Codex|Copilot|Gemini|ChatGPT|OpenAI|Anthropic|Amp`).
- **Requirement mapping** (design.md:50-86):
  - R1 = strategy line (element 1 above).
  - R2/R3 = units = the **same units the Workflow already defines, not new work**; orchestrator ownership; worker input contract; no-recursion; active-task prefix.
  - R3 inline fallback (design.md:84-86): "the existing Workflow steps and `## Final report` contract are the inline path verbatim; dispatch is an execution strategy layered over them, never a scope or contract change."
  - R4 (design.md:110-111): host BUILT-IN sub-agents only; prose must not depend on named SE worker agents.
- **Drift/version invariants** (design.md:88-104): generated Claude overlays regenerated via `make generate`; `make check` `release-check` (`--check`) proves committed overlays match byte-for-byte; `manifest.json` version hand-edited (files array derived from registry paths, unchanged); dated `CHANGELOG.md` entry.

## Caveats

- The pilot references line numbers from the pre-runtime-profile-gaps generator (`:255-263`, `:900`, `:972`); in the current tree the ordering check is at `generate-skill-surfaces.py:270-277`. The behavior (order-only, interspersed allowed) is unchanged.
- se-research/se-fact-check `## Final report` sections were NOT modified by the pilot; the dispatch section explicitly references but never alters them.
