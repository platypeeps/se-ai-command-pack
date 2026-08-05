# Design — Sub-agent dispatch pilot (se-research, se-fact-check)

Parent settled inputs: `07-25-agent-artifacts/design.md` section 1 (inputs #5/#6,
ACCEPTED 2026-07-25) and `research/cross-platform-agent-support.md`. Doctrine:
`templates/skills/se-review-skills/references/runtime-routing.md`
("Subagent decomposition", lines 67-86). Model: `sd-audit-repo` `## Dispatch
protocol` section.

## Scope

Prose-only change to two canonical skill bodies plus generated Claude overlays,
version, and changelog. No generator, lint, registry, or installer code changes.
No new required section. No final-report contract change.

- `templates/skills/se-research/SKILL.md`
- `templates/skills/se-fact-check/SKILL.md`
- `generated/skills/claude/se-research/SKILL.md` (regenerated, byte-stable except
  the mirrored dispatch section)
- `generated/skills/claude/se-fact-check/SKILL.md` (same)
- `templates/skills/_shared/references/skill-catalog.md` (generator restamps its
  version line)
- `manifest.json` — **version header only**. No files are added or removed, so the
  generator's `files` array (derived from registry/payload paths,
  `generate-skill-surfaces.py:900,972`) is unchanged; only the hand-edited
  `version` field moves.
- `CHANGELOG.md` dated entry.

## Section contract

Insert one **non-required** section `## Sub-agent dispatch` between `## Workflow`
and `## Safety rules` in each body — mirroring `sd-audit-repo`, where the
dispatch protocol sits between the workflow body and the report/safety tail.
`REQUIRED_SECTIONS` validation checks only the relative order of the five
required headings and permits interspersed non-required sections
(`generate-skill-surfaces.py:255-263`), so no generator change is needed and the
When→Arguments→Workflow→Safety→Final report order is preserved.

Insertion points (canonical bodies):
- se-research: after current line 69 (end of `## Workflow`), before `## Safety
  rules` (71).
- se-fact-check: after current line 81 (end of `## Workflow`), before `## Safety
  rules` (83).

## Dispatch section content (both skills)

Capability-first, host-neutral. Must not match `BANNED_PHRASE_PATTERN`
(`Claude|Cowork|Codex|Copilot|Gemini|ChatGPT|OpenAI|Anthropic|Amp`). Shape modeled
on `sd-audit-repo`, adapted to each skill's own fan-out units:

- **Strategy line (R1):** "On sub-agent dispatch platforms, run the units below in
  parallel; on inline platforms, work through them sequentially in one context."
- **Units (R2/R3 — same units the Workflow already defines, not new work):**
  - se-research: parallelism is **within each workflow phase, not across
    phases** — the phases are data-dependent (sweep lanes -> verify claims from
    those results -> disconfirm the top-three conclusions). One worker per
    search lane runs concurrently in step 3; then one worker per claim
    verification concurrently in step 4; then one worker per disconfirmation
    query concurrently in step 5. Dispatch never reorders or overlaps steps
    3->4->5; it only fans out the independent units inside a single phase.
  - se-fact-check: one worker per atomic claim (Workflow steps 5-6). Claims are
    mutually independent, so all claim workers run concurrently in one phase.
- **Orchestrator ownership (R2, runtime-routing 78-81):** the parent context owns
  unit IDs, deduplication, conflict resolution, verification, and the single final
  report. Workers never write the final report and never assign IDs.
- **Worker input contract (R2, runtime-routing 78-81):** each worker receives the
  smallest complete input set for its unit, plus explicit exclusions, an authority
  boundary, an **expected artifact** (the exact result shape the worker returns —
  e.g. se-research: the logged sources/claims for its lane; se-fact-check: the
  single verdict record for its claim), and a **stop condition** (when the unit is
  done). Concurrency is capped to host/task budget; task creation/edits stay with
  the parent.
- **No recursion when already forked (runtime-routing 26, 77):** both skills are
  assigned the `forked` runtime profile (`installer/registry.py` DEEP_ANALYSIS at
  163/206; overlays declare `context: fork`), so on a sub-agent-dispatch platform
  the skill may itself be running as an isolated forked sub-agent. Recursive
  spawning is prohibited: the dispatch prose must instruct that when the skill is
  already executing as a sub-agent, it runs the units inline in its own context
  rather than dispatching further. This is a prose guard only; no registry change.
- **Active task prefix (input #6):** when a Trellis task is active, each dispatch
  prompt opens with `Active task: <task path from task.py current>` before role
  instructions, so platforms that do not hook-inject context still receive it. When
  no Trellis task is active (e.g. a user-scoped install), the prefix is omitted and
  the worker receives its unit input directly.
- **Inline fallback (R3):** the existing Workflow steps and `## Final report`
  contract are the inline path verbatim; dispatch is an execution strategy layered
  over them, never a scope or contract change.

## Compatibility / invariants

- `REQUIRED_SECTIONS` ordering stays valid (order-only check; new section is
  non-required and interspersed).
- `BANNED_PHRASE_PATTERN` passes — no host product names in canonical bodies.
- Generated Claude overlays regenerated via `make generate`; `make check`'s
  `release-check` drift gate (`generate-skill-surfaces.py --check`) proves the
  committed overlays match the regenerated ones byte-for-byte.
- Final-report sections/evidence rules unchanged in both skills.

## Version / rollout

- `manifest.json` `0.66.9 -> 0.66.10`; the generator rewrites only the files
  array, so the version is hand-edited.
- `CHANGELOG.md`: prepend `## 0.66.10 - 2026-08-05` describing the dispatch pilot.
- No rollback complexity: prose additions are removable in a single revert; no
  data or contract migration.

## Tradeoffs / residuals

- `dispatch-rollout` (07-25) intentionally deferred; this pilot validates the
  pattern on the two highest-value skills first (PRD "dispatch-rollout MUST wait").
- Worker agents (`07-25-worker-agents`) are out of scope: this uses host BUILT-IN
  sub-agents only (R4); prose must not depend on named SE worker agents.
- Body-churn sequencing risk (arg-vocab renames) is already retired — all five
  `08-04-arg-vocab-*` children are archived, so the canonical vocabulary is
  settled and dispatch prose is written in it directly.
