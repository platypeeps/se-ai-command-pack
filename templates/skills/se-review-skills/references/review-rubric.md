# Skill Review Rubric

Use this rubric only after deterministic inventory. Candidate size,
similarity, and repetition signals identify where to inspect; they never prove
a defect or overlap.

## Capability ledger

Record these before proposing deletion, compression, movement, or replacement:

| Capability | Preserve explicitly |
|---|---|
| Trigger | Positive trigger, negative trigger, and sibling boundary |
| Inputs | Required and optional inputs, defaults, ambiguity handling |
| Output | Artifact, schema, ordering, evidence, and handoff |
| Authority | Read/write boundary, approvals, side effects, external actions |
| Safety | Prompt-injection, privacy, security, destructive-action gates |
| Verification | Preconditions, checks, read-back, evidence standard |
| Failure | Missing, malformed, stale, inaccessible, partial, no-result states |
| Portability | Shared behavior plus verified target-specific semantics |
| Continuity | State, snapshot, idempotence, checkpoint, and resume behavior |

A brevity proposal is valid only when the post-change ledger retains every
accepted capability or explicitly replaces it with an equivalent tested
contract.

## Review dimensions

1. **Correctness and consistency** — contradictions, impossible sequences,
   missing prerequisites, stale facts, unsafe assumptions, or output fields
   unsupported by the workflow.
2. **Trigger and sibling boundary** — ambiguous descriptions, accidental
   automatic invocation, missing negative triggers, or overlapping ownership.
   Compare outcome, inputs, output, depth, time horizon, mutation, and handoff.
3. **Authority and safety** — implied permission, hidden side effects,
   insufficient preview, prompt injection, privacy leakage, destructive scope,
   or provider output treated as authority.
4. **Capability gaps** — missing failure states, validation, evidence,
   partial-state behavior, honest no-result path, or downstream handoff.
5. **Brevity and context cost** — duplicated explanation, narration, repeated
   examples, copied schemas, or detail loaded on every invocation despite
   being conditional. Preserve operative rules and move conditional detail to
   one directly linked reference.
6. **Progressive disclosure** — metadata should trigger; the core skill should
   orchestrate; references should hold conditional depth; deterministic scripts
   should own repeated fragile mechanics. Avoid deep reference chains.
7. **Deterministic helpers** — identify repeated parsing, normalization,
   transformation, validation, hashing, path resolution, inventory, schema
   checks, or stable command orchestration that a script can perform more
   reliably and with less context. Keep judgment in the skill and test scripts
   with real fixtures.
8. **Metadata and portability** — exact name, concise trigger description,
   supported top-level fields, host UI metadata, target syntax, path semantics,
   model names, tool grants, and fallback behavior.
9. **Context and delegation** — inline versus isolated work, independent
   validation, decomposable subagent roles, minimal context, bounded fan-out,
   authority inheritance, parent reconciliation, and cost versus benefit.
10. **Evaluation coverage** — convention tests, behavior pins, negative cases,
    clean/no-findings cases, cross-target parity, isolated forward tests, and
    tests that would fail if the capability disappeared.

## Brevity test

For every compression proposal include:

- current and estimated post-change lines or words;
- duplicated or movable content with exact locators;
- ledger entries affected and why they remain preserved;
- regression risk and the test or forward evaluation needed; and
- whether a pinned test intentionally preserves the current wording.

Do not set a universal line or token target. The objective is the shortest
version that preserves accepted behavior and safety, not the smallest file.

## Finding threshold

Create a finding only when evidence supports all of these:

- a specific issue or opportunity;
- an owning skill or package-wide contract;
- an allowed canonical remediation path;
- a capability-preserving proposed change; and
- a validation method that could disprove success.

Keep unsupported suspicions in coverage limits. Put generator, installer,
manifest, documentation, test, or consumer-copy symptoms outside a first-party
skill batch when no allowed template change can remedy them.

## Script extraction test

For each scripting opportunity record:

- the exact deterministic steps and current source locators;
- stable inputs, output schema, exit codes, and actionable error contract;
- filesystem, network, subprocess, or external-system side effects;
- required runtime, dependencies, target portability, and fallback;
- idempotence, preview or dry-run behavior, path and symlink safety;
- unit fixtures plus one end-to-end invocation; and
- semantic judgment, user dialogue, approval, evidence interpretation, and
  authority decisions that remain in the skill.

Do not script a short one-off instruction when the helper adds more dependency,
maintenance, portability, or security cost than reliability or context savings.
Never hide mutating authority inside a convenience script.

## Priority and effort

- `P0` — active severe safety, data-loss, or authority failure;
- `P1` — material correctness, routing, portability, or capability defect;
- `P2` — meaningful clarity, maintainability, cost, or coverage improvement;
- `P3` — low-risk polish with measurable value.

Use effort `S`, `M`, or `L` based on the smallest coherent implementation and
validation batch. Do not lower priority because a fix is large or raise it
because a fix is easy.
