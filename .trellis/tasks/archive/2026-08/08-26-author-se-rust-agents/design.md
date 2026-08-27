# Design: se- rust agent trio

## D1. Canonical form

Three flat files in `templates/agents/`, one per role, matching the existing
`se-claim-verifier.md` conventions: frontmatter from the agent allowlist
(`name`, `description`, `tools`, `model`, `sandbox_mode` — generator
`ALLOWED_AGENT_FRONTMATTER_KEYS`), body opening with the bounded-worker
contract ("You are a worker dispatched...") and the opening-context
paragraph pattern (`Active task: <path>` line awareness).

## D2. What survives from opencode-cfg, and how

| Upstream mechanism | Fate | Re-expression |
| --- | --- | --- |
| Deny-by-default permission JSON | dropped as data, kept as posture | `tools` hint lists only what each role needs; body states the refusal boundary in prose |
| Model pins via local gateway | dropped (parent R2) | omit `model` (inherit) |
| Skeleton/fill split | kept | `se-rust-write` emits compiling skeletons with `todo!()` bodies and never fills; `se-rust-fill` fills only named holes and never touches signatures/types/public API |
| Reviewer role | kept, narrowed | `se-rust-reviewer` read-only, findings `path:line`, one verdict line; verdict authority stays with the sd-review lane |
| Private hostnames / gateway config | never ships (parent C4) | AC2 grep |

## D3. Tool grants

- `se-rust-write`, `se-rust-fill`: Read, Edit, Write, Grep, Glob, Bash
  (build/test only — body forbids git mutation and edits outside the brief's
  named files).
- `se-rust-reviewer`: Read, Grep, Glob, Bash (read-only commands); body
  forbids edits entirely.

`sandbox_mode` set only if the existing agents use it — match whatever
`se-claim-verifier.md`/`se-source-reader.md` do (inspect at edit time; do not
invent a value the pipeline never renders).

## D4. Contracts (each file states all three)

- Stage contract: what the parent sends (brief with named files/holes) and
  what stage of the typed-holes workflow this agent owns.
- Refusal boundary: wrong-stage requests are refused with the reason
  (`se-rust-fill` asked to change a signature refuses and names
  `se-rust-write`; `se-rust-reviewer` asked to fix refuses and returns
  findings).
- Return contract: `se-rust-write` returns the skeleton diff + hole
  inventory; `se-rust-fill` returns filled-hole diff + build/test evidence;
  `se-rust-reviewer` returns findings table + one verdict line.

## D5. Relationship to `se-typed-holes`

The skill (sibling task) teaches the workflow and may name the trio as
optional executors; the agents reference the skill by name for the shared
discipline. Both directions use final `se-` names only.
