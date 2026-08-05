# Pattern-conformance note — dispatch rollout

Records what matched the `07-25-dispatch-pilot` pattern (`se-fact-check`,
`se-research`) and what diverged, per PRD AC item 3 and requirement R1
("divergences from the pilot pattern require a recorded reason").

## What matched (all five skills)

Every rolled-out skill carries a `## Sub-agent dispatch` section placed between
`## Workflow` and `## Safety rules`, replicating the pilot's six-element shape
verbatim in structure:

1. **Strategy / inline-fallback opening** — identical framing: parallel on
   dispatch platforms, sequential inline; "Dispatch is an execution strategy
   layered over the Workflow above — it never changes the scope, the
   `<skill discipline>`, or the `## Final report` contract."
2. **One-worker-per-unit** — each skill's natural fan-out unit (see table),
   with orchestrator-only pre/post steps named by their Workflow step numbers.
3. **Orchestrator-owns-synthesis** — the parent assigns stable IDs, dedups,
   reconciles conflicts, and writes the single final report; workers never do.
4. **Worker input contract** — smallest complete input, explicit exclusions,
   read-only authority boundary, an **expected artifact**, and a **stop
   condition**.
5. **No-recursion guard** — inline when already running as a dispatched
   sub-agent; no further layer.
6. **Active-task prefix** — `Active task: <task path from task.py current>`
   when a Trellis task is active.

Per-skill unit + invariant mapping:

| Skill           | Fan-out unit              | Discipline invariant            | Inserted after |
|-----------------|---------------------------|---------------------------------|----------------|
| se-digest       | per input document        | the synthesis discipline        | step 7         |
| se-feedback     | per supplied source       | the disposition discipline      | step 12        |
| se-scan         | per player/vendor profile | the same-criteria discipline    | step 6         |
| se-video-notes  | per video (`mode=compare`)| the coverage-fidelity bar       | step 15        |
| se-red-team     | per adversarial lane      | the classification discipline   | step 13        |

Final-report contracts are unchanged for all five (R3). Neutrality lint,
section-order validation, and generator `--check` pass (R1/AC1, AC2).

## Divergences (recorded reasons)

- **se-video-notes — fan-out scoped to `mode=compare`.** In `single` mode there
  is one video and thus one unit; dispatch would add orchestration overhead with
  no parallelism. The section states this explicitly and runs the single unit
  inline. Reason: the skill's own unit count is argument-dependent, unlike the
  always-multi pilots.

- **se-scan — same-criteria is an orchestrator-enforced global gate, not a
  per-worker quota.** The pilot's discipline invariants are per-unit; se-scan's
  is cross-unit (identical criteria axes across all players). Recorded so the
  section does not imply each worker independently chooses axes. Reason: the
  skill's core value is apples-to-apples comparison, which only the orchestrator
  can enforce.

- **se-red-team — independent-red-team isolation (R2).** Workers receive the
  artifact, the user-shaped request, and the evidence/assertion ledger, but
  **never** the parent's steelman, suspected defects, expected findings, or
  conclusions, per `se-review-skills/references/runtime-routing.md` ("For
  independent validation, pass raw skill artifacts and the user-shaped request,
  but never raw sessions … Do not pass … the primary reviewer's conclusion").
  The no-recursion guard is additionally adapted to the fresh-session profile:
  a worker in a fresh independent session completes its lane inline and does not
  re-dispatch. Reason: composing dispatch with the `fresh-session` runtime
  profile from `07-25-runtime-profile-gaps` — contaminating a lane worker with
  the parent's framing would defeat the independence the profile exists to
  provide.

## Out of scope (R4)

`se-socratic-review` is anti-parallel by design (sequential dialectic) and is
deliberately untouched. No other skill bodies were modified; the generated diff
is limited to the five target skills plus the regenerated shared catalog.
